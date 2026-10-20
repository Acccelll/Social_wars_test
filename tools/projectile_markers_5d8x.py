#!/usr/bin/env python3
"""5D.8X inspect named Flash PlaceObject markers in authentic 0.02a unit SWFs.

Do not infer a projectile origin just from a colored pixel/alpha bounds.
The AS3 getProjectilePoint() calls bmd.getChildAt(0).getChildByName(name)
and localToGlobal()/parent.globalToLocal(). A matching instance name in a
nested sprite is not automatically proof it is the direct runtime child.
"""
import argparse,hashlib,json,zipfile
from pathlib import Path,PurePosixPath
from visual_timelines import inspect

UNITS={
 "bushwacker":("1358_bushwacker.swf","e9db23f98dcaa5cf81cbcdac85154fcb1da92a205b7d9047a5d420fb9d068c5e"),
 "reaperDrone":("1376_reaperDrone.swf","c26e398f5f2209eb9ba8fc3ef84ed243b1032240c3e2f543a879330e77b64b83")
}
NEEDLE=("projectilepoint","hitpoint","muzzle","firepoint","disparo","shootpoint")
def main():
 ap=argparse.ArgumentParser()
 ap.add_argument("--archive",required=True)
 ap.add_argument("--out",required=True)
 a=ap.parse_args()
 archive=Path(a.archive)
 if archive.stat().st_size!=492630085:raise ValueError("Original distribution ZIP length mismatch")
 output={"lot":"5D.8X","originalSwfModified":False,
   "source":"Release 0.02a asset SWFs; parsed PlaceObject instance names",
   "clientLookup":"DisplayObjectContainer(bmd.getChildAt(0)).getChildByName(clipName)",
   "fallback":"(x, y-bmd.height*0.6), or (x,y) if bmd null",
   "units":{}}
 with zipfile.ZipFile(archive) as z:
  for key,(filename,sha) in UNITS.items():
   candidates=[x for x in z.infolist() if PurePosixPath(x.filename).name==filename and
     "/assets/sprites/" in "/"+x.filename]
   if len(candidates)!=1:raise ValueError(f"Unable to locate exactly one {filename}")
   swf=z.read(candidates[0])
   if hashlib.sha256(swf).hexdigest()!=sha:raise ValueError("Asset SWF SHA mismatch "+key)
   metadata=inspect(swf,detailed=True)
   markers=[]
   named_all=[]
   for timeline in [metadata["root"]]+metadata["sprites"]:
    for event in timeline.get("frame_events",[]):
     name=event.get("instance_name")
     if not isinstance(name,str):continue
     record={
      "timelineSpriteId":timeline.get("character_id"),"timelineFrame":event.get("frame"),
      "name":name,"depth":event.get("depth"),
      "characterId":event.get("character_id",event.get("resolved_character_id")),
      "matrix":event.get("matrix")
     }
     named_all.append(record)
     if any(word in name.lower() for word in NEEDLE):markers.append(record)
   output["units"][key]={
    "asset":filename,"sha256":sha,"rootSpriteCount":len(metadata["sprites"]),
    "namedInstanceCount":len(named_all),
    "markerEvents":markers[:300],
    "markerEventTotal":len(markers),
    "uniqueRelevantNames":sorted({e["name"] for e in markers}),
    "someNamedInstances":named_all[:25],
    "caution":"Instance event names do not prove runtime bmd.getChildAt(0) hierarchy or parent transforms."
   }
 dest=Path(a.out);dest.parent.mkdir(parents=True,exist_ok=True)
 dest.write_text(json.dumps(output,indent=2,ensure_ascii=False)+"\n")
 print("PROJECTILE_MARKER_SCAN_5D8X",json.dumps({k:{"events":v["markerEventTotal"],
   "names":v["uniqueRelevantNames"],"allNamed":v["namedInstanceCount"]} for k,v in output["units"].items()}))
if __name__=="__main__":main()
