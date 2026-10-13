"""Collect actual production evidence; do not turn declared review into a quality score."""
import argparse
import json
from pathlib import Path
from animation_kit.contracts import read_json
from animation_kit.tools import Tools


def collect(workspace, workflow_id, model, human_assistance=0):
    api=Tools(workspace)
    run=read_json(api.store.project("workflow-"+workflow_id)/"workflow.json")
    finals=[h for h in run["history"] if h["tool"]=="render_final" and h["response"]["ok"]]
    result={"workflow_id":workflow_id,"model_label":model,"brief":run["brief"],"outcome":run["status"],
            "human_assistance_count":human_assistance,"calls":run["calls"],"render_attempts":run["previews"],
            "failures":[h["response"]["error"] for h in run["history"] if not h["response"]["ok"]],
            "verified_current_export":False,"artifact":None,"declared_review":None,
            "independent_semantic_quality":None,"model_parity_established":False}
    if not finals: return result
    final=finals[-1];project=final["arguments"]["project_id"]
    snapshot=api.store.load(project)
    manifest=api.inspect_artifact(project,final["response"]["result"]["job_id"])["manifest"]
    review=read_json(api.store.project(project)/"review.json")
    result.update(verified_current_export=(run["status"]=="complete" and snapshot["scene"].get("schema_version")=="kit.story/2.0"
                  and snapshot["scene"]["brief"]["prompt"]==run["brief"] and snapshot["scene_hash"]==manifest["scene_hash"]==review["scene_hash"]
                  and review["accepted"]),artifact=final["response"]["result"]["video_path"],declared_review=review,
                  export_seconds=manifest["seconds"],frame_count=manifest["frame_count"])
    return result


if __name__=="__main__":
    parser=argparse.ArgumentParser();parser.add_argument("--workspace",required=True);parser.add_argument("--workflow",required=True)
    parser.add_argument("--model",required=True);parser.add_argument("--human-assistance",type=int,default=0);parser.add_argument("--output",required=True)
    args=parser.parse_args();result=collect(args.workspace,args.workflow,args.model,args.human_assistance)
    Path(args.output).write_text(json.dumps(result,indent=2)+"\n",encoding="utf-8")
