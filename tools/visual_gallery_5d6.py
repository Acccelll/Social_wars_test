#!/usr/bin/env python3
"""5D.6: Category-filtered small GIF gallery, based on actual SWF IDs.

Includes original 8 previews and expands into 9 additional source SWFs.
GIFs stay outside Git; CSV/JSON metadata may be committed.
"""
import argparse,csv,hashlib,html,json,re,shutil,subprocess,tempfile,zipfile
from pathlib import Path,PurePosixPath
from urllib.parse import quote
from visual_timelines import inspect
from visual_preview_catalog import make_preview

GROUPS={
 "units":["1358_bushwacker.swf","1376_reaperDrone.swf","1037_megatank.swf"],
 "buildings":["0039_tower_2_m.swf","0040_workshop_1_m.swf","0118_laboratory_m.swf"],
 "interface":["popupResearchCenter_buildingProcess.swf",
              "popupResearchCenter_buildingProcess_2.swf","crossDCi.swf"]
}
def baseline_group(n):
    if n.startswith(("1212_","1313_","good_10_")):return "units"
    if n.startswith(("0022_","0026_")):return "buildings"
    raise ValueError("Unexpected 5D.5 SWF "+n)

def pick(doc):
    sprites=[s for s in doc["sprites"] if s.get("child_character_ids")
             and s.get("place_events",0)>0]
    if not sprites:return None
    animated=[s for s in sprites if 2<=s["declared_frames"]<=45]
    pool=animated or sprites
    return sorted(pool,key=lambda s:(-min(24,s["declared_frames"]),
                                     -min(100,s["place_events"]),s["character_id"]))[0]

def plan(z,entries,base):
    rows=[]
    for x in base["items"]:
        rows.append(dict(category=baseline_group(x["swf"]),source=x["source"],
           swf=x["swf"],id=int(x["id"]),name=x.get("name",""),
           frames_declared=x["frames_declared"],children=x.get("children",[]),
           kind="baseline"))
    for category,names in GROUPS.items():
        for name in names:
            if name not in entries:raise ValueError("Missing original SWF "+name)
            d=inspect(z.read(entries[name]),False)
            source=entries[name].filename.removeprefix("social-warriors_0.02a/")
            s=pick(d)
            rows.append(dict(category=category,source=source,swf=name,
              id=s["character_id"] if s else None,name=s.get("symbol_name","") if s else "",
              frames_declared=s["declared_frames"] if s else 0,
              children=s["child_character_ids"] if s else [],
              kind="new" if s else "no_sprite",
              **({"error":"No usable sprite definition"} if not s else {})))
    keys=[(x["swf"],x["id"]) for x in rows if x["id"] is not None]
    if len(keys)!=len(set(keys)):raise ValueError("Duplicated SWF/character ID")
    return rows

