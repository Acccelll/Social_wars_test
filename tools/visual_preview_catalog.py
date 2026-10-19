#!/usr/bin/env python3
"""Small FFDec GIF gallery keyed by original SWF + DefineSprite character ID."""
import argparse
import csv
import gzip
import hashlib
import html
import json
import re
import shutil
import subprocess
import tempfile
import zipfile
from pathlib import Path, PurePosixPath
from urllib.parse import quote

SOURCES=["1212_tetrapod_mech.swf","1313_splinterMech.swf",
         "0022_tower_1_m.swf","0026_command_center_1_m.swf","good_10_m.swf"]

def planning(folder, per_source):
    rows=[]
    for name in SOURCES:
        with gzip.open(folder/(name[:-4]+".timeline.json.gz"),"rt",encoding="utf-8") as f:
            doc=json.load(f)
        options=[x for x in doc["sprites"] if 2<=x["declared_frames"]<=40
                 and x.get("place_events",0)>0 and x.get("child_character_ids")]
        options.sort(key=lambda x:(-min(x["declared_frames"],20),
                                   -min(x["place_events"],100),x["character_id"]))
        for x in options[:per_source]:
            rows.append({"source":doc["source"],"swf":name,"id":x["character_id"],
                         "frames_declared":x["declared_frames"],
                         "name":x.get("symbol_name",""),
                         "children":x["child_character_ids"],
                         "placements":x["place_events"]})
    return rows

def make_preview(src, dst, width, max_frames):
    from PIL import Image, ImageSequence
    with Image.open(src) as im:
        original=im.n_frames
        frames=[]
        delays=[]
        for item in ImageSequence.Iterator(im):
            if len(frames)>=max_frames:break
            frame=item.convert("RGBA")
            frame.thumbnail((width,width),Image.Resampling.LANCZOS)
            frames.append(frame)
            delays.append(max(40,int(item.info.get("duration",100))))
        if not frames:raise ValueError("Empty GIF")
        dst.parent.mkdir(parents=True,exist_ok=True)
        frames[0].save(dst,format="GIF",save_all=True,append_images=frames[1:],
                       loop=0,duration=delays,optimize=True,disposal=2)
        return original,len(frames)

def render_gallery(rows, root):
    cards=[]
    for r in rows:
        src=quote(r.get("preview",""),safe="/.")
        view=('<img loading="lazy" src="'+src+'" alt="Sprite animation">' if src
              else '<div class="missing">Sem prévia</div>')
        title=html.escape(r["swf"][:-4])
        extra=html.escape(r.get("error",""))
        cards.append('<article>'+view+'<div class="body"><h2>'+title+
                     '</h2><p>Sprite ID #'+str(r["id"])+' · '+str(r["frames_declared"])+
                     ' quadros declarados · '+str(r.get("rendered_frames",0))+
                     ' na prévia</p><small>Filhos: '+
                     html.escape(",".join(map(str,r["children"][:24])))+
                     '</small><p class="error">'+extra+'</p></div></article>')
    page='''<!doctype html><html lang="pt-BR"><head><meta charset="utf-8">
<meta name="viewport" content="width=device-width,initial-scale=1">
<title>Social Wars — galeria de sprites</title>
<style>body{margin:0;font:14px system-ui,sans-serif;background:#141923;color:#eaf0f8}
header{padding:30px 5vw;border-bottom:1px solid #3a4557}header p{color:#b9c4d5;max-width:850px}
main{padding:24px 5vw;display:grid;grid-template-columns:repeat(auto-fit,minmax(270px,1fr));gap:18px}
article{background:#1d2938;border:1px solid #34485d;border-radius:12px;overflow:hidden}
img,.missing{width:100%;height:230px;object-fit:contain;display:block;background:#29374a}
.missing{display:grid;place-items:center}.body{padding:16px}h2{font-size:17px;margin:0}
p{line-height:1.45}small{color:#b4c0cf}.error{color:#e9aaaa}</style></head><body>
<header><h1>Social Wars · Catálogo de prévias animadas</h1>
<p>Sprites extraídos por SWF e character ID. As prévias são uma representação dos quadros Flash e não garantem equivalência de animações dinâmicas controladas pelo ActionScript.</p></header>
<main>'''+("\n".join(cards))+'</main></body></html>'
    (root/"index.html").write_text(page,encoding="utf-8")

