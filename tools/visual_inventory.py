#!/usr/bin/env python3
"""SWF/bitmap visual inventory for Social Warriors 0.02a.
Analysis only; does NOT extract/distribute copyrighted imagery.
Works directly from the official bundle ZIP; standard Python 3 library.
"""
import argparse
import csv
import hashlib
import json
import struct
import zipfile
import zlib
import lzma
from collections import Counter
from pathlib import Path, PurePosixPath

TAGS = {
    2: "shape", 22: "shape", 32: "shape", 83: "shape",
    46: "morphshape", 84: "morphshape",
    6: "bitmap", 21: "bitmap", 35: "bitmap", 90: "bitmap",
    20: "bitmap", 36: "bitmap",
    39: "sprite", 7: "button", 34: "button",
    14: "sound", 18: "sound_stream", 45: "sound_stream",
    4: "placement", 26: "placement", 70: "placement", 94: "placement",
    12: "script", 59: "script", 82: "script", 9: "background",
    76: "symbolclass", 56: "exportassets", 87: "binarydata",
}
EXTERNAL = {".png", ".jpg", ".jpeg", ".webp", ".gif", ".bmp", ".svg", ".apng"}
EXPECTED_MAIN_SHA = "e4ce0218920a30fceee85ba750df3eedffa3f90e977bd117655704e297e0dc77"

def scan_swf(binary):
    if len(binary) < 12 or binary[:3] not in (b"FWS", b"CWS", b"ZWS"):
        raise ValueError("SWF header absent")
    declared = struct.unpack_from("<I", binary, 4)[0]
    if declared > 150_000_000:
        raise ValueError("SWF uncompressed size exceeds inventory safety limit")
    if binary[:3] == b"FWS":
        body = binary[8:]
    elif binary[:3] == b"CWS":
        body = zlib.decompress(binary[8:])
    else:
        raise ValueError("LZMA/ZWS detected; requires FFDec for detailed indexing")
    if not body:
        raise ValueError("SWF body empty")
    nbits = body[0] >> 3
    rect_length = (5 + 4 * nbits + 7) // 8
    ptr = rect_length + 4
    if ptr > len(body):
        raise ValueError("Truncated SWF frame header")
    tags = Counter()
    symbol_names = []
    frames_in_sprites = 0
    while ptr + 2 <= len(body):
        tagword = int.from_bytes(body[ptr:ptr + 2], "little")
        ptr += 2
        code, length = tagword >> 6, tagword & 63
        if length == 63:
            if ptr + 4 > len(body):
                raise ValueError("Truncated long SWF tag")
            length = int.from_bytes(body[ptr:ptr + 4], "little")
            ptr += 4
        if ptr + length > len(body):
            raise ValueError("Truncated tag payload")
        if code == 0:
            break
        category = TAGS.get(code)
        if category:
            tags[category] += 1
        if code == 39 and length >= 4:
            frames_in_sprites += int.from_bytes(body[ptr + 2:ptr + 4], "little")
        if code in (76, 56) and length >= 2:
            p, end = ptr + 2, ptr + length
            count = int.from_bytes(body[ptr:ptr+2], "little")
            for _ in range(min(count, 50000)):
                if p + 2 > end: break
                p += 2
                stop = body.find(b"\x00", p, end)
                if stop < 0: break
                name = body[p:stop].decode("utf-8", errors="replace")
                if name:
                    symbol_names.append(name)
                p = stop + 1
        ptr += length
    output = dict(tags)
    output["sprite_timeline_frames"] = frames_in_sprites
    output["symbol_names"] = len(set(symbol_names))
    return output

def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--archive", required=True, help="Official Social Warriors 0.02a ZIP")
    ap.add_argument("--out", default="dist/visual-inventory")
    args = ap.parse_args()
    dest = Path(args.out)
    dest.mkdir(parents=True, exist_ok=True)
    manifest = []
    swfs = []
    external = []
    total = Counter()
    errors = []
    with zipfile.ZipFile(args.archive) as archive:
        records = [info for info in archive.infolist() if not info.is_dir()]
        for idx, info in enumerate(records, 1):
            name = info.filename.replace("\\", "/")
            suffix = PurePosixPath(name).suffix.lower()
            if suffix in EXTERNAL:
                record = dict(path=name, bytes=info.file_size, category=suffix[1:])
                external.append(record)
                total["external_bitmaps_and_vectors"] += 1
            if suffix == ".swf":
                record = dict(path=name, compressed_zip_bytes=info.compress_size,
                              bytes=info.file_size)
                try:
                    data = archive.read(info)
                    digest = hashlib.sha256(data).hexdigest()
                    record["sha256"] = digest
                    record["tags"] = scan_swf(data)
                    for key, val in record["tags"].items():
                        if key != "symbol_names":
                            total[key] += val
                    if PurePosixPath(name).name == "Basesec_1.5.4.swf":
                        record["is_expected_client"] = digest == EXPECTED_MAIN_SHA
                except Exception as exc:
                    record["error"] = str(exc)
                    errors.append(dict(path=name, error=str(exc)))
                swfs.append(record)
                total["swf_files"] += 1
            if idx % 10000 == 0:
                print(f"INSPECTED {idx}/{len(records)} archive members", flush=True)
        total["archive_files"] = len(records)
        total["archive_compressed_size"] = Path(args.archive).stat().st_size
    fields = ["path", "bytes", "compressed_zip_bytes", "sha256", "error",
              "bitmap", "shape", "morphshape", "sprite", "button",
              "sprite_timeline_frames", "symbol_names", "sound"]
    with open(dest / "swfs.csv", "w", encoding="utf-8", newline="") as f:
        w = csv.DictWriter(f, fieldnames=fields)
        w.writeheader()
        for row in swfs:
            flattened = {key: row.get(key, row.get("tags", {}).get(key, ""))
                         for key in fields}
            w.writerow(flattened)
    with open(dest / "external_images.csv", "w", encoding="utf-8", newline="") as f:
        w = csv.DictWriter(f, fieldnames=["path", "bytes", "category"])
        w.writeheader()
        w.writerows(external)
    for row in sorted(swfs, key=lambda x: sum(x.get("tags", {}).get(k, 0)
                  for k in ("bitmap","shape","sprite","morphshape","button")),
                  reverse=True)[:20]:
        manifest.append({"path":row["path"], "tags":row.get("tags",{}),
                         "error":row.get("error")})
    result = {
        "source": "Official 0.02a Social Warriors distribution",
        "totals": dict(total),
        "errors": errors,
        "priority_swfs": manifest,
        "main_swf": [r for r in swfs if PurePosixPath(r["path"]).name == "Basesec_1.5.4.swf"],
        "note": "Tags are definitions, not rendered frames; a sprite can contain many frames. A count here does not mean graphics have been exported."
    }
    (dest / "summary.json").write_text(json.dumps(result, indent=2, ensure_ascii=False), encoding="utf-8")
    print("VISUAL_INVENTORY_SUMMARY", json.dumps(result["totals"], sort_keys=True), flush=True)
    print("VISUAL_INVENTORY_ERRORS", len(errors), flush=True)
    print("MAIN_SWF", json.dumps(result["main_swf"]), flush=True)
    print("VISUAL_INVENTORY_TOP", json.dumps(manifest[:8]), flush=True)

if __name__ == "__main__":
    main()