def gallery(rows,dest):
    cards=[]
    for x in rows:
        label=html.escape(x["swf"][:-4])
        pic=('<img loading="lazy" src="'+quote(x["preview"],safe="/.")+
             '" alt="Sprite '+str(x["id"])+'">' if x.get("preview") else
             '<div class="empty">Sem prévia</div>')
        query=html.escape((x["swf"]+" "+x.get("name","")+" "+str(x["id"])).lower(),quote=True)
        title=label+" · #"+str(x["id"])
        details=(str(x["frames_declared"])+" quadros no SWF · "+
                 str(x.get("gif_frames",0))+" na prévia · filhos: "+
                 ", ".join(map(str,x["children"][:12])))
        cards.append('<article data-cat="'+x["category"]+'" data-search="'+query+
            '">'+pic+'<section><h2>'+title+'</h2><p>'+html.escape(details)+
            '</p><small>'+html.escape(x.get("error",""))+'</small></section></article>')
    webpage='''<!doctype html><html lang="pt-BR"><head><meta charset="utf-8">
<meta name="viewport" content="width=device-width,initial-scale=1">
<title>Social Wars | Biblioteca visual</title><style>
:root{color-scheme:dark}body{margin:0;font:14px system-ui;background:#101722;color:#edf4fc}
header{padding:25px 4vw;border-bottom:1px solid #344759}
header p{color:#bac9d9;max-width:840px}nav{display:flex;gap:9px;flex-wrap:wrap}
button,input{padding:10px;border:1px solid #74839b;background:#26384a;color:inherit;border-radius:7px}
button{cursor:pointer}button[aria-pressed=true]{background:#4c627c}
main{display:grid;grid-template-columns:repeat(auto-fit,minmax(260px,1fr));gap:16px;padding:25px 4vw}
article{border-radius:10px;overflow:hidden;background:#1d2a3a;border:1px solid #344759}
article[hidden]{display:none}img,.empty{width:100%;height:220px;display:block;object-fit:contain;background:#28364a}
.empty{display:grid;place-items:center}section{padding:14px}
h2{font-size:16px;overflow-wrap:anywhere}small{color:#e8b8b8}
#count{margin-top:12px;color:#b7c5d6}
</style></head><body><header><h1>Social Wars — Biblioteca visual 5D.6</h1>
<p>GIFs exportados de timelines do Flash. Categorias baseadas nos nomes dos SWFs, ainda não revisadas visualmente. Animações controladas por ActionScript podem diferir das prévias.</p>
<nav><button data-f="all" aria-pressed="true">Todos</button>
<button data-f="units" aria-pressed="false">Unidades</button>
<button data-f="buildings" aria-pressed="false">Construções</button>
<button data-f="interface" aria-pressed="false">Interface / telas</button>
<input id="q" aria-label="Buscar nome e ID" placeholder="Buscar nome ou ID"></nav>
<div id="count" aria-live="polite"></div></header><main>'''+''.join(cards)+'''</main>
<script>(()=>{let filter="all";const a=[...document.querySelectorAll("article")],
q=document.getElementById("q");function draw(){let count=0;
for(const e of a){e.hidden=!((filter==="all"||e.dataset.cat===filter)&&
e.dataset.search.includes(q.value.toLowerCase().trim()));if(!e.hidden)count++}
document.getElementById("count").textContent=count+" recurso(s)";}
for(const b of document.querySelectorAll("[data-f]"))b.addEventListener("click",()=>{
filter=b.dataset.f;for(const c of document.querySelectorAll("[data-f]"))
c.setAttribute("aria-pressed",String(c===b));draw()});
q.addEventListener("input",draw);draw()})();</script></body></html>'''
    (dest/"index.html").write_text(webpage,encoding="utf-8")

def publish(rows,out):
    totals={
     "sources":len(set(x["swf"] for x in rows)),
     "selected":len(rows),"rendered":sum("preview" in x for x in rows),
     "animated":sum(x.get("gif_frames",0)>1 for x in rows),
     "categories":{cat:dict(selected=sum(x["category"]==cat for x in rows),
                              rendered=sum(x["category"]==cat and "preview" in x for x in rows))
                   for cat in GROUPS},
     "items":rows,"errors":[x for x in rows if x.get("error")],
     "limitation":"Static FFDec representation; AS3 runtime behavior not confirmed."}
    (out/"catalog.json").write_text(json.dumps(totals,indent=2,ensure_ascii=False),encoding="utf-8")
    fields=["category","source","swf","id","name","frames_declared",
            "gif_frames","preview","size_bytes","sha256","kind","error"]
    with (out/"catalog.csv").open("w",newline="",encoding="utf-8") as f:
        w=csv.DictWriter(f,fieldnames=fields);w.writeheader()
        for r in rows:w.writerow({k:r.get(k,"") for k in fields})
    gallery(rows,out)
    print("GALLERY_5D6_SUMMARY",json.dumps({k:totals[k] for k in
          ("sources","selected","rendered","animated","categories")}),flush=True)
    print("GALLERY_5D6_ERRORS",len(totals["errors"]),flush=True)
    return totals

