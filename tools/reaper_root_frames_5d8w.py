#!/usr/bin/env python3
"""5D.8W: export REAL root frames (1..25) of Reaper Drone DefineSprite1654.

Unlike 5D.8K, do not hold one root frame and sample subframes. The 25
root frames are grouped by SWF FrameLabel: QUIETO/ANDAR/ATAQUE/MUERTE/PICAR.
Never edit SWF. Publish derived PNGs as CI artifacts, never source commit.
"""
import argparse, hashlib, io, json, re, subprocess, tempfile, zipfile, shutil
from pathlib import Path,PurePosixPath
from PIL import Image,ImageChops
import sys
sys.path.insert(0,str(Path(__file__).parent))
from visual_timelines import inspect

FILENAME="1376_reaperDrone.swf"
SHA="c26e398f5f2209eb9ba8fc3ef84ed243b1032240c3e2f543a879330e77b64b83"
STATES={"quieto":range(1,6),"andar":range(6,11),"ataque":range(11,16),
        "muerte":range(16,21),"picar":range(21,26)}
ID=1654

def run(cmd,timeout=130):
 r=subprocess.run(cmd,stdout=subprocess.PIPE,stderr=subprocess.STDOUT,text=True,
                  errors="replace",timeout=timeout)
 if r.returncode:raise RuntimeError("FFDec failed: "+r.stdout[-1800:])
 return r.stdout[-3000:]

def transparent_crop(img):
 img=img.convert("RGBA")
 bounds=img.getbbox()
 if bounds is None:return (0,0,0,0)
 return bounds

def atlas(states,out,root_metadata):
 allframes=[img for seq in states.values() for img in seq]
 sizes=[im.size for im in allframes]
 # Registered origin: preserve image canvas registration across all 25 frames;
 # no per-frame crop/recenter (causes jitter).
 maxw,maxh=max(w for w,h in sizes),max(h for w,h in sizes)
 # FFDec root GIF frame selection may have differing canvas sizes. Pad at 0,0
 # without inventing per-frame origin; flag ambiguity in metadata.
 cellw,cellh=min(maxw,720),min(maxh,720)
 import PIL.Image
 descriptors={}
 for state,images in states.items():
  canvas=Image.new("RGBA",(cellw*5,cellh))
  hashes=[]
  boxes=[]
  for j,im in enumerate(images):
   im=im.convert("RGBA")
   hashes.append(hashlib.sha256(im.tobytes()).hexdigest())
   boxes.append(transparent_crop(im))
   if im.width>cellw or im.height>cellh:
    ratio=min(cellw/im.width,cellh/im.height)
    im=im.resize((round(im.width*ratio),round(im.height*ratio)),Image.Resampling.LANCZOS)
   canvas.paste(im,(j*cellw,0))
  file=out/"units"/"reaper_drone"/(state+".png")
  file.parent.mkdir(parents=True,exist_ok=True)
  canvas.save(file,optimize=True)
  descriptors[state]={"url":"/original-visual/units/reaper_drone/"+state+".png",
    "frames":len(images),"columns":5,"frameWidth":cellw,"frameHeight":cellh,
    "distinctRenderedFrames":len(set(hashes)),"transparentRootFrames":sum(b==(0,0,0,0) for b in boxes),"fps":30,
    "sourceRootFrames":list(STATES[state]),"alphaBounds":[list(b) for b in boxes],
    "sourceSha256":SHA,"atlasSha256":hashlib.sha256(file.read_bytes()).hexdigest()}
 return descriptors

