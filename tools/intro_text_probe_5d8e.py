#!/usr/bin/env python3
"""Read-only scan of original Flash and server configuration for intro strings.

Searches text evidence, not AS3 control-flow or the rendering tree.
Does not claim the root cause of the unresponsive Ruffle modal.
"""
import argparse
import json
import re
import zlib
import zipfile
from collections import Counter
from pathlib import Path

TARGETS=("Basesec_1.5.4.swf","SWLoader.swf")
TERMS=("rescue your comrade","rescue","comrade","tutorial","welcome",
       "mission","quest","popup","dialog","close","mouseevent","click")
MAX_MB=180

def decompress_swf(data):
    if len(data)<8:raise ValueError("Truncated SWF")
    signature=data[:3]
    if signature==b"FWS":
        return data[8:]
    if signature==b"CWS":
        raw=zlib.decompress(data[8:])
        if len(raw)>MAX_MB*1024*1024:raise ValueError("SWF inflated too large")
        return raw
    if signature==b"ZWS":
        raise ValueError("ZWS unsupported in this text-only scanner")
    raise ValueError("Unexpected SWF signature")

def sample_text(data):
    # AS3 strings are length-prefixed in ABC; presence of a matching
    # sequence is only a clue, not proof of its use in UI behavior.
    matched={}
    for term in TERMS:
        expression=re.compile(re.escape(term.encode()),re.I)
        hits=list(expression.finditer(data))
        matches=[]
        for hit in hits[:6]:
            fragment=data[max(0,hit.start()-44):min(len(data),hit.end()+72)]
            printable="".join(chr(b) if 32<=b<127 else " " for b in fragment)
            matches.append(" ".join(printable.split())[:150])
        matched[term]={"occurrences":len(hits),"samples":matches}
    return matched

def execute(archive,config_dir):
    report={"scope":"string evidence only, NOT Flash UI or AS3 control flow",
            "swfs":{},"config_matches":{},
            "likely_tutorial_code_located":False}
    with zipfile.ZipFile(archive) as source:
        lookup={}
        for info in source.infolist():
            if not info.is_dir() and info.filename.lower().endswith(".swf"):
                name=Path(info.filename).name
                if name in TARGETS:lookup[name]=info
        for filename in TARGETS:
            if filename not in lookup:raise ValueError("Missing "+filename)
            raw=decompress_swf(source.read(lookup[filename]))
            report["swfs"][filename]={
                "uncompressed_body_bytes":len(raw),
                "term_matches":sample_text(raw)}
    cfg=Path(config_dir)
    if cfg.is_dir():
        for p in sorted(cfg.rglob("*.json")):
            if p.stat().st_size>50*1024*1024:continue
            try:
                text=p.read_text(encoding="utf-8")
            except UnicodeDecodeError:
                continue
            candidate=sample_text(text.encode("utf-8"))
            if any(x["occurrences"] for x in candidate.values()):
                report["config_matches"][str(p.relative_to(cfg))]={
                    key:val for key,val in candidate.items() if val["occurrences"]
                }
    # Never infer code location from string hits alone.
    return report

def main():
    ap=argparse.ArgumentParser()
    ap.add_argument("--archive",required=True)
    ap.add_argument("--config",required=True)
    ap.add_argument("--out",required=True)
    args=ap.parse_args()
    result=execute(args.archive,args.config)
    out=Path(args.out)
    out.parent.mkdir(parents=True,exist_ok=True)
    out.write_text(json.dumps(result,indent=2,ensure_ascii=False)+"\n",encoding="utf-8")
    print("INTRO_TEXT_EVIDENCE_5D8E",json.dumps({
        "swf_rescue_hits":{name:report["term_matches"]["rescue"]["occurrences"]
                           for name,report in result["swfs"].items()},
        "swf_tutorial_hits":{name:report["term_matches"]["tutorial"]["occurrences"]
                           for name,report in result["swfs"].items()},
        "config_files_with_terms":len(result["config_matches"]),
        "root_cause_confirmed":False
    }))
if __name__=="__main__":
    main()
