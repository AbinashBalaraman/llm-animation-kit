"""One shared tool surface for CLI, MCP and provider-independent agent loops."""
from __future__ import annotations

import json
import re
import time
import uuid
from pathlib import Path

from jsonschema import Draft202012Validator

from .components import evaluate
from .contracts import KitError, packaged_json, read_json, validate
from .render import artifact_valid, render
from .store import Store, atomic_json


class Tools:
    def __init__(self,workspace):
        self.store=Store(workspace)
        self.definitions=packaged_json("tools.json")
        self.by_name={t["name"]:t for t in self.definitions}

    def call(self,name,arguments):
        started=time.monotonic()
        try:
            try:
                json.dumps(arguments,allow_nan=False)
            except (ValueError,TypeError) as exc:
                raise KitError("non_json_arguments","Arguments must be finite JSON values.") from exc
            if name not in self.by_name:
                raise KitError("unknown_tool",f"Unknown tool: {name}",hint="Discover available tools.")
            errors=list(Draft202012Validator(self.by_name[name]["inputSchema"]).iter_errors(arguments))
            if errors:
                error=errors[0]
                raise KitError("tool_arguments",error.message,"/"+"/".join(str(p) for p in error.path),"Use the exact tool input schema.")
            result=getattr(self,name)(**arguments)
            response={"ok":True,"result":result}
        except KitError as exc:
            response={"ok":False,"error":exc.as_dict()}
        except Exception as exc:
            response={"ok":False,"error":{"code":"internal_error","message":str(exc),"pointer":"","repair_hint":"Inspect logs; do not assume the operation completed."}}
        # No provider secrets are accepted by these tool schemas.
        with (self.store.root/"audit.jsonl").open("a",encoding="utf-8") as stream:
            safe_arguments=arguments
            try:
                json.dumps(arguments,allow_nan=False)
            except (ValueError,TypeError):
                safe_arguments={"rejected":"non-JSON arguments"}
            stream.write(json.dumps({"time":time.time(),"tool":name,"arguments":safe_arguments,"ok":response["ok"],"seconds":round(time.monotonic()-started,3)},allow_nan=False)+"\n")
        return response

    def discover_capabilities(self):
        return dict(packaged_json("capabilities.json"),tools=[{"name":t["name"],"description":t["description"]} for t in self.definitions],
                    scene_schema=packaged_json("scene.schema.json"),workspace=str(self.store.root))

    def get_context(self,task,max_chars=9000):
        from .contracts import DATA
        words=set(re.findall(r"[a-z]+",task.lower()))
        recipes=[read_json(Path(str(p))) for p in DATA.joinpath("recipes").iterdir() if p.name.endswith(".json")]
        ranked=sorted(recipes,key=lambda r:(-len(words.intersection(r["keywords"])),r["id"]))
        if not any(words.intersection(r["keywords"]) for r in ranked):
            ranked=sorted(recipes,key=lambda r:r["id"]!="staging")
        entry={"workflow":"Discover -> inspect -> propose/validate -> apply -> preview -> inspect temporal evidence -> focused repair -> review -> final export.",
               "rules":["Use installed capabilities only; no generated video pixels or arbitrary Python.","Inspect revision before editing; preserve unaffected actions.","Model/technical review is not independent proof of aesthetic quality.","Use workflow_step for bounded tool calls; all errors consume budget."],
               "recipes":[],"example":None,"scene_schema_tool":"discover_capabilities","tool_schema_source":"MCP tools/list or CLI tools",
               "missing_capabilities":packaged_json("capabilities.json")["limitations"]}
        for recipe in ranked:
            candidate=dict(entry,recipes=entry["recipes"]+[recipe])
            if len(json.dumps(candidate))>max_chars-100:
                break
            entry=candidate
        if entry["recipes"]:
            example_id=entry["recipes"][0]["example"]
            example=packaged_json(f"examples/{example_id}.json")
            candidate=dict(entry,example={"id":example_id,"scene":example,"status":"editable authored example; visual verification recorded separately in examples/golden"})
            if len(json.dumps(candidate))<=max_chars-100:
                entry=candidate
        entry["characters"]=len(json.dumps(entry))
        entry["token_estimate"]=round(entry["characters"]/4)
        return entry

    def create_project(self,project_id,scene):
        return dict(self.store.create(project_id,scene),project_id=project_id)

    def load_example(self,project_id,example_id):
        return self.create_project(project_id,packaged_json(f"examples/{example_id}.json"))

    def inspect_project(self,project_id,frame=0):
        snapshot=self.store.load(project_id)
        scene=snapshot["scene"]
        if frame>=scene["frames"]:
            raise KitError("frame_range","Requested frame is outside this scene.")
        return dict(snapshot,evaluated=evaluate(scene,frame),duration_seconds=scene["frames"]/scene["fps"])

    def validate_proposal(self,scene):
        return validate(scene)

    def apply_revision(self,project_id,expected_revision,operations):
        return self.store.revise(project_id,expected_revision,operations)

    def undo(self,project_id,expected_revision,target_revision):
        return self.store.undo(project_id,expected_revision,target_revision)

    def preview(self,project_id):
        return self._render_summary(render(self.store,project_id,"preview"))

    @staticmethod
    def _render_summary(manifest):
        # Detailed per-frame digests remain on disk; sending them wastes model context.
        return {key:value for key,value in manifest.items() if key!="frames"}

    def inspect_artifact(self,project_id,job_id,frame=None,include_image=False):
        folder=(self.store.project(project_id)/"renders"/job_id).resolve()
        if not folder.is_relative_to(self.store.root):
            raise KitError("path_escape","Artifact path escapes workspace.")
        try:
            manifest=read_json(folder/"manifest.json")
        except FileNotFoundError as exc:
            raise KitError("missing_job","Unknown render job.") from exc
        if manifest["status"]!="succeeded":
            return {"manifest":manifest,"image_path":None,"review_required":True}
        for name,sha in manifest["artifacts"].items():
            artifact=(folder/name).resolve()
            if not artifact.is_relative_to(folder) or not artifact_valid(artifact,sha):
                raise KitError("corrupt_artifact",f"Artifact failed integrity check: {name}")
        image_path=folder/"contact-sheet.png"
        if frame is not None:
            if frame>=manifest["frame_count"]:
                raise KitError("frame_range","Frame lies outside rendered scene.")
            name=f"{frame:06d}.png"
            image_path=folder/"frames"/name
            if not artifact_valid(image_path,manifest["frames"][name]):
                raise KitError("corrupt_frame","Frame is missing/modified; rerun preview.")
        return {"manifest":self._render_summary(manifest),"video_path":str(folder/"video.mp4"),"source_path":str(folder/"scene.json"),
                "contact_sheet_path":str(folder/"contact-sheet.png"),"image_path":str(image_path) if include_image else None,
                "review_required":True,"review_note":"Inspect temporal evidence; diagnostics certify neither appeal nor exact human interpretation."}

    def record_review(self,project_id,expected_revision,accepted,notes,reviewer):
        with self.store.lock(project_id) as path:
            snapshot=self.store.load(project_id)
            if snapshot["revision"]!=expected_revision:
                raise KitError("stale_revision","Review refers to an outdated revision.")
            review={"revision":expected_revision,"scene_hash":snapshot["scene_hash"],"accepted":accepted,"notes":notes,"reviewer":reviewer,"time":time.time(),
                    "independent_quality_proof":False}
            atomic_json(path/"review.json",review)
            return review

    def render_final(self,project_id):
        snapshot=self.store.load(project_id)
        path=self.store.project(project_id)/"review.json"
        if not path.exists():
            raise KitError("review_required","Inspect a preview and record an explicit review before final export.")
        review=read_json(path)
        if not review["accepted"] or review["scene_hash"]!=snapshot["scene_hash"]:
            raise KitError("review_required","Current revision has no accepted review.")
        return self._render_summary(render(self.store,project_id,"final",expected_scene_hash=snapshot["scene_hash"]))

    def start_workflow(self,brief,max_calls=24,max_previews=3):
        ident=uuid.uuid4().hex[:16]
        with self.store.lock("workflow-"+ident) as path:
            state={"workflow_id":ident,"brief":brief,"max_calls":max_calls,"max_previews":max_previews,"calls":0,"previews":0,"status":"active","history":[]}
            atomic_json(path/"workflow.json",state)
        return state

    def workflow_step(self,workflow_id,tool,arguments):
        if tool in ("start_workflow","workflow_step","finish_workflow"):
            raise KitError("recursive_workflow","Workflow control tools cannot be nested.")
        with self.store.lock("workflow-"+workflow_id) as path:
            state_path=path/"workflow.json"
            if not state_path.exists():
                raise KitError("unknown_workflow","Start a workflow first.")
            state=read_json(state_path)
            if state["status"]!="active":
                raise KitError("workflow_closed","Workflow has already ended.")
            if state["calls"]>=state["max_calls"]:
                raise KitError("budget_exhausted","Tool-call budget exhausted; finish the workflow.")
            if tool in ("preview","render_final") and state["previews"]>=state["max_previews"]:
                raise KitError("budget_exhausted","Render-attempt budget exhausted; finish or request a new budget.")
            state["calls"]+=1
            if tool in ("preview","render_final"):
                state["previews"]+=1
            # Reserve before execution so crashes do not reset the budget.
            atomic_json(state_path,state)
            response=self.call(tool,arguments)
            state["history"].append({"tool":tool,"arguments":arguments,"response":response})
            atomic_json(state_path,state)
            return {"response":response,"remaining_calls":state["max_calls"]-state["calls"],"remaining_renders":state["max_previews"]-state["previews"]}

    def finish_workflow(self,workflow_id,outcome,summary):
        with self.store.lock("workflow-"+workflow_id) as path:
            if not (path/"workflow.json").exists():
                raise KitError("unknown_workflow","Start a workflow first.")
            state=read_json(path/"workflow.json")
            if state["status"]!="active":
                raise KitError("workflow_closed","Workflow has already ended.")
            if outcome=="complete":
                finals=[h for h in state["history"] if h["tool"]=="render_final" and h["response"]["ok"]]
                if not finals:
                    raise KitError("missing_evidence","Complete requires a successful final export in this workflow.")
                final=finals[-1]
                snapshot=self.store.load(final["arguments"]["project_id"])
                if snapshot["scene_hash"]!=final["response"]["result"]["scene_hash"]:
                    raise KitError("stale_export","Current project differs from the final export.")
            state.update(status=outcome,summary=summary)
            atomic_json(path/"workflow.json",state)
            return state
