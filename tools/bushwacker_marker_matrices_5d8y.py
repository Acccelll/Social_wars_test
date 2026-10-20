#!/usr/bin/env python3
"""5D.8Y: compose static SWF PlaceObject matrices for Bushwacker projectilePoint.

Only prove what binary tags establish. This is NOT runtime AVM2/display-tree
inspection. Parent sprites may advance independently; paths with unknown frames
are reported as candidates, not guaranteed muzzle positions.
"""
from __future__ import annotations
import argparse,hashlib,json,math,zipfile
from pathlib import Path,PurePosixPath
from collections import defaultdict
from visual_timelines import inspect

ASSET="1358_bushwacker.swf"
SHA="e9db23f98dcaa5cf81cbcdac85154fcb1da92a205b7d9047a5d420fb9d068c5e"
ROOT_ID=1092
ATTACK_ROOT_FRAMES=range(11,16)
MARKER_PARENT_IDS=(643,675,716,752,786)
I=(1.,0.,0.,1.,0.,0.) # affine a,b,c,d,tx,ty; all translations twips
def matrix(v):
    v=v or {}
    return (float(v.get("scale_x",1)),float(v.get("skew_x",0)),
       float(v.get("skew_y",0)),float(v.get("scale_y",1)),
       float(v.get("tx_twips",0)),float(v.get("ty_twips",0)))
def mul(parent,child):
    a,b,c,d,tx,ty=parent
    e,f,g,h,u,v=child
    return (a*e+c*f,b*e+d*f,a*g+c*h,b*g+d*h,a*u+c*v+tx,b*u+d*v+ty)
def point(m,x=0,y=0):
    a,b,c,d,tx,ty=m
    return (a*x+c*y+tx,b*x+d*y+ty)
def mapped(m):
    x,y=point(m)
    return {"twips":[round(x,3),round(y,3)],
            "pixels":[round(x/20,3),round(y/20,3)]}
def timeline_state(rec,n):
    state={}
    for ev in rec.get("frame_events",[]):
        if ev["frame"]>n:break
        depth=ev.get("depth")
        if depth is None:continue
        if ev["op"]=="remove":state.pop(depth,None)
        elif ev["op"]=="place":
            previous=state.get(depth,{})
            if ev.get("character_id") is None and ev.get("resolved_character_id") is None:
                if not previous:continue
                cid=previous["character_id"]
            else:cid=ev.get("character_id",ev.get("resolved_character_id"))
            # PlaceObject move with omitted matrix retains old transform.
            state[depth]={"character_id":cid,
               "matrix":ev.get("matrix",previous.get("matrix",{})),
               "depth":depth,"instance_name":ev.get("instance_name",previous.get("instance_name")),
               "lastFrame":ev["frame"],"event":ev}
    return list(state.values())
def edges(sprites):
    byparent=defaultdict(list)
    for pid,sp in sprites.items():
        for ev in sp.get("frame_events",[]):
            if ev["op"]!="place":continue
            cid=ev.get("character_id",ev.get("resolved_character_id"))
            if cid in sprites:
                byparent[pid].append({"parent":pid,"child":cid,"frame":ev["frame"],
                    "depth":ev["depth"],"matrix":ev.get("matrix",{}),
                    "instance_name":ev.get("instance_name")})
    return byparent
def paths(graph,start,goal,limit=5,maxdepth=5):
    result=[]
    def walk(now,trail,visited):
        if now==goal:
            result.append(trail);return
        if len(trail)>=maxdepth:return
        # Collapse duplicate placement edges of same sprite/frame/depth.
        seen=set()
        for e in graph.get(now,[]):
            sig=(e["child"],e["frame"],e["depth"],json.dumps(e["matrix"],sort_keys=True))
            if sig in seen:continue
            seen.add(sig)
            if e["child"] in visited:continue
            walk(e["child"],trail+[e],visited|{e["child"]})
            if len(result)>=limit:return
    walk(start,[],{start})
    return result
def combine_edges(chain,marker):
    transform=I
    for e in chain:
        transform=mul(transform,matrix(e["matrix"]))
    transform=mul(transform,matrix(marker.get("matrix")))
    return transform
