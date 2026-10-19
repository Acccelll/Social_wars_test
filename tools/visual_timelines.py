#!/usr/bin/env python3
"""Read-only metadata extraction of FWS/CWS sprite timelines from original ZIP."""
import argparse
import csv
import gzip
import json
import struct
import zipfile
import zlib
from collections import Counter
from pathlib import Path, PurePosixPath

MAX_SWF=150_000_000
PLACES={4,26,70,94}
REMOVES={5,28}

def u16(data, pos):
    if pos+2>len(data): raise ValueError("truncated UI16")
    return struct.unpack_from("<H",data,pos)[0]

def cstr(data, pos):
    end=data.find(b"\0",pos)
    if end<0: raise ValueError("unterminated name")
    return data[pos:end].decode("utf-8",errors="replace"),end+1

class Bits:
    def __init__(self,raw,pos=0):
        self.raw,self.bit=raw,pos*8
    def read(self,n):
        if n<0 or n>32 or self.bit+n>len(self.raw)*8:
            raise ValueError("bitstream truncated")
        v=0
        for _ in range(n):
            v=v*2+((self.raw[self.bit//8]>>(7-self.bit%8))&1)
            self.bit+=1
        return v
    def signed(self,n):
        if n==0:return 0
        v=self.read(n)
        return v-(1<<n) if v&(1<<(n-1)) else v
    def align(self):
        self.bit=(self.bit+7)//8*8
    @property
    def pos(self):return self.bit//8

def matrix(raw,pos):
    b=Bits(raw,pos)
    result={}
    if b.read(1):
        n=b.read(5)
        result["scale_x"]=round(b.signed(n)/65536,6)
        result["scale_y"]=round(b.signed(n)/65536,6)
    if b.read(1):
        n=b.read(5)
        result["skew_x"]=round(b.signed(n)/65536,6)
        result["skew_y"]=round(b.signed(n)/65536,6)
    n=b.read(5)
    result["tx_twips"]=b.signed(n)
    result["ty_twips"]=b.signed(n)
    b.align()
    return result,b.pos

def skip_cxform(raw,pos):
    b=Bits(raw,pos)
    add,mult,n=b.read(1),b.read(1),b.read(4)
    for enabled in (mult,add):
        if enabled:
            for _ in range(4):b.signed(n)
    b.align()
    return b.pos

def place(tag,raw):
    e={"op":"place","tag":tag}
    if tag==4:
        e["character_id"]=u16(raw,0)
        e["depth"]=u16(raw,2)
        e["move"]=False
        if len(raw)>4:e["matrix"],_=matrix(raw,4)
        return e
    if len(raw)<(4 if tag in (70,94) else 3):
        raise ValueError("short PlaceObject tag")
    flags=raw[0]
    pos=1
    flags2=0
    if tag in (70,94):
        flags2=raw[1]
        pos+=1
    e["flags"]=flags
    e["flags2"]=flags2
    e["move"]=bool(flags&1)
    e["depth"]=u16(raw,pos)
    pos+=2
    if flags2&8 or ((flags2&16) and (flags&2)):
        e["class_name"],pos=cstr(raw,pos)
    if flags&2:
        e["character_id"]=u16(raw,pos)
        pos+=2
    if flags&4:
        e["matrix"],pos=matrix(raw,pos)
    if flags&8:pos=skip_cxform(raw,pos)
    if flags&16:
        e["ratio"]=u16(raw,pos)
        pos+=2
    if flags&32:
        e["instance_name"],pos=cstr(raw,pos)
    if flags&64:
        e["clip_depth"]=u16(raw,pos)
    return e

def tag_iter(blob,start=0):
    pos=start
    while pos+2<=len(blob):
        h=u16(blob,pos)
        pos+=2
        code,length=h>>6,h&63
        if length==63:
            if pos+4>len(blob):raise ValueError("truncated extended tag")
            length=struct.unpack_from("<I",blob,pos)[0]
            pos+=4
        if pos+length>len(blob):raise ValueError("tag outside stream")
        raw=blob[pos:pos+length]
        pos+=length
        yield code,raw
        if code==0:break

def encode_tag(code,raw):
    return (struct.pack("<H",(code<<6)|len(raw))+raw if len(raw)<63
            else struct.pack("<HI",(code<<6)|63,len(raw))+raw)

def symbols(raw):
    names={}
    if len(raw)<2:return names
    count=u16(raw,0)
    pos=2
    for _ in range(count):
        if pos+2>len(raw):break
        cid=u16(raw,pos)
        pos+=2
        try:name,pos=cstr(raw,pos)
        except ValueError:break
        if name:names[str(cid)]=name
    return names

def timeline(raw, cid, nframes, detailed=False):
    frame=1
    shows=0
    counter=Counter()
    active={}
    deps=set()
    events=[]
    labels=[]
    warnings=[]
    for code,payload in tag_iter(raw):
        if code==0:break
        if code==1:
            shows+=1
            frame+=1
        elif code in PLACES:
            counter["placements"]+=1
            try:
                e=place(code,payload)
                if "character_id" in e:
                    active[e["depth"]]=e["character_id"]
                    deps.add(e["character_id"])
                elif e["depth"] in active:
                    e["resolved_character_id"]=active[e["depth"]]
                if detailed:events.append({"frame":frame,**e})
            except (ValueError,IndexError) as exc:
                counter["parse_warnings"]+=1
                if detailed:
                    # Lossless fallback: never discard a placement because
                    # some optional PlaceObject3 fields are unrecognized.
                    events.append({"frame":frame,"op":"place_raw",
                                   "tag":code,"payload_bytes":len(payload),
                                   "raw_hex":payload.hex(),
                                   "parse_error":str(exc)})
                if len(warnings)<5:
                    warnings.append(f"tag {code}, frame {frame}: {exc}")
        elif code in REMOVES:
            counter["removals"]+=1
            if len(payload)>=(4 if code==5 else 2):
                depth=u16(payload,2 if code==5 else 0)
                active.pop(depth,None)
                if detailed:
                    events.append({"frame":frame,"op":"remove","tag":code,"depth":depth})
            else:counter["parse_warnings"]+=1
        elif code==43:
            try:
                label,_=cstr(payload,0)
                labels.append({"frame":frame,"name":label})
            except ValueError:counter["parse_warnings"]+=1
        elif code in (12,59,82):counter["script_tags"]+=1
        elif code in (15,89):counter["sound_controls"]+=1
    result={
        "character_id":cid,"declared_frames":nframes,
        "show_frames":shows,
        "place_events":counter["placements"],
        "remove_events":counter["removals"],
        "parse_warnings":counter["parse_warnings"],
        "script_tags":counter["script_tags"],
        "sound_controls":counter["sound_controls"],
        "child_character_ids":sorted(deps),
        "frame_labels":labels if detailed else len(labels)
    }
    if warnings:result["warnings"]=warnings
    if detailed:
        result["frame_events"]=events
        result["frame_indexing"]="1-based; only frames with display list changes are listed"
    return result

def inspect(swf,detailed=False):
    if len(swf)<12:raise ValueError("short SWF")
    magic=swf[:3]
    declared=struct.unpack_from("<I",swf,4)[0]
    if declared>MAX_SWF:raise ValueError("SWF decompressed size limit exceeded")
    if magic==b"FWS":body=swf[8:]
    elif magic==b"CWS":body=zlib.decompress(swf[8:])
    else:raise ValueError("unsupported SWF compression: "+repr(magic))
    if len(body)+8!=declared:raise ValueError("decompressed SWF size mismatch")
    nbits=body[0]>>3
    rectsize=(5+4*nbits+7)//8
    start=rectsize+4
    if start>len(body):raise ValueError("truncated SWF frame header")
    fps=struct.unpack_from("<H",body,rectsize)[0]/256
    nframes=u16(body,rectsize+2)
    sprite_raw=[]
    names={}
    root_raw=bytearray()
    for code,raw in tag_iter(body,start):
        if code==39:
            if len(raw)<4:raise ValueError("malformed DefineSprite")
            sprite_raw.append((u16(raw,0),u16(raw,2),raw[4:]))
        elif code in (56,76):
            names.update(symbols(raw))
        elif code in PLACES|REMOVES|{1,43,12,59,82,15,89}:
            root_raw.extend(encode_tag(code,raw))
    root_raw.extend(b"\0\0")
    root=timeline(bytes(root_raw),0,nframes,detailed)
    sprites=[]
    total=Counter()
    for cid,n,raw in sprite_raw:
        record=timeline(raw,cid,n,detailed)
        if str(cid) in names:
            record["symbol_name"]=names[str(cid)]
        sprites.append(record)
        total["sprite_frames_declared"]+=n
        total["sprite_frames_observed"]+=record["show_frames"]
        total["placements"]+=record["place_events"]
        total["removals"]+=record["remove_events"]
        total["parse_warnings"]+=record["parse_warnings"]
    return {
        "swf_version":swf[3],"fps":fps,"stage_frames":nframes,
        "root":root,"sprites":sprites,"sprite_count":len(sprites),
        "symbol_names":names if detailed else len(names),
        "totals":dict(total),
        "limitation":"Static tags only. ActionScript may create or move objects at runtime."
    }

def main():
    p=argparse.ArgumentParser()
    p.add_argument("--archive",required=True)
    p.add_argument("--out",default="dist/timeline-catalog")
    p.add_argument("--details",default="",help="Comma-separated SWF basenames for full frame events")
    p.add_argument("--limit",type=int,default=0)
    p.add_argument("--strict",action="store_true")
    args=p.parse_args()
    out=Path(args.out)
    out.mkdir(parents=True,exist_ok=True)
    names={x.strip().lower() for x in args.details.split(",") if x.strip()}
    found=set()
    totals=Counter()
    rows=[]
    errors=[]
    with zipfile.ZipFile(args.archive) as z:
        swfs=sorted((x for x in z.infolist() if
                     not x.is_dir() and x.filename.lower().endswith(".swf")),
                    key=lambda x:x.filename.lower())
        if args.limit:swfs=swfs[:args.limit]
        for i,member in enumerate(swfs,1):
            basename=PurePosixPath(member.filename).name
            detail=basename.lower() in names
            if detail:found.add(basename.lower())
            rel=member.filename.removeprefix("social-warriors_0.02a/")
            try:
                result=inspect(z.read(member),detail)
                totals["swfs"]+=1
                totals["sprites"]+=result["sprite_count"]
                for k,v in result["totals"].items():totals[k]+=v
                rows.append({
                    "path":rel,"bytes":member.file_size,
                    "fps":result["fps"],"stage_frames":result["stage_frames"],
                    "sprites":result["sprite_count"],
                    "sprite_frames":result["totals"].get("sprite_frames_declared",0),
                    "placements":result["totals"].get("placements",0),
                    "removals":result["totals"].get("removals",0),
                    "parse_warnings":result["totals"].get("parse_warnings",0)
                })
                if detail:
                    outfile=out/(basename[:-4]+".timeline.json.gz")
                    with gzip.open(outfile,"wt",encoding="utf-8") as fh:
                        json.dump({"source":rel,**result},fh,
                                  ensure_ascii=False,separators=(",",":"))
                    print("TIMELINE_DETAIL",basename,
                          "sprites",result["sprite_count"],
                          "declared_frames",result["totals"].get("sprite_frames_declared",0),
                          "warnings",result["totals"].get("parse_warnings",0),flush=True)
                    for item in [result["root"], *result["sprites"]]:
                        if item.get("parse_warnings", 0):
                            print("TIMELINE_PARSE_WARNING", basename,
                                  "sprite_id", item["character_id"],
                                  json.dumps(item.get("warnings", [])), flush=True)
            except Exception as exc:
                errors.append({"source":rel,"error":str(exc)})
                print("TIMELINE_PARSE_ERROR",rel,str(exc),flush=True)
            if i%200==0:print("TIMELINE_PROGRESS",i,len(swfs),flush=True)
    fields=["path","bytes","fps","stage_frames","sprites",
            "sprite_frames","placements","removals","parse_warnings"]
    with (out/"timeline_inventory.csv").open("w",newline="",encoding="utf-8") as f:
        w=csv.DictWriter(f,fieldnames=fields)
        w.writeheader()
        w.writerows(rows)
    summary={"attempted":len(swfs),"analyzed":len(rows),
             "selected_details":sorted(names),"found_details":sorted(found),
             "totals":dict(totals),"errors":errors,
             "note":"Static SWF timelines and references, not completed playable animations."}
    (out/"timeline_summary.json").write_text(json.dumps(summary,indent=2),encoding="utf-8")
    print("TIMELINE_TOTALS",json.dumps(summary["totals"]),flush=True)
    print("TIMELINE_ERRORS",len(errors),flush=True)
    if args.strict and (errors or names-found):
        raise SystemExit("Timeline inventory failed validation")

if __name__=="__main__":
    main()