def main():
    parser=argparse.ArgumentParser()
    parser.add_argument("--archive",default="")
    parser.add_argument("--ffdec",default="")
    parser.add_argument("--out",default="dist/visual-previews")
    parser.add_argument("--details",default="data/visual/timeline_details")
    parser.add_argument("--per-source",type=int,default=2)
    parser.add_argument("--plan-only",action="store_true")
    parser.add_argument("--strict",action="store_true")
    args=parser.parse_args()
    root=Path(args.out).resolve()
    root.mkdir(parents=True,exist_ok=True)
    rows=planning(Path(args.details).resolve(),args.per_source)
    (root/"preview_plan.json").write_text(json.dumps(rows,indent=2),encoding="utf-8")
    print("PREVIEW_SELECTED",len(rows),flush=True)
    if args.plan_only:return
    from PIL import Image
    jar=Path(args.ffdec).resolve()
    if not jar.exists():raise ValueError("ffdec.jar missing")
    with zipfile.ZipFile(args.archive) as z:
        files={PurePosixPath(i.filename).name:i for i in z.infolist()
               if i.filename.endswith(".swf")}
        with tempfile.TemporaryDirectory() as tmp:
            for name in SOURCES:
                if name not in files:raise ValueError("SWF not found: "+name)
                src=Path(tmp)/name
                with z.open(files[name]) as stream,src.open("wb") as f:
                    shutil.copyfileobj(stream,f)
                selection=[r for r in rows if r["swf"]==name]
                if not selection:continue
                ids=",".join(str(r["id"]) for r in selection)
                output=Path(tmp)/(name[:-4]+"_export")
                output.mkdir()
                cmd=["java","-Xmx2g","-Djava.awt.headless=true",
                     "-jar",str(jar),"-cli","-selectid",ids,
                     "-format","sprite:gif","-export","sprite",str(output),str(src)]
                run=subprocess.run(cmd,stdout=subprocess.PIPE,stderr=subprocess.STDOUT,
                                   text=True,errors="replace",timeout=240)
                print("PREVIEW_FFDEC",name,ids,"exit",run.returncode,flush=True)
                (root/(name[:-4]+".ffdec.log")).write_text(run.stdout[-3000:],
                                                           encoding="utf-8")
                gifs=list(output.rglob("*.gif"))
                print("PREVIEW_GIFS",name,len(gifs),
                      [str(g.relative_to(output)) for g in gifs[:15]],flush=True)
                for row in selection:
                    cid=str(row["id"])
                    # FFDec sprite:gif stores frames.gif under a directory
                    # identifying the sprite, rather than naming it ID.gif.
                    candidates=[p for p in gifs if re.search(
                        r"(?<![0-9])"+re.escape(cid)+r"(?![0-9])",
                        p.relative_to(output).as_posix())]
                    if not candidates:
                        row["error"]="GIF inexistente para o sprite ID "+cid
                        continue
                    original=sorted(candidates,key=lambda p:len(p.name))[0]
                    preview=root/"previews"/name[:-4]/(cid+".gif")
                    try:
                        n,m=make_preview(original,preview,256,20)
                        row.update(preview=preview.relative_to(root).as_posix(),
                                   gif_original_frames=n,rendered_frames=m,
                                   gif_bytes=preview.stat().st_size,
                                   sha256=hashlib.sha256(preview.read_bytes()).hexdigest())
                        print("PREVIEW_RENDERED",name,cid,m,flush=True)
                    except Exception as exc:
                        row["error"]=str(exc)
    success=sum(bool(r.get("preview")) for r in rows)
    animated=sum(r.get("rendered_frames",0)>1 for r in rows)
    metadata={"selected":len(rows),"rendered":success,"animated":animated,
              "errors":[r for r in rows if r.get("error")],"items":rows}
    (root/"preview_catalog.json").write_text(json.dumps(metadata,indent=2,
                                                     ensure_ascii=False),encoding="utf-8")
    with (root/"preview_catalog.csv").open("w",newline="",encoding="utf-8") as f:
        fields=["swf","source","id","frames_declared","placements","name",
                "preview","gif_original_frames","rendered_frames","gif_bytes","sha256","error"]
        w=csv.DictWriter(f,fieldnames=fields)
        w.writeheader()
        for row in rows:w.writerow({field:row.get(field,"") for field in fields})
    render_gallery(rows,root)
    print("PREVIEW_SUMMARY",json.dumps({"selected":len(rows),"rendered":success,
                                       "animated":animated}),flush=True)
    if args.strict and (success!=len(rows) or animated==0):
        raise SystemExit("GIF coverage incomplete")
if __name__=="__main__":
    main()