def main():
    p=argparse.ArgumentParser()
    p.add_argument("--archive",required=True)
    p.add_argument("--out",required=True)
    a=p.parse_args()
    if Path(a.archive).stat().st_size!=492630085:raise ValueError("Canonical release size mismatch")
    with zipfile.ZipFile(a.archive) as z:
        matches=[x for x in z.infolist()
          if PurePosixPath(x.filename).name==ASSET and "/assets/sprites/" in "/"+x.filename]
        if len(matches)!=1:raise ValueError("Bushwacker source ambiguous")
        raw=z.read(matches[0])
    if hashlib.sha256(raw).hexdigest()!=SHA:raise ValueError("Original Bushwacker SWF hash mismatch")
    data=inspect(raw,detailed=True)
    sprites={sp["character_id"]:sp for sp in data["sprites"]}
    if ROOT_ID not in sprites:raise ValueError("Root character missing")
    graph=edges(sprites)
    root=sprites[ROOT_ID]
    report={"lot":"5D.8Y","sourceSwf":ASSET,"sourceSha256":SHA,
      "sourceSwfUnmodified":True,"rootSprite":ROOT_ID,
      "fps":data["fps"],"rootLabels":root["frame_labels"],
      "matrixOrder":"Flash a,b,c,d,tx,ty; x'=a*x+c*y+tx, y'=b*x+d*y+ty",
      "twipsPerPixel":20,
      "sourceLimitations":[
       "Static parser: cannot establish AVM2 parent.getChildAt(0) hierarchy at attack time",
       "Nested sprites may advance independently of their root state",
       "Static marker position in sprite-local coordinates is not scene-local/world muzzle location",
       "Bitmap FFDec alpha crop and Canvas registration are not accounted for",
       "Transforms computed here must be independently checked before altering live projectile origin"],
      "attackStates":[],"markerPaths":[],"markerParents":[],"timelineDiagnostics":{}}
    for frame in ATTACK_ROOT_FRAMES:
        direct=timeline_state(root,frame)
        record={"rootFrame":frame,"directChildren":[
         {"id":c["character_id"],"depth":c["depth"],"matrix":c["matrix"]}
         for c in direct if c["character_id"] in sprites],
         "targetMarkers":{}}
        report["attackStates"].append(record)
    for parentid in MARKER_PARENT_IDS:
        sp=sprites.get(parentid)
        if not sp:raise ValueError(f"Missing attack direction sprite {parentid}")
        markers=[ev for ev in sp["frame_events"]
          if ev.get("instance_name")=="projectilePoint" and ev["op"]=="place"]
        rec={"parentId":parentid,"framesDeclared":sp["declared_frames"],
          "markers":markers[:10],"chains":[]}
        chains=paths(graph,ROOT_ID,parentid,limit=16,maxdepth=5)
        for chain in chains:
            if not chain:continue
            for ev in markers:
                composed=combine_edges(chain,ev)
                rec["chains"].append({
                  "path":[{"parent":e["parent"],"child":e["child"],
                    "frame":e["frame"],"depth":e["depth"],
                    "matrix":e["matrix"]} for e in chain],
                  "markerFrame":ev["frame"],"markerDepth":ev["depth"],
                  "markerLocalTwips":mapped(matrix(ev["matrix"])),
                  "markerInRootSprite":mapped(composed),
                  "composedMatrix":list(composed),
                  "framePathRuntimeConfirmed":False})
        report["markerParents"].append(rec)
    for record in report["attackStates"]:
        roots={x["id"] for x in record["directChildren"]}
        record["targetMarkers"]={
            str(v["parentId"]):{
                "directChild":v["parentId"] in roots,
                "pathsFound":len(v["chains"]),
                "bestMinimalDepth":min((len(x["path"]) for x in v["chains"]),default=None)}
            for v in report["markerParents"]}
    report["timelineDiagnostics"]={
      "spritesParsed":len(sprites),"warnings":sum(x.get("parse_warnings",0) for x in sprites.values()),
      "markerParentIds":list(MARKER_PARENT_IDS),
      "pathCounts":{str(x["parentId"]):len(x["chains"]) for x in report["markerParents"]}}
    dest=Path(a.out);dest.parent.mkdir(parents=True,exist_ok=True)
    dest.write_text(json.dumps(report,ensure_ascii=False,indent=2)+"\n")
    print("BUSH_MARKER_MATRIX_CHAINS_5D8Y",json.dumps({
      "rootAttackDirectIds":{str(r["rootFrame"]):[
       c["id"] for c in r["directChildren"]] for r in report["attackStates"]},
      "pathCounts":report["timelineDiagnostics"]["pathCounts"],
      "firstComposed":{str(r["parentId"]):[
       c["markerInRootSprite"]["pixels"] for c in r["chains"][:2]]
       for r in report["markerParents"]},
      "warnings":report["timelineDiagnostics"]["warnings"]},ensure_ascii=False),flush=True)
if __name__=="__main__":main()
