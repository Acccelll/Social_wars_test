#!/usr/bin/env python3
"""5D.8E: call original Flask command.php and verify a seeded unit truly moves.

Safe scope: loopback-only HTTP, isolated saves folder, and one newly-created
ephemeral village. Do not use against public servers or personal save files.
Does NOT claim that Ruffle visually played the move animation.
"""
import argparse
import hashlib
import http.cookiejar
import json
from pathlib import Path
from urllib.parse import urlencode, urlparse
from urllib.request import build_opener, HTTPCookieProcessor, Request

DYNAMIC="/dynamic/menvswomen/srvsexwars/command.php"

def choose_destination(item, occupied):
    x,y=item[1:3]
    for nx,ny in ((x+1,y+1),(x-1,y+1),(x+2,y),(x,y+2),(x-2,y)):
        if 0<=nx<100 and 0<=ny<100 and (nx,ny) not in occupied:
            return [nx,ny]
    raise ValueError("No free destination near selected unit")

def build_command(index, destination):
    command={"first_number":0,"publishActions":[],"ts":0,"tries":0,
             "accessToken":"","commands":[[
                 0,"move",[index,destination[0],destination[1],0,""],[0]*8
             ]]}
    # Original server.py checks only length and the delimiter of this hash;
    # this is a local protocol fixture, not real server authentication.
    raw="0"*64+";"+json.dumps(command,separators=(",",":"))
    return urlencode({
        "USERID":"{USERID}","user_key":"test-only","language":"en","data":raw
    })

def run(host,save_dir,fixture):
    parsed=urlparse(host)
    if parsed.scheme!="http" or parsed.hostname not in ("127.0.0.1","localhost"):
        raise ValueError("Original server command probe limited to HTTP loopback")
    if parsed.port is None:raise ValueError("Server port required")
    saves=Path(save_dir).resolve()
    if not saves.is_dir():raise ValueError("Missing disposable saves directory")
    manifest=json.loads(Path(fixture).read_text(encoding="utf-8"))
    selected=manifest["seeded_units"][0]
    index=str(selected["index"])
    before_files={p.name for p in saves.glob("*.save.json")}
    if before_files:
        raise ValueError("Refusing probe because the test saves folder is not empty")
    opener=build_opener(HTTPCookieProcessor(http.cookiejar.CookieJar()))
    # This server route creates exactly one new village and redirects to play.
    with opener.open(host+"/new.html",timeout=25) as response:
        if response.status!=200:raise ValueError("New village HTTP "+str(response.status))
    fresh=sorted([p for p in saves.glob("*.save.json") if p.name not in before_files])
    if len(fresh)!=1:raise ValueError("Expected exactly 1 isolated save; got "+str(len(fresh)))
    current=fresh[0]
    userid=current.name.removesuffix(".save.json")
    before_bytes=current.read_bytes()
    before=json.loads(before_bytes)
    items=before["maps"][0]["items"]
    if index not in items:raise ValueError("Seeded unit absent from new player map")
    unit=items[index]
    if unit[0]!=selected["item_id"] or unit[1:3]!=selected["map_tile"]:
        raise ValueError("Saved unit differs from fixture")
    if unit[7]!=1:raise ValueError("Unexpected unit owner")
    occupied={(item[1],item[2]) for key,item in items.items() if key!=index}
    target=choose_destination(unit,occupied)
    form=build_command(int(index),target).replace("%7BUSERID%7D",userid)
    req=Request(host+DYNAMIC,data=form.encode("ascii"),
                headers={"Content-Type":"application/x-www-form-urlencoded"},
                method="POST")
    with opener.open(req,timeout=25) as response:
        content=response.read()
        if response.status!=200 or json.loads(content).get("result")!="success":
            raise ValueError("Command endpoint rejected")
    after_bytes=current.read_bytes()
    after=json.loads(after_bytes)
    after_unit=after["maps"][0]["items"][index]
    if after_unit[1:3]!=target:raise ValueError("Move command did not persist new coordinates")
    if after_unit[0]!=unit[0] or after_unit[7]!=unit[7]:
        raise ValueError("Move unexpectedly changed unit identity or owner")
    if after_unit[3:]!=unit[3:]:
        raise ValueError("Move unexpectedly mutated non-position item fields")
    changes={
        key:(value,after["maps"][0]["items"].get(key))
        for key,value in items.items()
        if value!=after["maps"][0]["items"].get(key)
    }
    if set(changes)!={index}:raise ValueError("Extra map items changed: "+repr(list(changes)))
    if len(list(saves.glob("*.save.json")))!=1:
        raise ValueError("Unexpected saves added during command")
    return {
        "protocol":"original_flask_command.php POST",
        "result":"move_persisted",
        "source":"official AcidCaos socialwarriors server.py/command.py",
        "original_item_index":int(index),
        "original_unit_item_id":unit[0],
        "coordinates_before":unit[1:3],
        "coordinates_after":after_unit[1:3],
        "changed_map_object_count":len(changes),
        "map_object_count":len(items),
        "before_sha256":hashlib.sha256(before_bytes).hexdigest(),
        "after_sha256":hashlib.sha256(after_bytes).hexdigest(),
        "saved_file":True,
        "original_client_animation_observed":False,
        "sprite_character_id_confirmed":None,
        "tutorial_dialog_resolved":False,
        "warning":"Server-side persisted move is not evidence of in-client movement animation."
    }

def main():
    p=argparse.ArgumentParser()
    p.add_argument("--host",default="http://127.0.0.1:5055")
    p.add_argument("--saves",required=True)
    p.add_argument("--fixture",required=True)
    p.add_argument("--out",required=True)
    opts=p.parse_args()
    data=run(opts.host,opts.saves,opts.fixture)
    out=Path(opts.out)
    out.parent.mkdir(parents=True,exist_ok=True)
    out.write_text(json.dumps(data,ensure_ascii=False,indent=2)+"\n",encoding="utf-8")
    print("ORIGINAL_SERVER_MOVE_5D8E",json.dumps({k:data[k] for k in [
        "result","original_item_index","original_unit_item_id",
        "coordinates_before","coordinates_after","changed_map_object_count",
        "original_client_animation_observed"]}),flush=True)

if __name__=="__main__":main()
