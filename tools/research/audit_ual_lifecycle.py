"""Observe the official pinned UAL and exact candidate in an owned CI host."""
import argparse
import hashlib
import json
import os
from pathlib import Path
import shutil
import subprocess

MODULE_HASHES = {
    "0.10.5-native-test": "8e6dd664c1fc0982a435b5932d0c9f006f1522926aa28b9556b7f2ce7dcb4695",
    "0.10.6-native-test": "30cc9542a2af3529fd4f3a2299d6331bddf51b61f8213a0a1a779b472789de3d",
}
LOADER_HASH = "fa266e3513d02c08a1b808f28c10538a489eaffaa4b0707f7cc1066e71b5afd7"


def digest(path):
    return hashlib.sha256(path.read_bytes()).hexdigest()


def main():
    p=argparse.ArgumentParser(description=__doc__)
    for name in ("host","module","loader","output"):
        p.add_argument("--"+name,type=Path,required=True)
    p.add_argument("--artifact-version",choices=sorted(MODULE_HASHES),default="0.10.5-native-test")
    args=p.parse_args()
    module_hash=MODULE_HASHES[args.artifact_version]
    if (os.name!="nt" or os.environ.get("GITHUB_ACTIONS")!="true" or
            os.environ.get("GITHUB_REPOSITORY")!="lineum-dynamics/nms-companion-auto-summon"):
        raise ValueError("Owned Windows CI only")
    if args.host.name!="cas-ual-host.exe" or digest(args.module)!=module_hash or digest(args.loader)!=LOADER_HASH:
        raise ValueError("Explicit host/module/loader identity differs")
    root=args.output.resolve().parent/"ual-owned-cases"
    if root.exists(): raise ValueError("Use a new owned case directory")
    root.mkdir(parents=True)
    env={key:value for key,value in os.environ.items() if key.upper() in
         {"SYSTEMROOT","WINDIR","SYSTEMDRIVE","PATH","TEMP","TMP","GITHUB_ACTIONS","GITHUB_REPOSITORY"}}
    report={"schema":1,"controller_revision":os.environ.get("GITHUB_SHA"),
            "artifact_version":args.artifact_version,
            "module_sha256":module_hash,"loader_sha256":LOADER_HASH,"host_sha256":digest(args.host),
            "game_access":False,"security_settings_changed":False,"cases":[],"passed":False,
            "scope":"Exact candidate and official UAL; unsupported owned host, normal process-exit teardown"}
    try:
        for mode in ("baseline","with-asi"):
            for index in range(3):
                stage=root/f"{mode}-{index}"; stage.mkdir()
                host=stage/"cas-ual-host.exe"; loader=stage/"winmm.dll"
                shutil.copyfile(args.host,host); shutil.copyfile(args.loader,loader)
                module=stage/"scripts/CompanionAutoSummon.asi"
                if mode=="with-asi":
                    module.parent.mkdir(); shutil.copyfile(args.module,module)
                if digest(host)!=report["host_sha256"] or digest(loader)!=LOADER_HASH:
                    raise ValueError("Staged owned inputs changed")
                if mode=="with-asi" and digest(module)!=module_hash: raise ValueError("Staged module changed")
                try:
                    run=subprocess.run([str(host),str(loader),mode],cwd=stage,env=env,
                                       capture_output=True,text=True,encoding="utf-8",timeout=20)
                except subprocess.TimeoutExpired:
                    report["cases"].append({"mode":mode,"index":index,"os_exit_code":None,"status":"HOST_TIMEOUT"})
                    raise
                case={"mode":mode,"index":index,"os_exit_code":run.returncode,"records":None}
                report["cases"].append(case)
                if run.returncode or run.stderr: raise RuntimeError("Owned UAL child failed")
                observed=json.loads(run.stdout); case["records"]=observed
                if (not observed.get("passed") or observed["asi_present"]!=(mode=="with-asi") or
                    observed["native_status"]!=(2 if mode=="with-asi" else 0) or
                    observed["manual_initialize_call"] or not observed["working_directory_restored"]):
                    raise ValueError("Owned UAL observations failed controls")
                if digest(loader)!=LOADER_HASH or (mode=="with-asi" and digest(module)!=module_hash):
                    raise ValueError("An input changed during the owned run")
        report["passed"]=True
    except Exception as error:
        report["error"]={"type":type(error).__name__,"reason":"Owned loader capture incomplete; inspect the failed case"}
        raise
    finally:
        args.output.write_text(json.dumps(report,indent=2)+"\n",encoding="utf-8")
    print(json.dumps({"passed":True,"cases":len(report["cases"]),"module_sha256":module_hash}))


if __name__=="__main__": main()
