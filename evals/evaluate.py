"""Collect an actual agent workflow and score annotated technical checks only."""
from __future__ import annotations
import argparse
import hashlib
import json
from pathlib import Path
import sys

ROOT=Path(__file__).resolve().parents[1]
sys.path.insert(0,str(ROOT))
from animation_kit.contracts import read_json, KitError
from animation_kit.store import Store, atomic_json


def check(scene,predicate):
    kind=predicate["kind"]
    if kind=="action":
        requested={k:v for k,v in predicate.items() if k!="kind"}
        return any(all(a.get(k)==v for k,v in requested.items()) for a in scene["actions"])
    if kind=="prop":
        return any(p["kind"]==predicate["prop_kind"] and p["x"]<=predicate.get("max_x",960) for p in scene["props"])
    if kind=="actor_count": return len(scene["actors"])==predicate["value"]
    if kind=="shot_count": return len(scene["shots"])==predicate["value"]
    if kind=="camera_zoom": return any(abs(s["camera"]["zoom"]-predicate["value"])<1e-8 for s in scene["shots"])
    raise ValueError(f"Unknown benchmark predicate: {kind}")


def collect(workspace,workflow_id,task_id,condition,model,human_minutes,ratings=None):
    if len(workflow_id)!=16 or any(c not in "0123456789abcdef" for c in workflow_id):
        raise ValueError("Invalid workflow ID")
    task=next((t for t in read_json(ROOT/"evals"/"heldout.json") if t["id"]==task_id),None)
    if task is None: raise ValueError("Unknown task ID")
    store=Store(workspace)
    state=read_json(store.project("workflow-"+workflow_id)/"workflow.json")
    finals=[h for h in state["history"] if h["tool"]=="render_final" and h["response"]["ok"]]
    checks=[]
    artifact=None
    if finals:
        final=finals[-1]
        project=final["arguments"]["project_id"]
        snapshot=store.load(project)
        artifact=final["response"]["result"]
        checks=[{"predicate":p,"passed":check(snapshot["scene"],p)} for p in task["checks"]]
        checks.append({"predicate":{"kind":"matches_final_export"},"passed":snapshot["scene_hash"]==artifact["scene_hash"]})
    elif task.get("expected_outcome")=="unsupported":
        checks=[{"predicate":{"kind":"unsupported_report"},"passed":state["status"]=="unsupported"}]
    else:
        checks=[{"predicate":{"kind":"final_export"},"passed":False}]
    if ratings:
        expected={"appeal","acting_clarity","staging","revision_correctness"}
        if set(ratings)!=expected or any(not isinstance(v,int) or not 1<=v<=5 for v in ratings.values()):
            raise ValueError("Human ratings need appeal, acting_clarity, staging, revision_correctness, each integer 1–5")
    render_attempts=[h for h in state["history"] if h["tool"] in ("preview","render_final")]
    record={"task":task_id,"condition":condition,"model":model,"workflow_id":workflow_id,"workflow_status":state["status"],
            "annotated_checks":checks,"annotated_checks_passed":all(x["passed"] for x in checks),"human_ratings":ratings,
            "human_minutes":human_minutes,"tool_calls":state["calls"],"render_attempts":len(render_attempts),
            "tool_failures":sum(not h["response"]["ok"] for h in state["history"]),
            "render_seconds":sum(h["response"].get("result",{}).get("seconds",0) for h in render_attempts if not h["response"].get("result",{}).get("cached")),
            "artifact":artifact,"kit_version":"0.1.0","human_review_required":ratings is None,
            "limitations":["Annotated checks cover only part of the brief","Aesthetic equivalence is not inferred","Model token/spend values need provider-side accounting"]}
    return record


def main():
    parser=argparse.ArgumentParser()
    parser.add_argument("--workspace",required=True)
    parser.add_argument("--workflow-id",required=True)
    parser.add_argument("--task",required=True)
    parser.add_argument("--condition",choices=("stronger-full","other-full","other-basic"),required=True)
    parser.add_argument("--model",required=True)
    parser.add_argument("--human-minutes",type=float,required=True)
    parser.add_argument("--ratings",help="Optional JSON file of independently assigned visual ratings")
    parser.add_argument("--out",required=True)
    args=parser.parse_args()
    if args.human_minutes<0: parser.error("Human minutes cannot be negative")
    record=collect(args.workspace,args.workflow_id,args.task,args.condition,args.model,args.human_minutes,read_json(args.ratings) if args.ratings else None)
    atomic_json(args.out,record)
    print(json.dumps(record,indent=2))

if __name__=="__main__": main()
