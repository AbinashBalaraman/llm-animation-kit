"""Reproducible production through shared tools, with a real review boundary.

prepare renders evidence. finish consumes a review authored AFTER inspection.
This utility never creates visual approval on the reviewer's behalf.
"""
import argparse
import shutil
from pathlib import Path
from animation_kit.contracts import read_json
from animation_kit.store import atomic_json
from animation_kit.tools import Tools


def checked(result):
    if not result["ok"]: raise RuntimeError(str(result["error"]))
    return result["result"]


def main():
    parser=argparse.ArgumentParser()
    sub=parser.add_subparsers(dest="command",required=True)
    prepare=sub.add_parser("prepare")
    prepare.add_argument("--scene",required=True);prepare.add_argument("--project",required=True)
    prepare.add_argument("--workspace",default=".kit-workspace/productions")
    finish=sub.add_parser("finish")
    finish.add_argument("--run",required=True);finish.add_argument("--review",required=True);finish.add_argument("--output",required=True)
    args=parser.parse_args()
    if args.command=="prepare":
        api=Tools(args.workspace);scene=read_json(args.scene)
        workflow=checked(api.call("start_workflow",{"brief":scene["brief"]["prompt"],"max_calls":36,"max_previews":8}))
        ident=workflow["workflow_id"]
        def call(tool,arguments): return checked(checked(api.call("workflow_step",{"workflow_id":ident,"tool":tool,"arguments":arguments}))["response"])
        planned=call("plan_story",{"plan":scene.get("direction",{})})
        if not planned["ready_for_storyboard"]: raise RuntimeError("Resolve the writing plan before rendering: "+str(planned["issues"]))
        call("create_project",{"project_id":args.project,"scene":scene})
        diagnostic=call("check_story",{"project_id":args.project})
        if not diagnostic["passed"]: raise RuntimeError("Storyboard evidence is invisible: "+str(diagnostic))
        sheet=call("preview_frames",{"project_id":args.project})
        print("Storyboard:",sheet["image_path"],flush=True)
        preview=call("preview",{"project_id":args.project})
        run={"workspace":str(api.store.root),"workflow_id":ident,"project_id":args.project,"preview":preview}
        location=api.store.project(args.project)/"production-run.json"
        atomic_json(location,run)
        print("Preview:",preview["video_path"],flush=True)
        print("Run:",location,flush=True)
        print("Inspect the clip and frames; write a truthful review_story payload, then use finish.")
    else:
        run=read_json(args.run);api=Tools(run["workspace"]);ident=run["workflow_id"]
        def call(tool,arguments): return checked(checked(api.call("workflow_step",{"workflow_id":ident,"tool":tool,"arguments":arguments}))["response"])
        submitted=read_json(args.review)
        # The run supplies identity; a review file cannot redirect another project.
        snapshot=api.store.load(run["project_id"])
        review=call("review_story",dict(submitted,project_id=run["project_id"],expected_revision=snapshot["revision"],preview_job_id=run["preview"]["job_id"]))
        if not review["accepted"]: raise RuntimeError("Review rejected; revise before final delivery.")
        final=call("render_final",{"project_id":run["project_id"]})
        checked(api.call("finish_workflow",{"workflow_id":ident,"outcome":"complete","summary":"Exported the authored story with per-requirement evidence. Review scope: "+("playback" if review["playback_reviewed"] else "sampled frames; motion/audio playback remains unassessed")+"."}))
        output=Path(args.output);output.mkdir(parents=True,exist_ok=True)
        folder=Path(final["manifest_path"]).parent
        for name in final["artifacts"]:
            if name!="trace.json": shutil.copyfile(folder/name,output/name)
        # Portable publication manifest: original frame hashes/trace stay in the render workspace.
        record={k:v for k,v in final.items() if k not in ("manifest_path","video_path","contact_sheet_path")}
        record["artifacts"]={k:v for k,v in final["artifacts"].items() if k!="trace.json"}
        record["review_scope"]="playback" if review["playback_reviewed"] else "sampled_frames"
        atomic_json(output/"manifest.json",record);atomic_json(output/"review.json",review)
        from animation_kit.direction import as_markdown
        plan=snapshot["scene"]["direction"]
        atomic_json(output/"direction.json",plan)
        (output/"story.md").write_text(as_markdown(plan),encoding="utf-8",newline="\n")
        print((output/"video.mp4").resolve())


if __name__=="__main__": main()