def main():
    p=argparse.ArgumentParser()
    p.add_argument("--archive",required=True)
    p.add_argument("--ffdec",default="")
    p.add_argument("--baseline",default="data/visual/preview_catalog.json")
    p.add_argument("--out",default="dist/gallery-5d6")
    p.add_argument("--plan-only",action="store_true")
    p.add_argument("--strict",action="store_true")
    a=p.parse_args()
    out=Path(a.out).resolve();out.mkdir(parents=True,exist_ok=True)
    base=json.loads(Path(a.baseline).read_text(encoding="utf-8"))
    with zipfile.ZipFile(a.archive) as z:
        entries={}
        for x in z.infolist():
            if x.filename.lower().endswith(".swf") and not x.is_dir():
                n=PurePosixPath(x.filename).name
                if n in entries:raise ValueError("Duplicate SWF: "+n)
                entries[n]=x
        rows=plan(z,entries,base)
        (out/"plan.json").write_text(json.dumps(rows,indent=2),encoding="utf-8")
        print("GALLERY_5D6_PLAN",len(rows),flush=True)
        if a.plan_only:
            if a.strict and (len(rows)!=17 or
               not all(any(x["category"]==cat and x["id"] is not None for x in rows)
                       for cat in GROUPS)):
                raise SystemExit("Category plan incomplete")
            return
        jar=Path(a.ffdec)
        if not jar.exists():raise ValueError("Missing ffdec.jar")
        with tempfile.TemporaryDirectory() as tmp:
            temp=Path(tmp)
            for name in dict.fromkeys(x["swf"] for x in rows if x["id"] is not None):
                batch=[x for x in rows if x["swf"]==name and x["id"] is not None]
                swf=temp/name;dst=temp/(name[:-4]+"_ffdec");dst.mkdir()
                with z.open(entries[name]) as inp,swf.open("wb") as f:
                    shutil.copyfileobj(inp,f)
                ids=",".join(str(x["id"]) for x in batch)
                cmd=["java","-Xmx2g","-Djava.awt.headless=true","-jar",str(jar),
                     "-cli","-selectid",ids,"-format","sprite:gif",
                     "-export","sprite",str(dst),str(swf)]
                result=subprocess.run(cmd,stdout=subprocess.PIPE,stderr=subprocess.STDOUT,
                                      text=True,errors="replace",timeout=240)
                (out/(name[:-4]+".log")).write_text(result.stdout[-1400:],encoding="utf-8")
                gifs=list(dst.rglob("*.gif"))
                print("GALLERY_5D6_FFDEC",name,"exit",result.returncode,"gifs",len(gifs),flush=True)
                for row in batch:
                    pattern=re.compile(r"(?<![0-9])"+str(row["id"])+r"(?![0-9])")
                    matches=[g for g in gifs if pattern.search(g.relative_to(dst).as_posix())]
                    if not matches:
                        row["error"]="No matching frames.gif for sprite ID"
                        continue
                    gif=sorted(matches,key=lambda x:len(str(x)))[0]
                    preview=out/"previews"/row["category"]/name[:-4]/(str(row["id"])+".gif")
                    try:
                        original,n=make_preview(gif,preview,256,20)
                        row.update(preview=preview.relative_to(out).as_posix(),
                                   gif_frames=n,original_frames=original,
                                   size_bytes=preview.stat().st_size,
                                   sha256=hashlib.sha256(preview.read_bytes()).hexdigest())
                    except Exception as exc:row["error"]=str(exc)
                if result.returncode:
                    for row in batch:row.setdefault("error",f"FFDec exit {result.returncode}")
    totals=publish(rows,out)
    if a.strict and (totals["rendered"]<14 or
      not all(totals["categories"][cat]["rendered"]>=1 for cat in GROUPS)):
        raise SystemExit("Preview coverage below requirements")

if __name__=="__main__":main()
