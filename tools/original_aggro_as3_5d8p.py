#!/usr/bin/env python3
"""Read-only AVM2 origin inspection for auto-aggro constants and target scoring, SW 0.02a."""
import argparse
import hashlib
import json
import re
import shutil
import subprocess
import tempfile
import zipfile
from pathlib import Path,PurePosixPath

SWF_NAME="Basesec_1.5.4.swf"
SWF_SHA="e4ce0218920a30fceee85ba750df3eedffa3f90e977bd117655704e297e0dc77"
CLASSES=["core.Config","core.isoengine.IsoFightingElement","core.isoengine.IsoUnit","core.isoengine.IsoEngine","core.isoengine.isoUtils.CheckFunctions"]
KEYWORDS=re.compile(r"AGGRO_RANGE|getNearestTarget|fCheckNearestTarget|acquireNewTarget|IA_Attack|iAttackRange|distance\\(",re.I)
DECLARATION=re.compile(r"\b(?:public|private|protected|internal)\s+(?:static\s+)?(?:const|var)\s+AGGRO_RANGE\s*:\s*\w+\s*=\s*([^;]+);")
METHOD=re.compile(r"\b(?:public|private|protected|internal)\s+(?:override\s+)?function\s+([A-Za-z_]\w*)\s*\(",re.I)

def export(jar,swf,out,fmt):
    dest=out/("as3_"+fmt)
    dest.mkdir(parents=True,exist_ok=True)
    args=["java","-Xmx3g","-Djava.awt.headless=true","-jar",str(jar),"-cli",
          "-selectclass",",".join(CLASSES),"-format","script:"+fmt,
          "-timeout","25","-exportFileTimeout","60","-exportTimeout","160",
          "-export","script",str(dest),str(swf)]
    r=subprocess.run(args,capture_output=True,text=True,errors="replace",timeout=180)
    (out/("ffdec_"+fmt+".log")).write_text((r.stdout+"\n"+r.stderr)[-10000:])
    if r.returncode:raise ValueError(f"FFDec export {fmt} error: {r.returncode}")
    return dest

def main():
    p=argparse.ArgumentParser()
    for key in ("archive","ffdec","out"):p.add_argument("--"+key,required=True)
    a=p.parse_args();out=Path(a.out).resolve();out.mkdir(parents=True,exist_ok=True)
    if Path(a.archive).stat().st_size!=492630085:raise ValueError("Archive 0.02a size changed")
    with tempfile.TemporaryDirectory(prefix="sw-aggro-original-") as td,zipfile.ZipFile(a.archive) as z:
        entries=[x for x in z.infolist() if not x.is_dir() and PurePosixPath(x.filename).name==SWF_NAME]
        if len(entries)!=1:raise ValueError("Wrong original client SWF match count")
        swf=Path(td)/SWF_NAME
        with z.open(entries[0]) as f,swf.open("wb") as w:shutil.copyfileobj(f,w)
        sha=hashlib.sha256(swf.read_bytes()).hexdigest()
        if sha!=SWF_SHA:raise ValueError("Client SWF hash changed")
        dirs={fmt:export(a.ffdec,swf,out,fmt) for fmt in ("as","pcode")}
    info={"lot":"5D.8P","client_swf_sha256":sha,"original_swf_untouched":True,
          "requested_classes":CLASSES,"found_classes":[],"aggro_range_static_declarations":[],
          "method_index":[],"references_by_class":{},"note":"Static ActionScript expressions and line numbers are not dynamic proof of which detection mode executed at runtime."}
    for file in sorted(dirs["as"].rglob("*.as")):
        source=file.read_text(encoding="utf-8",errors="replace")
        name=file.relative_to(dirs["as"]).as_posix()
        if name.startswith("scripts/"):name=name[8:]
        name=name.removesuffix(".as").replace("/",".")
        info["found_classes"].append(name)
        lines=source.splitlines()
        matches=[]
        for index,line in enumerate(lines):
            if KEYWORDS.search(line):
                matches.append({"line":index+1,"source":line.strip()[:320]})
        info["references_by_class"][name]=matches[:120]
        for hit in DECLARATION.finditer(source):
            info["aggro_range_static_declarations"].append({
              "class":name,"expression":hit.group(1).strip(),
              "line":source.count("\n",0,hit.start())+1,
              "type":"source-level declaration"})
        for hit in METHOD.finditer(source):
            method=hit.group(1)
            if not any(t in method.lower() for t in ["target","attack","update","distance","check"]):continue
            start=hit.start();near=source[start:min(len(source),start+850)]
            info["method_index"].append({
             "class":name,"method":method,
             "line":source.count("\n",0,start)+1,
             "signature_and_opening":near[:280].replace("\n"," "),
             "mentions_aggro":bool("AGGRO_RANGE" in near)
            })
    if "core.Config" not in info["found_classes"]:raise ValueError("Missing Config AS3 source")
    (out/"aggro_code_index.json").write_text(json.dumps(info,indent=2,ensure_ascii=False)+"\n")
    print("AGGRO_STATIC_SOURCE_5D8P",json.dumps({
       "classes":info["found_classes"],
       "aggro_declarations":info["aggro_range_static_declarations"],
       "methods":len(info["method_index"]),
       "reference_counts":{k:len(v) for k,v in info["references_by_class"].items()}
    },ensure_ascii=False),flush=True)
if __name__=="__main__":main()
