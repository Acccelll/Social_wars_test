#!/usr/bin/env python3
"""5D.7 evidence-only states and duplicate GIF auditing for Social Wars."""
import argparse,csv,hashlib,html,json,re,shutil,zipfile
from collections import defaultdict
from pathlib import Path,PurePosixPath
from urllib.parse import quote
from visual_timelines import inspect

STATES={
 "idle":("idle","stand","wait","rest"),
 "movement":("walk","run","move","march","fly","travel"),
 "attack":("attack","shoot","fire","strike","blast","punch","slash"),
 "damage":("hurt","damage","damaged","injured","stun"),
 "destruction":("die","dead","death","destroy","destroyed","explode","explosion","wreck"),
 "construction":("build","building","construct","construction","upgrade","repair","production")
}

def classify_text(text):
    value=re.sub(r"([a-z])([A-Z])",r"\1 \2",str(text))
    words=set(re.findall(r"[a-z]+",value.lower()))
    return [name for name,terms in STATES.items() if words.intersection(terms)]

def classify_evidence(node,children):
    observations=[]
    def add(kind,text):
        if text and str(text).strip():
            observations.append({"kind":kind,"text":str(text)})
    add("symbol_name",node.get("symbol_name"))
    for label in node.get("frame_labels",[]):add("frame_label",label["name"])
    for op in node.get("frame_events",[]):
        add("instance_name",op.get("instance_name"))
        add("class_name",op.get("class_name"))
    for child in children:
        add("child_symbol_name",child.get("symbol_name"))
        for label in child.get("frame_labels",[]):add("child_frame_label",label["name"])
    evidence={}
    seen=set()
    for item in observations:
        marker=(item["kind"],item["text"])
        if marker in seen:continue
        seen.add(marker)
        for state in classify_text(item["text"]):
            evidence.setdefault(state,[]).append(item)
    return {k:v[:12] for k,v in evidence.items()}

def scan_sources(archive,names):
    with zipfile.ZipFile(archive) as z:
        lookup={}
        for info in z.infolist():
            if not info.is_dir() and info.filename.endswith(".swf"):
                name=PurePosixPath(info.filename).name
                if name in lookup:raise ValueError("Ambiguous SWF filename: "+name)
                lookup[name]=info
        missing=set(names)-set(lookup)
        if missing:raise ValueError("Source SWFs missing: "+repr(missing))
        return {name:inspect(z.read(lookup[name]),True) for name in names}

def hash_perceptual(frame):
    from PIL import Image
    # Black matte matters for transparent gifs, but candidates only.
    im=frame.convert("RGBA").resize((9,8),Image.Resampling.LANCZOS)
    matte=Image.new("RGBA",im.size,(255,255,255,255))
    matte.alpha_composite(im)
    luminance=list(matte.convert("L").getdata())
    bits=0
    for y in range(8):
        for x in range(8):
            bits=(bits<<1)|int(luminance[y*9+x]>luminance[y*9+x+1])
    return f"{bits:016x}"

