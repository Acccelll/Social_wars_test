#!/usr/bin/env python3
"""Extract direct PNG/JPEG/GIF/WebP/SVG assets from original 0.02a ZIP.
No decompiler required; embedded SWF bitmaps are a separate stage.
"""
import argparse
import csv
import hashlib
import json
import shutil
import zipfile
from collections import Counter
from pathlib import Path, PurePosixPath

EXT = {".png", ".jpg", ".jpeg", ".bmp", ".webp", ".gif", ".svg", ".apng"}

def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--archive", required=True)
    ap.add_argument("--out", default="dist/visual-external")
    args = ap.parse_args()
    root = Path(args.out).resolve()
    root.mkdir(parents=True,exist_ok=True)
    rows=[]
    counts=Counter()
    with zipfile.ZipFile(args.archive) as z:
        for record in z.infolist():
            if record.is_dir(): continue
            p = PurePosixPath(record.filename.replace("\\", "/"))
            if p.suffix.lower() not in EXT: continue
            if p.is_absolute() or ".." in p.parts:
                raise ValueError("Unsafe member: " + record.filename)
            parts=list(p.parts)
            if parts and parts[0] == "social-warriors_0.02a":
                parts.pop(0)
            dest=root.joinpath(*parts)
            dest.parent.mkdir(parents=True,exist_ok=True)
            h=hashlib.sha256()
            with z.open(record) as src, dest.open("wb") as dst:
                while chunk:=src.read(1024*1024):
                    h.update(chunk)
                    dst.write(chunk)
            ext=p.suffix.lower().lstrip(".")
            rows.append({"path":str(Path(*parts)).replace("\\","/"),"bytes":record.file_size,
                         "extension":ext,"sha256":h.hexdigest()})
            counts["total_files"]+=1
            counts["total_bytes"]+=record.file_size
            counts["extension_"+ext]+=1
    with (root/"external_manifest.csv").open("w",newline="",encoding="utf-8") as f:
        w=csv.DictWriter(f,fieldnames=["path","bytes","extension","sha256"])
        w.writeheader()
        w.writerows(rows)
    (root/"external_summary.json").write_text(
        json.dumps({"counts":dict(counts),"note":"Images external to SWFs only."},
                   indent=2),encoding="utf-8")
    print("EXTERNAL_EXTRACT_SUMMARY",json.dumps(dict(counts)),flush=True)
    if not rows: raise SystemExit("No image resources found")

if __name__=="__main__":
    main()