def main():
 p=argparse.ArgumentParser()
 for name in ("archive","ffdec","out"):p.add_argument("--"+name,required=True)
 a=p.parse_args()
 out=Path(a.out).resolve();out.mkdir(parents=True,exist_ok=True)
 if Path(a.archive).stat().st_size!=492630085:raise ValueError("Non canonical release size")
 with zipfile.ZipFile(a.archive) as z,tempfile.TemporaryDirectory(prefix="reaper-25-root-") as td:
  entries=[i for i in z.infolist() if PurePosixPath(i.filename).name==FILENAME
           and "/assets/sprites/" in "/"+i.filename]
  if len(entries)!=1:raise ValueError("SWF path is ambiguous/missing")
  raw=z.read(entries[0])
  if hashlib.sha256(raw).hexdigest()!=SHA:raise ValueError("SWF SHA mismatch")
  timeline=inspect(raw,detailed=True)
  root=next(s for s in timeline["sprites"] if s["character_id"]==ID)
  assert root["declared_frames"]==25 and root["show_frames"]==25
  assert root["parse_warnings"]==0
  labels={x["name"].lower():x["frame"] for x in root["frame_labels"]}
  assert labels=={s:min(seq) for s,seq in STATES.items()}
  swf=Path(td)/FILENAME;swf.write_bytes(raw)
  jar=str(Path(a.ffdec).resolve())
  scratch=Path(td)/"probe"
  scratch.mkdir()
  def command(framesel,dest):
   return ["java","-Xmx2g","-Djava.awt.headless=true","-jar",jar,"-cli",
           "-selectid",str(ID),"-select",f"{ID}:{framesel}","-sublength","1",
           "-format","sprite:png","-export","sprite",str(dest),str(swf)]
  log=run(command("1-25",scratch),timeout=160)
  (out/"ffdec-export.log").write_text(log)
  # FFDec may organize output as 1654/frame-number.png or single frame PNG
  # in different versions: accept only 25 uniquely numbered frame images.
  files=list(scratch.rglob("*.png"))
  numbered={}
  for file in files:
   if f"{ID}" not in file.as_posix():continue
   number_match=re.search(r"(?:^|[/])([0-9]{1,2})\.png$",file.as_posix())
   if number_match:
    frame=int(number_match.group(1))
    if 1<=frame<=25:numbered[frame]=file
  if len(numbered)!=25:
   # Explicit root frame per FFDec invocation. 25 separate exports only
   # if format=png did not provide correctly numbered 25 root frames.
   numbered={}
   for frame in range(1,26):
    dest=Path(td)/f"single_{frame:02d}"
    dest.mkdir()
    run(command(str(frame),dest),timeout=75)
    pics=list(dest.rglob("*.png"))
    if len(pics)!=1:
     raise ValueError(f"Root frame {frame}: FFDec created {len(pics)} PNGs")
    numbered[frame]=pics[0]
  frames={}
  for state,seq in STATES.items():
   frames[state]=[Image.open(numbered[n]).convert("RGBA") for n in seq]
  entries=atlas(frames,out,root)
  analysis={"lot":"5D.8W","sourceSWF":FILENAME,"sourceSha256":SHA,
     "originalSWFModified":False,
     "rootSpriteId":ID,"rootFrameCount":root["declared_frames"],
     "stateLabels":labels,
     "renderSource":"Individual root frames 1..25; FFDec sprite:png; sublength 1",
     "rootTransformTwips":timeline["root"]["frame_events"][0]["matrix"],
     "states":entries,
     "keyframeEventsByState":{
       state:{
        "rootFrames":list(seq),
        "place":sum(x["op"]=="place" for x in root["frame_events"] if x["frame"] in seq),
        "remove":sum(x["op"]=="remove" for x in root["frame_events"] if x["frame"] in seq)
       } for state,seq in STATES.items()
     },
     "registrationCaveat":"FFDec output canvas bounds may differ across frames; atlas padding anchors top-left, not a proven gameplay pivot. Do not infer muzzle coordinate from bitmap bounds.",
     "animationCaveat":"Root QUIETO/ANDAR/ATAQUE frames may be directional poses (not a temporal sequence). MUERTE/PICAR have unchanged frames; do not manufacture time motion. AVM2/controller still not recovered."}
  (out/"reaper_root25_manifest.json").write_text(json.dumps(analysis,indent=2,ensure_ascii=False)+"\n")
  print("REAPER_ROOT25_5D8W",json.dumps({"frames":25,"states":{k:v["distinctRenderedFrames"] for k,v in entries.items()},
     "rootTransformTwips":analysis["rootTransformTwips"]}),flush=True)
if __name__=="__main__":main()
