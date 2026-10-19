#!/usr/bin/env python3
"""Metadata-only source catalog; images themselves are never committed."""
import argparse
import csv
import json
import re
import zipfile
from collections import Counter
from pathlib import PurePosixPath, Path

def category(path):
    parts=[x for x in PurePosixPath(path.replace("\\","/")).parts
           if x not in ("social-warriors_0.02a",)]
    if len(parts)<2 or parts[0]!="assets":
        return "other"
    if parts[1] == "sprites":
        return "unit_and_entity_sprites"
    return "assets/" + parts[1]

def label_for(path):
    stem=PurePosixPath(path).stem
    m=re.match(r"^(\d+)[_-](.+)$",stem)
    identifier=m.group(1) if m else ""
    label=(m.group(2) if m else stem).replace("_"," ").replace("-"," ").strip()
    return identifier,label

def main():
    p=argparse.ArgumentParser()
    p.add_argument("--archive",required=True)
    p.add_argument("--out",default="dist/visual-source-catalog")
    args=p.parse_args()
    dest=Path(args.out)
    dest.mkdir(parents=True,exist_ok=True)
    rows=[]
    by_category=Counter()
    swf_by_category=Counter()
    by_type=Counter()
    building_re=re.compile(
        r"(tower|barracks|laboratory|factory|fortress|bunker|turret|"
        r"mine|storage|reactor|power|command|radar|garage|"
        r"headquarters|building|hospital|generator|wall|gate|"
        r"warehouse|workshop|construction|drill|silo|plant|"
        r"artillery|defense|defence|fort)", re.IGNORECASE)
    with zipfile.ZipFile(args.archive) as z:
        for entry in z.infolist():
            if entry.is_dir(): continue
            filename=entry.filename.replace("\\","/")
            suffix=PurePosixPath(filename).suffix.lower()
            folder=category(filename)
            by_category[folder]+=1
            by_type[suffix or "[none]"]+=1
            if suffix!=".swf":continue
            swf_by_category[folder]+=1
            identifier,label=label_for(filename)
            rows.append({"path":filename,"category":folder,
                         "name":PurePosixPath(filename).name,"id":identifier,
                         "label":label,"size_bytes":entry.file_size})
    rows.sort(key=lambda x:(x["category"],x["name"].lower()))
    building_candidates=[
        {**row, "classification":"filename_heuristic_only"}
        for row in rows if building_re.search(row["label"])
    ]
    with (dest/"swf_catalog.csv").open("w",encoding="utf-8",newline="") as f:
        writer=csv.DictWriter(f,fieldnames=["path","category","name","id","label","size_bytes"])
        writer.writeheader()
        writer.writerows(rows)
    with (dest/"building_candidates.csv").open("w",encoding="utf-8",newline="") as f:
        writer=csv.DictWriter(f,fieldnames=["path","category","name","id",
                                             "label","size_bytes","classification"])
        writer.writeheader()
        writer.writerows(building_candidates)
    meta={"swf_count":len(rows),
          "swf_by_category":dict(swf_by_category.most_common()),
          "building_candidate_count":len(building_candidates),
          "asset_directories":dict(by_category.most_common()),
          "file_extensions":dict(by_type.most_common()),
          "note":"Category is derived from ZIP directories, not visually verified class identity."}
    (dest/"catalog_summary.json").write_text(json.dumps(meta,indent=2,ensure_ascii=False),encoding="utf-8")
    print("VISUAL_CATALOG_SUMMARY",json.dumps({"swfs":len(rows),"folders":dict(by_category.most_common(16))}),flush=True)
    print("VISUAL_CATALOG_SAMPLE",json.dumps(rows[:8]),flush=True)
    print("VISUAL_SWF_CATEGORY_COUNTS",json.dumps(dict(swf_by_category.most_common())),flush=True)
    print("VISUAL_BUILDING_CANDIDATES",json.dumps(building_candidates[:45],ensure_ascii=False),flush=True)

if __name__=="__main__":
    main()
