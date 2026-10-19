#!/usr/bin/env python3
"""Batch extraction of Social Warriors visual resources using JPEXS FFDec.

Local-only or ephemeral CI output: do not commit the third-party assets.
By default exports bitmaps, shapes (SVG), morph shapes (SVG), buttons
(PNG), and sprite stills (PNG). Sprite timelines require a separate
animation pass; default PNG is NOT full animation preservation.
"""
import argparse
import csv
import hashlib
import json
import os
import shutil
import subprocess
import tempfile
import time
import zipfile
from pathlib import Path, PurePosixPath

DIRECT_IMAGES = {".png", ".jpg", ".jpeg", ".gif", ".webp", ".bmp", ".svg", ".apng"}
GRAPHIC_TYPES = "image,shape,morphshape,sprite,button"
SAFE_FORMATS = "shape:svg,morphshape:svg,sprite:png,button:png"
EXPECTED_MAIN = "e4ce0218920a30fceee85ba750df3eedffa3f90e977bd117655704e297e0dc77"

def relative_target(name):
    p = PurePosixPath(name.replace("\\", "/"))
    if p.is_absolute() or ".." in p.parts or not p.parts:
        raise ValueError("Unsafe archive member path: " + str(name))
    parts = list(p.parts)
    if len(parts) > 1 and parts[0] == "social-warriors_0.02a":
        parts.pop(0)
    return Path(*parts)

def files_recursive(path):
    return sum(1 for x in path.rglob("*") if x.is_file()) if path.exists() else 0

