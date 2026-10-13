"""Provider-independent bounded loop. Hosts supply their model through this interface."""
from __future__ import annotations
from typing import Protocol
import json

from .contracts import KitError


class Provider(Protocol):
    def decide(self,context:dict)->dict:
        """Return {tool,arguments} or {finish,summary}. No executable model code."""


def run_agent(provider:Provider,api,brief,max_calls=24,max_previews=3,max_context_chars=32000):
    started=api.call("start_workflow",{"brief":brief,"max_calls":max_calls,"max_previews":max_previews})
    if not started["ok"]:
        return started
    workflow=started["result"]
    recipes=api.call("get_context",{"task":brief,"max_chars":5000})
    history=[]
    for turn in range(max_calls):
        context={"brief":brief,"knowledge":recipes,"tools":[tool for tool in api.definitions if tool["name"] not in ("start_workflow","workflow_step","finish_workflow")],"history":history[-3:],"remaining_calls":max_calls-turn,
                 "workflow_id":workflow["workflow_id"],"constraints":"Author a kit.story/2.0 document preserving the original brief. Invent needed vector assets and motion; never substitute a demo. Read get_schema. No video-generation models. Review each requirement against actual preview frames, and disclose playback/visual access."}
        while len(json.dumps(context))>max_context_chars and context["history"]:
            context["history"].pop(0)
        if len(json.dumps(context))>max_context_chars:
            return api.call("finish_workflow",{"workflow_id":workflow["workflow_id"],"outcome":"budget_exhausted","summary":"Declared context budget cannot fit the required tool schemas/knowledge. Increase the budget or use a host that manages tool context."})
        decision=None
        try:
            decision=provider.decide(context)
            if not isinstance(decision,dict):
                raise KitError("provider_format","Provider must return a JSON decision object.")
            if "finish" in decision:
                result=api.call("finish_workflow",{"workflow_id":workflow["workflow_id"],"outcome":decision["finish"],"summary":decision.get("summary","")})
                if result["ok"]:
                    return result
            else:
                result=api.call("workflow_step",{"workflow_id":workflow["workflow_id"],"tool":decision.get("tool",""),"arguments":decision.get("arguments",{})})
        except Exception as exc:
            result={"ok":False,"error":{"code":"provider_failure","message":str(exc)}}
        history.append({"decision":decision,"result":result})
    return api.call("finish_workflow",{"workflow_id":workflow["workflow_id"],"outcome":"budget_exhausted","summary":"Agent iteration limit reached. Inspect recorded history and retain valid project versions."})
