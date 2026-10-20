#!/usr/bin/env python3
"""5D.8Z: Export five actual Bushwacker ATTACK root frames and measure alpha
bounds without inventing a sprite-root registration point.

Source SWF SHA checked. FFDec output origin is NOT necessarily (0,0)
of DefineSprite1092. The PNG sheet and alpha boxes are observations;
projectilePoint remains in root-local twips and needs a calibrated transform.
"""
import argparse,hashlib,json,re,subprocess,tempfile,zipfile
from pathlib import Path,PurePosixPath
from PIL import Image,ImageDraw
from visual_timelines import inspect
SWF="1358_bushwacker.swf"
SHA="e9db23f98dcaa5cf81cbcdac85154fcb1da92a205b7d9047a5d420fb9d068c5e"
ROOT=1092
FRAMES=range(11,16)
def command(jar,swf,frames,dest):
 return ["java","-Xmx2g","-Djava.awt.headless=true","-jar",str(jar),
         "-cli","-selectid",str(ROOT),"-select",f"{ROOT}:{frames}",
         "-sublength","1","-format","sprite:png",
         "-export","sprite",str(dest),str(swf)]
def run(args,timeout=180):
 p=subprocess.run(args,capture_output=True,text=True,errors="replace",timeout=timeout)
 if p.returncode:raise RuntimeError(f"FFDec failed ({p.returncode}): {(p.stdout+p.stderr)[-1900:]}")
 return (p.stdout+"\n"+p.stderr)[-5000:]
def collect(out):
 found={}
 for p in out.rglob("*.png"):
  if str(ROOT) not in str(p):continue
  match=re.search(r"[/\\]([0-9]{1,2})\.png$",str(p))
  if match and int(match.group(1)) in FRAMES:
   found[int(match.group(1))]=p
 return found
def main():
 a=argparse.ArgumentParser()
 for k in ("archive","ffdec","out"):a.add_argument("--"+k,required=True)
 v=a.parse_args()
 out=Path(v.out).resolve();out.mkdir(parents=True,exist_ok=True)
 if Path(v.archive).stat().st_size!=492630085:raise ValueError("Original archive size mismatch")
 with tempfile.TemporaryDirectory(prefix="bush-root-5d8z-") as tmp,zipfile.ZipFile(v.archive) as z:
  paths=[m for m in z.infolist() if PurePosixPath(m.filename).name==SWF and "/assets/sprites/" in "/"+m.filename]
  if len(paths)!=1:raise ValueError("Asset missing or ambiguous")
  raw=z.read(paths[0])
  if hashlib.sha256(raw).hexdigest()!=SHA:raise ValueError("Original Bush SWF SHA mismatch")
  parsed=inspect(raw,detailed=True)
  root=next(s for s in parsed["sprites"] if s["character_id"]==ROOT)
  assert root["declared_frames"]>=15 and root["parse_warnings"]==0
  swf=Path(tmp)/SWF;swf.write_bytes(raw)
  scratch=Path(tmp)/"all";scratch.mkdir()
  log=run(command(v.ffdec,swf,"11-15",scratch))
  outputs=collect(scratch)
  if len(outputs)!=5:
   outputs={}
   for frame in FRAMES:
    d=Path(tmp)/f"frame_{frame}";d.mkdir()
    log+="\n"+run(command(v.ffdec,swf,str(frame),d),timeout=110)
    candidates=list(d.rglob("*.png"))
    if len(candidates)!=1:raise ValueError(f"Ambiguous frame {frame} PNGs: {len(candidates)}")
    outputs[frame]=candidates[0]
  (out/"ffdec-export.log").write_text(log)
  frames=[Image.open(outputs[n]).convert("RGBA") for n in FRAMES]
  cw=max(im.width for im in frames);ch=max(im.height for im in frames)
  # No cropping or independent recentering; raw origin is (0,0) of FFDec PNG.
  # Wider/smaller FFDec canvas is zero-padded at top-left and noted below.
  sheet=Image.new("RGBA",(cw*5,ch))
  records=[]
  for i,(frame,im) in enumerate(zip(FRAMES,frames)):
   box=im.getbbox()
   if box is None:raise ValueError(f"Unexpected transparent ATTACK frame {frame}")
   sheet.paste(im,(i*cw,0))
   records.append({
     "rootFrame":frame,"pose":i+1,"pngCanvas":[im.width,im.height],
     "alphaBounds":[*box],
     "visibleWidth":box[2]-box[0],"visibleHeight":box[3]-box[1],
     "sourceSha256":hashlib.sha256(outputs[frame].read_bytes()).hexdigest(),
     "actualPixelHash":hashlib.sha256(im.tobytes()).hexdigest()})
  sheet_path=out/"bush_attack_root_11_15.png";sheet.save(sheet_path,optimize=True)
  distinct=len(set(r["actualPixelHash"] for r in records))
  if distinct!=5:raise ValueError(f"Five attack root directions not visually distinct: {distinct}")
  manifest={
   "lot":"5D.8Z","sourceSWF":SWF,"sourceSha256":SHA,
   "originalSWFModified":False,"rootSpriteId":ROOT,
   "sourceFrames":[11,12,13,14,15],"renderMethod":"FFDec sprite:png selecting actual root frames; sublength=1",
   "pngAtlas":"bush_attack_root_11_15.png","atlasSha256":hashlib.sha256(sheet_path.read_bytes()).hexdigest(),
   "columns":5,"frameWidth":cw,"frameHeight":ch,
   "frames":records,"distinctImages":distinct,
   "registration":{"known":False,
    "why":"FFDec exported-image (0,0) is not proven identical to Flash DefineSprite root pivot; separate FFDec PNG canvas sizes can also vary.",
    "rootToImageOffsetPx":None,
    "doNotAssumeImageCenterOrAlphaBoundsAsOrigin":True},
   "sourceMuzzlesRootLocal":[[116.15,-371.7],[254.55,-299.2],
                             [186.55,-182.5],[89.7,-78.25],[-93.9,-109.7]],
   "nextCalibration":"Measure same root origin in an untrimmed FFDec export or Flash runtime; then map original local markers via that offset and verified world scale."
  }
  (out/"registration_5d8z.json").write_text(json.dumps(manifest,ensure_ascii=False,indent=2)+"\n")
  print("BUSH_ROOT_REGISTRATION_5D8Z",json.dumps({
    "size":[cw,ch],"poseBounds":[r["alphaBounds"] for r in records],
    "frameSizes":[r["pngCanvas"] for r in records],
    "distinct":distinct,"rootRegistrationKnown":False}),flush=True)
if __name__=="__main__":main()
