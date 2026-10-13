"""Brief coverage checks and source-bound declared visual review. No semantic oracle."""
from pathlib import Path
from .contracts import KitError, read_json
from .story import evaluate, visible_evidence
from .store import atomic_json


def preflight(scene):
    checks=[]
    for beat in scene["beats"]:
        state=evaluate(scene,beat["frame"])
        visible=[n for n in beat["nodes"] if visible_evidence(state,n)]
        checks.append({"beat":beat["id"],"frame":beat["frame"],"requirements":beat["requirements"],
                       "visible_drawing_nodes":visible,"ok":bool(visible)})
    return {"passed":all(c["ok"] for c in checks),"checks":checks,
            "meaning":"Checks geometry visibility and authored coverage only. A reviewer must verify identity, actions, story and comedy in the actual pixels."}


def record(api, project_id, expected_revision, preview_job_id, accepted, reviewer, coverage, playback_reviewed, notes):
    with api.store.lock(project_id) as path:
        snapshot=api.store.load(project_id); scene=snapshot["scene"]
        if scene.get("schema_version")!="kit.story/2.0": raise KitError("story_required","Use record_review for legacy exercises.")
        if snapshot["revision"]!=expected_revision: raise KitError("stale_revision","Review is for an outdated revision.")
        evidence=api.inspect_artifact(project_id,preview_job_id)
        manifest=evidence["manifest"]
        if manifest["status"]!="succeeded" or manifest["scene_hash"]!=snapshot["scene_hash"] or manifest["profile"]!="preview":
            raise KitError("stale_preview","Render and inspect a preview of the current story.")
        wanted={r["id"] for r in scene["brief"]["requirements"]}
        found=[c["requirement_id"] for c in coverage]
        if len(set(found))!=len(found) or set(found)!=wanted:
            raise KitError("review_coverage","Review every brief requirement exactly once.")
        diagnostic=preflight(scene)
        for row in coverage:
            eligible=[b for b in scene["beats"] if row["requirement_id"] in b["requirements"]]
            for frame in row["frames"]:
                if not 0<=frame<scene["frames"]: raise KitError("frame_range","Review cites an out-of-range frame.")
                state=evaluate(scene,frame)
                nodes=[n for b in eligible if b["shot"]==state["shot"] for n in b["nodes"]]
                if row["status"]=="pass" and not any(visible_evidence(state,n) for n in nodes):
                    raise KitError("invisible_evidence","A passed requirement needs visible, non-text drawing evidence in its declared story beat.")
                # Verify the actual cited frame, not just the source declaration.
                api.inspect_artifact(project_id,preview_job_id,frame=frame)
        if accepted and (not diagnostic["passed"] or any(c["status"]!="pass" for c in coverage)):
            raise KitError("brief_not_met","Resolve rejected/unreviewed requirements or record this as a rejected review.")
        review={"revision":expected_revision,"scene_hash":snapshot["scene_hash"],"accepted":accepted,
                "preview_job_id":preview_job_id,"preview_engine_hash":manifest["engine_hash"],
                "preview_video_hash":manifest["artifacts"]["video.mp4"],"reviewer":reviewer,
                "coverage":coverage,"playback_reviewed":playback_reviewed,"notes":notes,
                "preflight":diagnostic,"independent_quality_proof":False,
                "limitations":[] if playback_reviewed else ["Sampled-frame review only; normal-speed motion and sound remain unassessed."]}
        atomic_json(path/"review.json",review)
        return review
