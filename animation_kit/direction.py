"""A portable, inspectable writing/directing plan, separate from drawing geometry.

The host LLM writes and revises the answers. Structural validation cannot judge
whether its story is good, its answers truthful, or its acting understandable.
"""
import hashlib
import json
from jsonschema import Draft202012Validator
from .story_schema import obj, arr, ID

PROSE={"type":"string","minLength":12,"maxLength":3000}
SELF_CHECKS=("motivation","causality","stakes","clarity","ending","filmability")
PLAN_SCHEMA=obj({
    "schema_version":{"const":"kit.direction/1.0"},
    "brief":{"type":"string","minLength":1,"maxLength":3000},
    "mode":{"enum":["narrative","explainer","abstract"]},
    "premise":PROSE,
    "answers":obj({key:PROSE for key in ("who","what","when","where","why","how")}),
    "story_text":{"type":"string","minLength":120,"maxLength":12000},
    "beats":arr(obj({"id":ID,"role":{"enum":["setup","inciting_event","attempt","turn","resolution","explanation","transition"]},
                     "cause":PROSE,"visible_action":PROSE,"change":PROSE}),1,40),
    "shots":arr(obj({"id":ID,"beats":arr(ID,1,12),"seconds":{"type":"number","exclusiveMinimum":0,"maximum":120},
                     "framing":PROSE,"action":PROSE,"reaction":PROSE,"continuity_in":PROSE,"continuity_out":PROSE,
                     "dialogue": {"type":"string","maxLength":2000}}),1,40),
    "self_review":arr(obj({"focus":{"enum":list(SELF_CHECKS)},"question":PROSE,"answer":PROSE,
                           "verdict":{"enum":["pass","revise","not_applicable"]},
                           "revision": {"type":"string","maxLength":3000}}),6,12)
})


def inspect_plan(plan):
    issues=[{"code":"plan_schema","pointer":"/"+"/".join(map(str,e.path)),"message":e.message}
            for e in Draft202012Validator(PLAN_SCHEMA).iter_errors(plan)]
    if not issues:
        def issue(code,message): issues.append({"code":code,"pointer":"","message":message})
        beat_ids=[b["id"] for b in plan["beats"]]; shot_ids=[s["id"] for s in plan["shots"]]
        if len(set(beat_ids))!=len(beat_ids) or len(set(shot_ids))!=len(shot_ids): issue("plan_ids","Beat and shot IDs must each be unique.")
        assigned={b for s in plan["shots"] for b in s["beats"]}
        if assigned!=set(beat_ids): issue("plan_coverage","Every story beat must appear in the shot list; no unknown beat references.")
        if sum(s["seconds"] for s in plan["shots"])>120: issue("plan_duration","Planned runtime exceeds the current 120-second backend limit.")
        if {r["focus"] for r in plan["self_review"]}!=set(SELF_CHECKS): issue("plan_questions","Self-question all six story checks before drawing.")
        if any(r["verdict"]=="revise" for r in plan["self_review"]): issue("unresolved_story","Rewrite the story and affected shots, then reassess unresolved self-questions.")
        if plan["mode"]=="narrative":
            if not {"setup","turn","resolution"} <= {b["role"] for b in plan["beats"]}:
                issue("story_structure","A narrative needs a setup, a meaningful turn, and a resolution.")
            if any(r["verdict"]=="not_applicable" for r in plan["self_review"]):
                issue("story_question_skipped","For a narrative, answer every story check; stakes can be small and personal.")
    return {"ready_for_storyboard":not issues,"issues":issues,
            "plan_hash":hashlib.sha256(json.dumps(plan,sort_keys=True,separators=(",",":"),allow_nan=False).encode()).hexdigest(),
            "semantic_quality_verified":False,
            "meaning":"These are structural checks on the host's written plan. Read the story and challenge its answers; the tool does not write or approve creative quality."}


def scene_plan_issues(scene):
    plan=scene.get("direction")
    if plan is None: return [{"code":"plan_required","pointer":"/direction","message":"Write who/what/when/where/why/how, a complete story, causal beats, a shot script and a self-review before artwork."}]
    result=inspect_plan(plan);issues=result["issues"][:]
    if issues: return issues
    if plan["brief"]!=scene.get("brief",{}).get("prompt"):
        issues.append({"code":"plan_brief","pointer":"/direction/brief","message":"The writing plan must preserve the exact original prompt."})
    expected=[(s["id"],round(s["seconds"]*scene.get("fps",24))) for s in plan["shots"]]
    actual=[(s.get("id"),s.get("end",0)-s.get("start",0)) for s in scene.get("shots",[])]
    if actual!=expected:
        issues.append({"code":"plan_shots","pointer":"/direction/shots","message":"Ordered shot IDs and durations must match the written shot script. Revise the plan when the edit changes."})
    return issues


def as_markdown(plan):
    """Make the authored story and script easy for a person to read alongside MP4."""
    lines=["# Story and directing plan", "", plan["premise"], "", "## Story", "", plan["story_text"], "", "## Who, what, when, where, why and how", ""]
    for key,value in plan["answers"].items(): lines.extend([f"**{key.capitalize()}:** {value}", ""])
    lines.extend(["## Shot script", ""])
    for shot in plan["shots"]:
        lines.extend([f"### {shot['id']} — {shot['seconds']:g} seconds", ""])
        for key in ("framing","action","reaction","continuity_in","continuity_out","dialogue"):
            if shot[key]: lines.extend([f"**{key.replace('_',' ').capitalize()}:** {shot[key]}", ""])
    lines.extend(["## Writer's self-review", ""])
    for check in plan["self_review"]:
        lines.extend([f"**{check['focus'].capitalize()}: {check['question']}**", "", check["answer"], ""])
        if check["revision"]: lines.extend(["Revision: "+check["revision"], ""])
    lines.extend(["These are authored production notes. Structural validation and self-review do not independently establish story or animation quality.", ""])
    return "\n".join(lines)
