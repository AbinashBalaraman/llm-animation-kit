"""Export the visually inspected example through a recorded production workflow."""
from pathlib import Path
import json
import shutil
import sys
import argparse

ROOT=Path(__file__).resolve().parents[1]
sys.path.insert(0,str(ROOT))
from animation_kit.tools import Tools

parser=argparse.ArgumentParser(description="Export a demo after explicit preview review.")
parser.add_argument("--review-notes",required=True,help="What you actually inspected and any unresolved limitations")
parser.add_argument("--reviewer",choices=("human","model"),required=True)
args=parser.parse_args()

api=Tools(ROOT/".kit-workspace")
started=api.call("start_workflow",{"brief":"Export the reviewed original 2D discovery example and retain the editable source and before/after evidence.","max_calls":12,"max_previews":3,"purpose":"legacy_exercise"})
ident=started["result"]["workflow_id"]
def step(tool,arguments):
    result=api.call("workflow_step",{"workflow_id":ident,"tool":tool,"arguments":arguments})
    if not result["ok"] or not result["result"]["response"]["ok"]:
        raise RuntimeError(result)
    return result["result"]["response"]["result"]

step("discover_capabilities",{})
step("get_context",{"task":"Review camera framing and delayed reaction timing","max_chars":5000})
snapshot=step("inspect_project",{"project_id":"discovery-revised","frame":100})
preview=step("preview",{"project_id":"discovery-revised"})
step("inspect_artifact",{"project_id":"discovery-revised","job_id":preview["job_id"],"frame":100})
review=step("record_review",{"project_id":"discovery-revised","expected_revision":snapshot["revision"],"accepted":True,"notes":args.review_notes,"reviewer":args.reviewer})
final=step("render_final",{"project_id":"discovery-revised"})
step("inspect_artifact",{"project_id":"discovery-revised","job_id":final["job_id"]})
finished=api.call("finish_workflow",{"workflow_id":ident,"outcome":"complete","summary":"Exported an inspected authored 2D example with source, frames and recorded limitations; this is an implementation demo, not an independent LLM comparison."})
if not finished["ok"]: raise RuntimeError(finished)
destination=ROOT/"examples"/"golden"/"discovery-final"
destination.mkdir(parents=True,exist_ok=True)
folder=Path(final["manifest_path"]).parent
for name in ("video.mp4","contact-sheet.png","scene.json","manifest.json","trace.json","sound.wav"):
    shutil.copy2(folder/name,destination/name)
public_final=dict(final)
for key,name in (("manifest_path","manifest.json"),("video_path","video.mp4"),("contact_sheet_path","contact-sheet.png")):
    public_final[key]=(destination/name).relative_to(ROOT).as_posix()
(ROOT/"examples"/"golden"/"visual-review.json").write_text(json.dumps({"review":review,"workflow_id":ident,"final":public_final},indent=2)+"\n",encoding="utf-8")
print(json.dumps({"workflow_id":ident,"final_video":str(destination/"video.mp4"),"editable_source":str(destination/"scene.json")},indent=2))
