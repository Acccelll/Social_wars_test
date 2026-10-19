#!/usr/bin/env python3
"""5D.8F: bounded, read-only FFDec ActionScript tutorial handler probe.

Only metadata is intended for repository; AS3 decompilation and full logs
must remain temporary GitHub Actions artifacts. Never replace/edit SWFs.
"""
import argparse
import hashlib
import json
import re
import shutil
import subprocess
import tempfile
import zipfile
from collections import Counter
from pathlib import Path, PurePosixPath

SWF_NAME="Basesec_1.5.4.swf"
SHA256="e4ce0218920a30fceee85ba750df3eedffa3f90e977bd117655704e297e0dc77"
TARGET_TERMS=("PopupTutorialMC","TutorialMain","tutorialMode","closeWindow",
              "RESCUE YOUR COMRADE","MouseEvent","addEventListener")
CLASS_MATCH=re.compile(r"(?<![A-Za-z0-9_$])(?:[A-Za-z_$][A-Za-z0-9_$]*\.)*"
                       r"(?:PopupTutorialMC|TutorialMain)(?![A-Za-z0-9_$])")
METHOD_MATCH=re.compile(r"\b(?:public|private|protected|internal)?\s*"
                        r"(?:override\s+|static\s+|final\s+)*function\s+"
                        r"([A-Za-z_$][A-Za-z0-9_$]*)\s*\(",re.M)

def extract_original(zip_path,output):
    with zipfile.ZipFile(zip_path) as archive:
        candidates=[x for x in archive.infolist() if
                    not x.is_dir() and PurePosixPath(x.filename).name==SWF_NAME]
        if len(candidates)!=1:raise ValueError("Expected one original "+SWF_NAME)
        with archive.open(candidates[0]) as inp, output.open("wb") as dst:
            shutil.copyfileobj(inp,dst)
    sha=hashlib.sha256(output.read_bytes()).hexdigest()
    if sha!=SHA256:raise ValueError("Unexpected Basesec SHA256: "+sha)
    return sha

def run_ffdec(java,jar,arguments,log,timeout):
    cmd=[java,"-Xmx3g","-Djava.awt.headless=true","-jar",str(jar),"-cli",*arguments]
    try:
        run=subprocess.run(cmd,stdout=subprocess.PIPE,stderr=subprocess.STDOUT,
                           text=True,errors="replace",timeout=timeout)
        output=run.stdout
        status={"returncode":run.returncode,"timed_out":False,
                "output_chars":len(output)}
    except subprocess.TimeoutExpired as e:
        output=(e.stdout or b"")
        if isinstance(output,bytes):output=output.decode("utf-8","replace")
        status={"returncode":None,"timed_out":True,"output_chars":len(output)}
    log.write_text(output[-8_000_000:],encoding="utf-8")
    return output,status

def summarize_scripts(folder):
    files=sorted(folder.rglob("*.as"))
    indexed=[]
    class_methods={}
    for path in files:
        src=path.read_text(encoding="utf-8",errors="replace")
        relative=path.relative_to(folder).as_posix()
        if len(src)>2_000_000:continue
        terms={term:len(re.findall(re.escape(term),src,re.I))
               for term in TARGET_TERMS if re.search(re.escape(term),src,re.I)}
        methods=sorted(set(METHOD_MATCH.findall(src)))
        indexed.append({"relative_path":relative,"bytes":path.stat().st_size,
                        "target_occurrences":terms,"method_names":methods[:90]})
        class_methods[relative]=methods
    return indexed

def inspect(archive,jar,out,java="java"):
    out=Path(out);out.mkdir(parents=True,exist_ok=True)
    jar=Path(jar).resolve()
    if not jar.is_file():raise ValueError("Missing FFDec jar")
    with tempfile.TemporaryDirectory(prefix="sw-5d8f-") as td:
        tmp=Path(td);swf=tmp/SWF_NAME
        sha=extract_original(archive,swf)
        listing,ls=run_ffdec(java,jar,["-dumpAS3",str(swf)],
                             out/"dump_as3.log",140)
        matches=sorted({x.group() for x in CLASS_MATCH.finditer(listing)})
        matched_lines=[ln.strip()[:450] for ln in listing.splitlines()
                       if any(t in ln.lower() for t in
                              ("popuptutorialmc","tutorialmain","tutorialmode",
                               "closewindow","resc"))]
        filtered=sorted(set(matches),key=lambda s:(s.count("."),len(s)),reverse=True)
        # Fully qualified names, if provided by FFDec dump, take priority.
        chosen=filtered[:20]
        # These original class names were verified from FFDec's AS3 dump
        # in the first 5D.8F pass, not inferred from file names.
        followup_classes=[
            "popups.PopupTutorial","popups.PopupIntro","popups.PopupConfirm",
            "popups.PopupMissionInfo","popups.PopupNextMission",
            "popups.PopupAlert","managers.PopupManager",
            "cutscene.CutScene","quest.QuestInfo"
        ]
        present=set(re.findall(
            r"^([A-Za-z_$][A-Za-z0-9_$]*(?:\\.[A-Za-z_$][A-Za-z0-9_$]*)*)\\s+\\d+\\s*$",
            listing,re.M))
        followup=[name for name in followup_classes if name in present]
        candidates = sorted(set((chosen or ["PopupTutorialMC","TutorialMain"])+followup))
        selected=out/"selected_actionscript"
        selected.mkdir(exist_ok=True)
        formats=[("as","as3_source"),("pcode","as3_pcode")]
        statuses={}
        all_index=[]
        for fmt,key in formats:
            root=selected/key;root.mkdir(exist_ok=True)
            _,status=run_ffdec(java,jar,[
                "-selectclass",",".join(candidates),
                "-format","script:"+fmt,
                "-timeout","25","-exportFileTimeout","45",
                "-exportTimeout","140",
                "-export","script",str(root),str(swf)],
                out/("ffdec_"+key+".log"),170)
            statuses[key]=status
            all_index+= [{"format":fmt,**r} for r in summarize_scripts(root)]
        result={
            "original_swf":SWF_NAME,"original_sha256":sha,
            "dump_status":ls,"dump_matched_lines":matched_lines[:60],
            "dump_class_candidates":matches[:60],
            "selected_class_names":candidates,
            "verified_popup_logic_classes":followup,
            "export_statuses":statuses,
            "exported_scripts":all_index,
            "as_source_files":sum(x["format"]=="as" for x in all_index),
            "pcode_files":sum(x["format"]=="pcode" for x in all_index),
            "root_cause_verified":False,
            "click_handler_verified":False,
            "runtime_modal_dismissed":False,
            "warning":"AS3 method names alone cannot prove a UI event handler was executed."
        }
        (out/"tutorial_as3_index.json").write_text(
            json.dumps(result,indent=2,ensure_ascii=False)+"\n",encoding="utf-8")
        print("TUTORIAL_AS3_5D8F",json.dumps({
            "class_candidates":matches[:15],
            "as_source_files":result["as_source_files"],
            "pcode_files":result["pcode_files"],
            "methods":{x["relative_path"]:x["method_names"][:20]
                       for x in all_index if x["format"]=="as"},
            "dump_timed_out":ls["timed_out"],
            "export_statuses":statuses
        },ensure_ascii=False),flush=True)
        return result

def main():
    p=argparse.ArgumentParser()
    p.add_argument("--archive",required=True)
    p.add_argument("--ffdec",required=True)
    p.add_argument("--out",default="dist/tutorial-as3-5d8f")
    a=p.parse_args()
    inspect(a.archive,a.ffdec,a.out)
if __name__=="__main__":main()
