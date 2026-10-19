#!/usr/bin/env python3
"""Evidence from manually-labeled original-client screenshots, not gameplay proof."""
import argparse,json
from pathlib import Path
from PIL import Image,ImageChops

def difference(a,b,rect):
    if rect is None:return None
    with Image.open(a) as im1,Image.open(b) as im2:
        x=max(0,int(rect["x"]));y=max(0,int(rect["y"]))
        right=min(im1.width,im2.width,int(rect["x"]+rect["width"]))
        bottom=min(im1.height,im2.height,int(rect["y"]+rect["height"]))
        if right-x<20 or bottom-y<20:return None
        area=(x,y,right,bottom)
        delta=ImageChops.difference(im1.convert("RGB").crop(area),
                                    im2.convert("RGB").crop(area))
        mask=delta.convert("L").point(lambda v:255 if v>=18 else 0)
        return round(mask.histogram()[255]/((right-x)*(bottom-y)),6)

def analyze(report,root):
    images={x["event_index"]:root/x["file"] for x in report.get("screenshots",[]) if "event_index" in x}
    rows=[];start=None
    for i,event in enumerate(report.get("events",[])):
        if event.get("type")=="begin_action":start=(i,event)
        elif event.get("type")=="end_action" and start:
            idx,begin=start;start=None
            a,b=images.get(idx),images.get(i)
            fraction=difference(a,b,begin.get("player_bounds")) if (
                a and b and a.is_file() and b.is_file()) else None
            lo=begin.get("wall_clock_ms");hi=event.get("wall_clock_ms")
            network=sorted({x["path"] for x in report.get("network_events",[])
                if isinstance(lo,int) and isinstance(hi,int)
                and lo<=x.get("wall_clock_ms",-1)<=hi})
            rows.append({
                "operator_label":begin.get("kind",""),
                "begin_image":a.name if a else "",
                "end_image":b.name if b else "",
                "changed_fraction":fraction,
                "visual_evidence":"insufficient" if fraction is None else
                    ("visual_change" if fraction>=0.005 else "no_significant_change"),
                "requests_during_interval":network,
                "game_action_confirmed":False,
                "sprite_id_confirmed":None
            })
    return rows

if __name__=="__main__":
    p=argparse.ArgumentParser()
    p.add_argument("--report",required=True)
    p.add_argument("--out",required=True)
    a=p.parse_args()
    inp=Path(a.report)
    result=analyze(json.loads(inp.read_text()),inp.parent)
    dest=Path(a.out);dest.mkdir(parents=True,exist_ok=True)
    body={"windows":result,"confirmed_actions":0,"confirmed_sprites":0,
          "warning":"Screen changes and user labels are not proof of Flash animation identity."}
    (dest/"action_evidence_5d8b.json").write_text(json.dumps(body,indent=2)+"\n")
    print("ACTION_EVIDENCE_5D8B",json.dumps({
        "windows":len(result),"visual_changes":sum(x["visual_evidence"]=="visual_change" for x in result),
        "confirmed_actions":0}))
