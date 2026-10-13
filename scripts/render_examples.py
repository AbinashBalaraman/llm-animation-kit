"""Produce actual before/after preview evidence using the public tool API."""
from pathlib import Path
import json
import shutil
import sys

ROOT=Path(__file__).resolve().parents[1]
sys.path.insert(0,str(ROOT))

from animation_kit.contracts import packaged_json
from animation_kit.tools import Tools

api=Tools(ROOT/".kit-workspace")

def call(tool,arguments):
    response=api.call(tool,arguments)
    if not response["ok"]:
        raise RuntimeError(response)
    return response["result"]

def collect(project_id,name):
    result=call("preview",{"project_id":project_id})
    destination=ROOT/"examples"/"golden"/name
    destination.mkdir(parents=True,exist_ok=True)
    folder=Path(result["manifest_path"]).parent
    for filename in ("video.mp4","contact-sheet.png","scene.json","trace.json","manifest.json","sound.wav"):
        if (folder/filename).exists():
            shutil.copy2(folder/filename,destination/filename)
    public_result=dict(result)
    for key,filename in (("manifest_path","manifest.json"),("video_path","video.mp4"),("contact_sheet_path","contact-sheet.png")):
        public_result[key]=(destination/filename).relative_to(ROOT).as_posix()
    return public_result

records=[]
if not (api.store.project("discovery-demo")/"current.json").exists():
    records.append({"tool":"load_example","arguments":{"project_id":"discovery-demo","example_id":"discovery"},"result":call("load_example",{"project_id":"discovery-demo","example_id":"discovery"})})
# A rerun reconstructs independent authored sources rather than hiding revisions.
original=packaged_json("examples/discovery.json")
for ident in ("discovery-original","discovery-revised","friends-demo"):
    if not (api.store.project(ident)/"current.json").exists():
        call("create_project",{"project_id":ident,"scene":packaged_json("examples/two_friends.json") if ident=="friends-demo" else original,"legacy_exercise":True})
base=collect("discovery-original","discovery-before")
revision=api.store.load("discovery-revised")
if revision["revision"]==0:
    # First show the actual conflict produced by a naive linked timing edit.
    bad={"project_id":"discovery-revised","expected_revision":0,"operations":[{"type":"shift_action","action_id":"wonder","delta":12},{"type":"shift_action","action_id":"reach","delta":12}]}
    rejected=api.call("apply_revision",bad)
    if rejected["ok"]:
        raise AssertionError("Expected gesture overlap rejection")
    records.append({"tool":"apply_revision","arguments":bad,"response":rejected})
    celebration=next(a for a in original["actions"] if a["id"]=="celebrate")
    repaired=dict(celebration,start=132,end=191)
    good=dict(bad,operations=bad["operations"]+[
        {"type":"replace_action","action":repaired},
        {"type":"set_camera","shot_id":"reaction","camera":{"x":480,"y":285,"zoom":1.08}}])
    records.append({"tool":"apply_revision","arguments":good,"response":api.call("apply_revision",good)})
    if not records[-1]["response"]["ok"]:
        raise RuntimeError(records[-1])
revised=collect("discovery-revised","discovery-after")
friends=collect("friends-demo","two-friends")
report={"type":"authored worked examples, not a model benchmark","before":base,"after":revised,"friends":friends,"tool_records":records,
        "edit":"Delay the surprise/reach by 12 frames, repair the resulting gesture conflict explicitly, and widen the reaction camera.",
        "review_status":"awaiting visual inspection","quality_claim":"No professional-quality or model-parity claim."}
(ROOT/"examples"/"golden"/"run-record.json").write_text(json.dumps(report,indent=2)+"\n",encoding="utf-8")
print(json.dumps({"before":base["video_path"],"after":revised["video_path"],"friends":friends["video_path"]},indent=2))
