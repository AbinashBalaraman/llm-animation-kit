"""Strict document decoding and semantic validation for the shipped 2D backend."""
from __future__ import annotations

import json
import math
from pathlib import Path
from importlib.resources import files
from jsonschema import Draft202012Validator

DATA = files("animation_kit").joinpath("data")


class KitError(Exception):
    def __init__(self, code, message, pointer="", hint=""):
        super().__init__(message)
        self.code, self.pointer, self.hint = code, pointer, hint

    def as_dict(self):
        return {"code": self.code, "message": str(self), "pointer": self.pointer, "repair_hint": self.hint}


def _unique_pairs(pairs):
    result = {}
    for key, value in pairs:
        if key in result:
            raise KitError("duplicate_key", f"Duplicate JSON key: {key}")
        result[key] = value
    return result


def loads(text):
    def reject_constant(value):
        raise KitError("nonfinite", f"Invalid JSON number: {value}")
    def finite_float(value):
        result=float(value)
        if not math.isfinite(result): reject_constant(value)
        return result
    try:
        return json.loads(text, object_pairs_hook=_unique_pairs, parse_constant=reject_constant,parse_float=finite_float)
    except json.JSONDecodeError as exc:
        raise KitError("invalid_json", str(exc)) from exc


def read_json(path):
    return loads(Path(path).read_text(encoding="utf-8"))


def packaged_json(name):
    return loads(DATA.joinpath(name).read_text(encoding="utf-8"))


def validate(scene):
    issues = []
    try:
        json.dumps(scene,allow_nan=False)
    except (ValueError,TypeError):
        return {"valid":False,"issues":[{"code":"non_json","pointer":"/","message":"Scene must contain finite JSON values.","repair_hint":"Remove nonfinite numbers and non-JSON values."}]}
    is_story = isinstance(scene,dict) and scene.get("schema_version") == "kit.story/2.0"
    schema = packaged_json("story.schema.json" if is_story else "scene.schema.json")
    for error in sorted(Draft202012Validator(schema).iter_errors(scene), key=lambda e: str(e.path)):
        pointer = "/" + "/".join(str(p).replace("~", "~0").replace("/", "~1") for p in error.path)
        issues.append({"code": "schema", "pointer": pointer, "message": error.message,
                       "repair_hint": "Use discover_capabilities and the exact scene schema."})
    if issues:
        return {"valid": False, "issues": issues}
    if is_story:
        from .story import validate_semantics
        issues = validate_semantics(scene)
        return {"valid": not issues, "issues": issues}
    entities = scene["actors"] + scene["props"]
    ids = [e["id"] for e in entities]
    action_ids = [a["id"] for a in scene["actions"]]
    if len(set(ids)) != len(ids) or len(set(action_ids)) != len(action_ids):
        issues.append({"code": "duplicate_id", "pointer": "/", "message": "Entity/action IDs must be unique.", "repair_hint": "Rename conflicting IDs and their references."})
    actor_ids = {e["id"] for e in scene["actors"]}
    entity_ids = set(ids)
    intervals = {}
    channels = {"move_to": "root", "look_at": "gaze", "gesture": "arms", "expression": "face"}
    for i, action in enumerate(scene["actions"]):
        ptr = f"/actions/{i}"
        def issue(code, msg, hint):
            issues.append({"code": code, "pointer": ptr, "message": msg, "repair_hint": hint})
        if action["actor"] not in actor_ids:
            issue("missing_actor", f"Unknown actor {action['actor']}", "Use an existing actor ID.")
        if action["start"] >= action["end"] or action["end"] > scene["frames"]:
            issue("timing", "Action needs 0 <= start < end <= scene frames.", "Retiming must keep actions inside the scene.")
        if action["type"] == "look_at" and action["target"] not in entity_ids:
            issue("missing_target", f"Unknown gaze target {action['target']}", "Select an installed entity or create the prop first.")
        if action["type"] == "move_to":
            actor = next((x for x in scene["actors"] if x["id"] == action["actor"]), None)
            if actor and abs(action["x"] - actor["x"]) / max(1, action["end"] - action["start"]) > 6:
                issue("speed", "Move is too fast for the supported walk controller.", "Allow more frames or reduce distance; do not silently teleport.")
        key = (action["actor"], channels[action["type"]])
        for start, end, other_id in intervals.get(key, []):
            if max(start, action["start"]) < min(end, action["end"]):
                issue("channel_conflict", f"Overlaps {other_id} on {key[1]}", "Sequence actions on the same channel; different channels may overlap.")
        intervals.setdefault(key, []).append((action["start"], action["end"], action["id"]))
    for i, shot in enumerate(scene["shots"]):
        if shot["start"] >= shot["end"] or shot["end"] > scene["frames"]:
            issues.append({"code": "shot_timing", "pointer": f"/shots/{i}", "message": "Invalid shot interval.", "repair_hint": "Shots must partition [0, frames)."})
    ordered = sorted(scene["shots"], key=lambda s: s["start"])
    if not ordered or ordered[0]["start"] != 0 or ordered[-1]["end"] != scene["frames"] or any(a["end"] != b["start"] for a, b in zip(ordered, ordered[1:])):
        issues.append({"code": "shot_coverage", "pointer": "/shots", "message": "Shots must cover every frame exactly once.", "repair_hint": "Remove gaps/overlaps; use half-open intervals."})
    if len({s["id"] for s in ordered}) != len(ordered):
        issues.append({"code": "duplicate_shot", "pointer": "/shots", "message": "Shot IDs must be unique.", "repair_hint": "Assign stable unique shot IDs."})
    return {"valid": not issues, "issues": issues}


def require_valid(scene):
    report = validate(scene)
    if not report["valid"]:
        raise KitError("invalid_scene", json.dumps(report), hint="Run validate_proposal and fix the located issues.")
    return scene