def main():
    p = argparse.ArgumentParser()
    p.add_argument("--archive", required=True)
    p.add_argument("--ffdec", required=True, help="Path to ffdec.jar")
    p.add_argument("--out", default="dist/visual-export")
    p.add_argument("--start", type=int, default=0,
                   help="Index into lexicographically sorted list of SWFs")
    p.add_argument("--limit", type=int, default=10,
                   help="Maximum number of SWFs to process (0 = all)")
    p.add_argument("--max-source-bytes", type=int, default=0,
                   help="Skip SWFs larger than this source byte count, 0 = no limit")
    p.add_argument("--external", action="store_true",
                   help="Extract external .png/.jpg/.webp/.svg/etc entries")
    p.add_argument("--only-basename", default="",
                   help="Optional exact SWF basename, e.g. Basesec_1.5.4.swf")
    p.add_argument("--names", default="",
                   help="Comma-separated exact SWF basenames to export as a group")
    p.add_argument("--path-prefix", default="",
                   help="SWFs beneath original assets path, e.g. assets/characters_2/")
    p.add_argument("--fail-on-error", action="store_true",
                   help="Fail exit code for FFDec errors in any source file")
    p.add_argument("--types", choices=("images", "visual", "sprites"),
                   default="visual")
    p.add_argument("--timeout", type=int, default=240)
    p.add_argument("--java", default="java")
    args = p.parse_args()

    if args.start < 0 or args.limit < 0:
        p.error("start and limit must be >= 0")
    if args.timeout < 10:
        p.error("timeout must be >= 10 seconds")
    ffdec = Path(args.ffdec).resolve()
    if not ffdec.is_file():
        p.error("Cannot find ffdec.jar at " + str(ffdec))

    dest = Path(args.out).resolve()
    dest.mkdir(parents=True, exist_ok=True)
    details = []
    errors = []
    counts = {"swf_attempted":0,"swf_exported":0,
              "exported_files":0,"external_files":0}
    types = ("image" if args.types == "images" else
             "sprite" if args.types == "sprites" else GRAPHIC_TYPES)

    with zipfile.ZipFile(args.archive) as z:
        members = [i for i in z.infolist() if not i.is_dir()]
        swfs = sorted((x for x in members
                       if PurePosixPath(x.filename).suffix.lower() == ".swf"),
                      key=lambda x:x.filename.lower())
        selection = swfs[args.start:] if args.limit == 0 else swfs[args.start:args.start+args.limit]
        if args.only_basename:
            selection = [x for x in swfs
                         if PurePosixPath(x.filename).name.lower() ==
                         args.only_basename.lower()]
        if args.names:
            chosen = [name.strip().lower() for name in args.names.split(",") if name.strip()]
            if len(chosen) != len(set(chosen)):
                p.error("--names contains duplicate basenames")
            selected_names = set(chosen)
            selection = [x for x in swfs
                         if PurePosixPath(x.filename).name.lower() in selected_names]
            found = {PurePosixPath(x.filename).name.lower() for x in selection}
            missing = selected_names - found
            if missing:
                p.error("SWF basename(s) missing from distribution: " + ", ".join(sorted(missing)))
        if not selection:
            p.error("No SWF matched the selected filters")
        if args.path_prefix:
            prefix = args.path_prefix.replace("\\", "/").strip("/")
            if not prefix.startswith("assets/") or ".." in prefix.split("/"):
                p.error("--path-prefix must be within assets/")
            selection = [x for x in selection
                         if relative_target(x.filename).as_posix().startswith(prefix + "/")]
        print(f"SWF_SELECTION total={len(swfs)} start={args.start} "
              f"selected={len(selection)} type={types}", flush=True)

        if args.external:
            for member in members:
                if PurePosixPath(member.filename).suffix.lower() not in DIRECT_IMAGES:
                    continue
                try:
                    rel = relative_target(member.filename)
                    target = dest / "external" / rel
                    target.parent.mkdir(parents=True, exist_ok=True)
                    with z.open(member) as src, target.open("wb") as out:
                        shutil.copyfileobj(src,out,1024*1024)
                    counts["external_files"] += 1
                except Exception as exc:
                    errors.append({"path":member.filename,"reason":str(exc)})
            print("EXTERNAL_IMAGES_EXPORTED",counts["external_files"],flush=True)

        for sequence, member in enumerate(selection, 1):
            rel = relative_target(member.filename)
            rec = {"path":member.filename, "bytes":member.file_size}
            if args.max_source_bytes and member.file_size > args.max_source_bytes:
                rec["status"] = "SKIPPED_SIZE"
                details.append(rec)
                continue
            counts["swf_attempted"] += 1
            sub = dest / "swfs" / rel.with_suffix("")
            sub.mkdir(parents=True,exist_ok=True)
            before = files_recursive(sub)
            try:
                with tempfile.TemporaryDirectory(prefix="socialwars-asset-") as tmp:
                    input_path = Path(tmp) / rel.name
                    with z.open(member) as src, input_path.open("wb") as out:
                        shutil.copyfileobj(src,out,1024*1024)
                    if rel.name == "Basesec_1.5.4.swf":
                        digest = hashlib.sha256(input_path.read_bytes()).hexdigest()
                        rec["reference_sha256_match"] = digest == EXPECTED_MAIN
                        if digest != EXPECTED_MAIN:
                            raise ValueError("SWF hash differs from recovered reference")
                    command = [args.java, "-Xmx2g", "-Djava.awt.headless=true",
                               "-jar",str(ffdec),"-cli",
                               "-format",SAFE_FORMATS,
                               "-export",types,str(sub),str(input_path)]
                    t0 = time.time()
                    finished = subprocess.run(command,stdout=subprocess.PIPE,
                                              stderr=subprocess.STDOUT, timeout=args.timeout,
                                              text=True,errors="replace")
                    rec["exit_code"] = finished.returncode
                    rec["elapsed_seconds"] = round(time.time()-t0,2)
                    rec["tail"] = finished.stdout[-1400:]
                    rec["created_files"] = max(files_recursive(sub)-before,0)
                    counts["exported_files"] += rec["created_files"]
                    if finished.returncode != 0:
                        rec["status"] = "FFDEC_ERROR"
                        errors.append({"path":member.filename,"exit_code":finished.returncode,
                                       "reason":rec["tail"]})
                    elif rec["created_files"] == 0:
                        # A vector-only SWF may legitimately contain no bitmaps.
                        # Do not count this as a failed extraction.
                        rec["status"] = "EMPTY_CATEGORY"
                    else:
                        rec["status"] = "EXPORTED"
                        counts["swf_exported"] += 1
            except Exception as exc:
                rec["status"] = "ERROR"
                rec["error"] = str(exc)
                errors.append({"path":member.filename, "reason":str(exc)})
            details.append(rec)
            print(f"SWF_EXPORT {sequence}/{len(selection)} "
                  f"{rel.name}: {rec.get('status')} files={rec.get('created_files',0)} "
                  f"seconds={rec.get('elapsed_seconds','?')}", flush=True)

    fields = ["path","bytes","status","exit_code","elapsed_seconds",
              "created_files","reference_sha256_match","error","tail"]
    with (dest/"export_results.csv").open("w",encoding="utf-8",newline="") as f:
        w = csv.DictWriter(f,fieldnames=fields)
        w.writeheader()
        for r in details:
            w.writerow({k:r.get(k,"") for k in fields})
    summary = {"source":"Social Warriors 0.02a user-owned/local archive",
               "export_types":types,"formats":SAFE_FORMATS,
               "totals":counts,"errors":errors,
               "limitations":"sprite PNG captures stills only, not every animation frame",
               "details":details}
    (dest/"export_summary.json").write_text(
        json.dumps(summary,indent=2,ensure_ascii=False),encoding="utf-8")
    print("VISUAL_EXPORT_SUMMARY",json.dumps(counts),flush=True)
    print("VISUAL_EXPORT_ERRORS",len(errors),flush=True)
    print("VISUAL_EXPORT_SELECTED",json.dumps(details[:5]),flush=True)
    if args.fail_on_error and errors:
        raise SystemExit(f"{len(errors)} extraction errors; inspect export_summary.json")
    if counts["swf_attempted"] and not counts["swf_exported"]:
        print("NOTE: zero files exported in requested category", flush=True)

if __name__ == "__main__":
    main()