def fingerprint(gif):
    from PIL import Image
    with Image.open(gif) as image:
        count=getattr(image,"n_frames",1)
        frames=[]
        pixel_sha=[]
        for n in sorted({0,count//2,count-1}):
            image.seek(n)
            rgba=image.convert("RGBA")
            frames.append(hash_perceptual(rgba))
            thumb=rgba.copy()
            thumb.thumbnail((96,96),Image.Resampling.LANCZOS)
            canvas=Image.new("RGBA",(96,96),(0,0,0,0))
            canvas.alpha_composite(thumb,((96-thumb.width)//2,(96-thumb.height)//2))
            pixel_sha.append(hashlib.sha256(canvas.tobytes()).hexdigest())
        return {"decoded_frames":count,"perceptual_hashes":frames,
                "pixel_fingerprint":hashlib.sha256("|".join(pixel_sha).encode()).hexdigest()}

def duplicates(rows,threshold=8):
    sha=defaultdict(list);pixels=defaultdict(list);near=[]
    for item in rows:
        sha[item["sha256"]].append(item["key"])
        pixels[item["pixel_fingerprint"]].append(item["key"])
    exact=[v for v in sha.values() if len(v)>1]
    same_pixels=[v for v in pixels.values()
                 if len(v)>1 and len({next(x["sha256"] for x in rows if x["key"]==key)
                                      for key in v})>1]
    for i,a in enumerate(rows):
        for b in rows[i+1:]:
            if a["sha256"]==b["sha256"] or a["pixel_fingerprint"]==b["pixel_fingerprint"]:
                continue
            if a["decoded_frames"]!=b["decoded_frames"]:continue
            distance=sum((int(x,16)^int(y,16)).bit_count()
                         for x,y in zip(a["perceptual_hashes"],b["perceptual_hashes"]))
            if distance<=threshold:
                near.append({"a":a["key"],"b":b["key"],"distance":distance,
                             "status":"candidate_for_human_review"})
    return {"exact_sha256":exact,"same_decoded_pixels":same_pixels,
            "near_candidates":sorted(near,key=lambda r:(r["distance"],r["a"],r["b"]))}

def render_html(rows,dest,dups):
    cards=[]
    exact_keys={k for group in dups["exact_sha256"] for k in group}
    for r in rows:
        states=" ".join(r["candidate_states"]) if r["candidate_states"] else "unclassified"
        title=html.escape(r["swf"]+" #"+str(r["id"]))
        label=html.escape(", ".join(r["candidate_states"]) or "Não identificado")
        badge=" / duplicata exata" if r["key"] in exact_keys else ""
        img=quote(r["preview"],safe="/.")
        cards.append('<article data-cat="'+html.escape(r["category"],quote=True)+
                     '" data-state="'+html.escape(states,quote=True)+'">'+
                     '<img src="'+img+'" loading="lazy" alt="GIF do sprite">'+
                     '<div class="desc"><h2>'+title+'</h2><p>Hipótese: '+label+
                     html.escape(badge)+'</p><p>'+str(r["gif_frames"])+
                     ' quadros GIF</p></div></article>')
    page='''<!doctype html><html lang="pt-BR"><head><meta charset="utf-8">
<meta name="viewport" content="width=device-width,initial-scale=1">
<title>Social Wars — Revisão 5D.7</title>
<style>:root{color-scheme:dark}body{margin:0;background:#121a28;color:#eaf2fd;font:14px system-ui}
header{padding:28px 5vw;border-bottom:1px solid #40546b}header p{max-width:870px;line-height:1.5;color:#bfd0e1}
nav{display:flex;gap:8px;flex-wrap:wrap}select{padding:10px;background:#253a4d;color:inherit;border:1px solid #64819c;border-radius:8px}
main{padding:24px 5vw;display:grid;grid-template-columns:repeat(auto-fill,minmax(250px,1fr));gap:16px}
article{border-radius:10px;border:1px solid #3f5268;overflow:hidden;background:#1d2c3e}
article[hidden]{display:none}img{width:100%;height:225px;object-fit:contain;display:block;background:#293d4f}
.desc{padding:14px}h2{font-size:15px;overflow-wrap:anywhere}
</style></head><body><header><h1>Social Wars — Auditoria visual 5D.7</h1>
<p>Estados são hipóteses apoiadas apenas em rótulos ou símbolos do SWF.
Nenhuma ação foi validada no cliente original. Similaridade visual requer inspeção humana.</p>
<nav><select id="cat"><option value="all">Todas as categorias</option>
<option value="units">Unidades</option><option value="buildings">Construções</option>
<option value="interface">Interface</option></select><select id="state">
<option value="all">Todos os estados</option><option value="unclassified">Não identificado</option>
<option value="idle">Espera</option><option value="movement">Movimento</option>
<option value="attack">Ataque</option><option value="damage">Dano</option>
<option value="destruction">Destruição</option><option value="construction">Construção</option>
</select></nav><p id="count"></p></header><main>'''+''.join(cards)+'''</main>
<script>(()=>{const a=[...document.querySelectorAll("article")],
c=document.getElementById("cat"),s=document.getElementById("state");
function update(){let n=0;for(const e of a){e.hidden=!(
(c.value==="all"||e.dataset.cat===c.value)&&
(s.value==="all"||e.dataset.state.split(" ").includes(s.value)));
if(!e.hidden)n++}document.getElementById("count").textContent=n+" prévia(s)";}
c.addEventListener("change",update);s.addEventListener("change",update);update()})();</script></body></html>'''
    (dest/"review.html").write_text(page,encoding="utf-8")

def process(gallery_root,archive,out):
    data=json.loads((gallery_root/"catalog.json").read_text(encoding="utf-8"))
    originals=scan_sources(archive,sorted({r["swf"] for r in data["items"]}))
    results=[]
    for item in data["items"]:
        if "preview" not in item:raise ValueError("No preview "+item["swf"])
        swf=item["swf"];sprite_id=item["id"]
        node=next((s for s in originals[swf]["sprites"] if
                   s["character_id"]==sprite_id),None)
        if node is None:raise ValueError("Sprite ID missing "+swf+"/"+str(sprite_id))
        ids=set(node.get("child_character_ids",[]))
        children=[s for s in originals[swf]["sprites"] if s["character_id"] in ids]
        evidence=classify_evidence(node,children)
        gif=gallery_root/item["preview"]
        sha=hashlib.sha256(gif.read_bytes()).hexdigest()
        if sha!=item["sha256"]:raise ValueError("GIF integrity mismatch "+str(gif))
        record={
            "key":swf+"#"+str(sprite_id),"source":item["source"],
            "swf":swf,"id":sprite_id,"category":item["category"],
            "preview":item["preview"],"sha256":sha,
            "frames_declared":item["frames_declared"],
            "gif_frames":item["gif_frames"],
            "candidate_states":list(evidence),"evidence":evidence,
            "confidence":"metadata_hint" if evidence else "unclassified",
            "review_status":"original_runtime_confirmation_pending",
        }
        record.update(fingerprint(gif))
        results.append(record)
    dups=duplicates(results)
    stats={
        "sources":len(originals),"previews":len(results),
        "metadata_hints":sum(bool(r["candidate_states"]) for r in results),
        "unclassified":sum(not r["candidate_states"] for r in results),
        "state_counts":{s:sum(s in r["candidate_states"] for r in results) for s in STATES},
        "exact_duplicate_groups":len(dups["exact_sha256"]),
        "pixel_equivalent_groups":len(dups["same_decoded_pixels"]),
        "near_candidate_pairs":len(dups["near_candidates"]),
        "runtime_confirmed":0
    }
    out.mkdir(parents=True,exist_ok=True)
    body={"status":"metadata_only_not_runtime_validated","stats":stats,
          "duplicates":dups,"entries":results}
    (out/"review.json").write_text(json.dumps(body,indent=2,ensure_ascii=False),encoding="utf-8")
    columns=["key","category","source","swf","id","frames_declared","gif_frames",
             "candidate_states","confidence","review_status","sha256"]
    with (out/"review.csv").open("w",encoding="utf-8",newline="") as f:
        writer=csv.DictWriter(f,fieldnames=columns)
        writer.writeheader()
        for r in results:
            writer.writerow({k:json.dumps(r[k]) if isinstance(r.get(k),list) else r.get(k,"")
                             for k in columns})
    shutil.copytree(gallery_root/"previews",out/"previews",dirs_exist_ok=True)
    render_html(results,out,dups)
    print("REVIEW_5D7_STATS",json.dumps(stats),flush=True)
    print("REVIEW_5D7_EXACT",json.dumps(dups["exact_sha256"]),flush=True)
    print("REVIEW_5D7_NEAR",json.dumps(dups["near_candidates"][:20]),flush=True)
    print("REVIEW_5D7_STATES",json.dumps([{r["key"]:r["candidate_states"]} for r in results]),flush=True)
    return stats,dups

if __name__=="__main__":
    p=argparse.ArgumentParser()
    p.add_argument("--gallery",required=True)
    p.add_argument("--archive",required=True)
    p.add_argument("--out",default="dist/visual-review-5d7")
    a=p.parse_args()
    process(Path(a.gallery),Path(a.archive),Path(a.out))
