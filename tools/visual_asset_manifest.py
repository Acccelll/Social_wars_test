#!/usr/bin/env python3
"""Generate an auditable catalog of rendered resources from FFDec output.

This script does NOT export graphics. It indexes an existing local
visual-export directory; output CSV contains metadata only.
"""
import argparse
import csv
import hashlib
import json
import struct
from collections import Counter
from pathlib import Path

KNOWN = {".png",".jpg",".jpeg",".gif",".webp",".svg",".bmp"}

def dimensions(file, ext):
    try:
        with file.open("rb") as f:
            head=f.read(32)
        if ext == ".png" and head.startswith(b"\x89PNG\r\n\x1a\n") and len(head)>=24:
            w,h=struct.unpack(">II",head[16:24])
            return w,h
        if ext == ".gif" and head[:3] == b"GIF" and len(head)>=10:
            w,h=struct.unpack("<HH",head[6:10])
            return w,h
    except (ValueError,OSError):
        pass
    return None,None

def main():
    p=argparse.ArgumentParser()
    p.add_argument("--root",required=True,help="Previously exported FFDec directory")
    p.add_argument("--out",default=None,help="Metadata directory; defaults to root")
    args=p.parse_args()
    root=Path(args.root).resolve()
    if not root.is_dir(): p.error("Export directory does not exist")
    output=Path(args.out).resolve() if args.out else root
    output.mkdir(parents=True,exist_ok=True)

    rows=[]
    groups=Counter()
    ext_counts=Counter()
    for file in sorted(root.rglob("*")):
        if not file.is_file() or file.suffix.lower() not in KNOWN: continue
        rel=file.relative_to(root).as_posix()
        ext=file.suffix.lower()
        parts=file.relative_to(root).parts
        if parts[0] == "swfs" and len(parts)>=4:
            # Example swfs/assets/sprites/1212_tetrapod_mech/image/1.png
            source=("/".join(parts[1:4]) + ".swf")
            group=parts[4] if len(parts)>=5 else "other"
        elif parts[0] == "external":
            source="external"
            group="external"
        else:
            source="unknown"
            group="other"
        width,height=dimensions(file,ext)
        h=hashlib.sha256()
        with file.open("rb") as stream:
            for block in iter(lambda:stream.read(1024*1024),b""):
                h.update(block)
        rows.append({"source":source,"path":rel,"group":group,
                     "format":ext.lstrip("."),"bytes":file.stat().st_size,
                     "width":width or "","height":height or "",
                     "sha256":h.hexdigest()})
        groups[source]+=1
        ext_counts[ext.lstrip(".")]+=1

    with (output/"visual_files.csv").open("w",encoding="utf-8",newline="") as f:
        w=csv.DictWriter(f,fieldnames=["source","path","group","format",
                                       "bytes","width","height","sha256"])
        w.writeheader()
        w.writerows(rows)
    summary={"total_exported_files":len(rows),
             "by_source":dict(groups.most_common()),
             "by_format":dict(ext_counts.most_common()),
             "limitations":"Metadata catalog, not proof of animation fidelity or visual correctness"}
    (output/"visual_files_summary.json").write_text(json.dumps(summary,indent=2),encoding="utf-8")
    print("VISUAL_FILES_SUMMARY",json.dumps(summary),flush=True)

if __name__=="__main__":
    main()
