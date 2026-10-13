"""Artifact QA only: schema + selected static/symbolic checks, not a studio runtime.

Run: python research/contracts/validate_contracts.py
Requires the already available jsonschema package. Does not download or install.
"""
from pathlib import Path
from copy import deepcopy
from itertools import combinations
import hashlib
import importlib.metadata
import json
import math
import platform
import sys

from jsonschema import Draft202012Validator

ROOT = Path(__file__).resolve().parent
EX = ROOT / "examples"


def read(path):
    def invalid_number(value):
        raise ValueError("Non-finite JSON number: " + value)
    return json.loads(path.read_text(encoding="utf-8"), parse_constant=invalid_number)


SCHEMA = read(ROOT / "studio.schema.json")
VALIDATOR = Draft202012Validator(SCHEMA)
BUNDLE = {p.name: read(p) for p in sorted(EX.glob("*.json"))}
ID_FIELDS = {"characterRef": "characterId", "scene": "sceneId", "shot": "shotId", "action": "actionId"}


def symbolic_errors(scene, actions):
    """Metadata-only event assertions; no spatial/contact solution is claimed."""
    errors = set()
    owners = {x["propId"]: x["ownerId"] for x in scene["initialState"]["ownership"]}
    contacts = {(c["actorId"], c["effector"], c["targetEntityId"], c["affordanceId"]) for c in scene["initialState"]["contacts"]}
    seats = {(s["seatEntityId"], s["seatAffordanceId"]): s["actorId"] for s in scene["initialState"]["seatOccupancy"]}

    def conditions(items):
        for c in items:
            kind = c["conditionType"]
            if kind == "ownership" and owners.get(c["propId"]) != c["ownerId"]:
                errors.add("OWNERSHIP_CONDITION")
            elif kind == "contact":
                key = (c["actorId"], c["effector"], c["targetEntityId"], c["affordanceId"])
                if (key in contacts) != c["active"]:
                    errors.add("CONTACT_CONDITION")
            elif kind == "hand_free" and any(x[0] == c["actorId"] and x[1] == c["hand"] for x in contacts):
                errors.add("HAND_NOT_FREE")
            elif kind == "seated":
                occupied = seats.get((c["seatEntityId"], c["seatAffordanceId"])) == c["actorId"]
                if occupied != c["active"]:
                    errors.add("SEAT_CONDITION")
            # Proximity is intentionally NOT evaluated: no solved actor trajectories.

    events = []
    for a in actions:
        events.extend([(a["frameRange"]["start"], 1, a["actionId"], "pre", a), (a["frameRange"]["end"], 0, a["actionId"], "post", a)])
        p = a["parameters"]
        if a["actionType"] == "handover":
            events.extend([(p["receiverContactFrame"], 2, a["actionId"], "contact", a), (p["transferFrame"], 3, a["actionId"], "transfer", a), (p["giverReleaseFrame"], 4, a["actionId"], "release", a)])
        elif a["actionType"] == "sit":
            events.append((p["seatContactFrame"], 2, a["actionId"], "sit", a))
    for _, _, _, event, a in sorted(events, key=lambda e: e[:3]):
        p = a["parameters"]
        if event in ("pre", "post"):
            conditions(a["preconditions" if event == "pre" else "postconditions"])
        elif event == "contact":
            contacts.add((p["receiverId"], p["receiverHand"], p["propId"], p["receiverGraspAffordanceId"]))
        elif event == "transfer":
            if owners.get(p["propId"]) != a["actorId"]:
                errors.add("OWNERSHIP_CONDITION")
            if (p["receiverId"], p["receiverHand"], p["propId"], p["receiverGraspAffordanceId"]) not in contacts:
                errors.add("TRANSFER_WITHOUT_CONTACT")
            owners[p["propId"]] = p["receiverId"]
        elif event == "release":
            contacts.discard((a["actorId"], p["giverHand"], p["propId"], p["giverGraspAffordanceId"]))
        elif event == "sit":
            key = (p["seatEntityId"], p["seatAffordanceId"])
            if key in seats:
                errors.add("SEAT_OCCUPIED")
            seats[key] = a["actorId"]
    return errors


def selected_semantic_errors(bundle, verify_hashes=True):
    """Subset documented in VALIDATION.md. Input must first pass the schema."""
    errors = set()
    project = bundle["project.json"]
    assets = {a["assetId"]: a for a in project["assets"]}
    if len(assets) != len(project["assets"]): errors.add("DUPLICATE_ASSET_ID")
    if math.gcd(project["fps"]["numerator"], project["fps"]["denominator"]) != 1: errors.add("UNREDUCED_FPS")
    registry = project["documents"]
    if len({d["documentId"] for d in registry}) != len(registry): errors.add("DUPLICATE_DOCUMENT_ID")
    for d in registry:
        loaded = bundle.get(d["path"])
        if not loaded or loaded.get("documentType") != d["documentType"] or loaded.get(ID_FIELDS[d["documentType"]]) != d["documentId"]:
            errors.add("DOCUMENT_REFERENCE")
    for d in bundle.values():
        if d["projectId"] != project["projectId"]: errors.add("PROJECT_REFERENCE")
    for a in assets.values():
        expected_profile = project["selectedRigProfileId"] if a["assetType"] in ("character_rig", "motion_library") else None
        if a["rigProfileId"] != expected_profile: errors.add("ASSET_RIG_PROFILE")
        path = (EX / a["uri"]).resolve()
        if not path.is_relative_to(EX.resolve()):
            errors.add("ASSET_PATH_ESCAPE")
        elif verify_hashes and (not path.is_file() or hashlib.sha256(path.read_bytes()).hexdigest() != a["sha256"]):
            errors.add("ASSET_HASH_MISMATCH")
    for c in (d for d in bundle.values() if d["documentType"] == "characterRef"):
        if assets.get(c["rigAsset"]["assetId"]) != c["rigAsset"]: errors.add("ASSET_REFERENCE_MISMATCH")
        if c["rigAsset"]["assetType"] != "character_rig": errors.add("ASSET_ROLE")
    scenes = {d["sceneId"]: d for d in bundle.values() if d["documentType"] == "scene"}
    shots = {d["shotId"]: d for d in bundle.values() if d["documentType"] == "shot"}
    if set(project["shotOrder"]) - set(shots): errors.add("SHOT_REFERENCE")
    for scene in scenes.values():
        entities = {e["entityId"]: e for e in scene["entities"]}
        if len(entities) != len(scene["entities"]): errors.add("DUPLICATE_ENTITY_ID")
        state = scene["initialState"]
        for field, key, code in [("ownership", "propId", "MULTIPLE_OWNERS"), ("attachments", "propId", "MULTIPLE_ATTACHMENTS")]:
            if len({v[key] for v in state[field]}) != len(state[field]): errors.add(code)
        for o in state["ownership"]:
            if o["propId"] not in entities or (o["ownerId"] is not None and entities.get(o["ownerId"], {}).get("entityType") != "character"):
                errors.add("ENTITY_REFERENCE")
        transforms = [e["transform"] for e in scene["entities"]] + [a["localTransform"] for a in state["attachments"]]
        for t in transforms:
            if abs(sum(v*v for v in t["rotationXyzw"]) - 1) > 1e-6: errors.add("NON_UNIT_QUATERNION")
            if max(t["scale"]) != min(t["scale"]): errors.add("NON_UNIFORM_SCALE")
        for entity in scene["entities"]:
            for affordance in entity.get("affordances", []):
                rotations = [affordance["localRotationXyzw"]]
                rotations += [affordance[k]["rotationXyzw"] for k in ("footZone", "clearanceBox") if k in affordance]
                if any(abs(sum(v*v for v in q)-1) > 1e-6 for q in rotations): errors.add("NON_UNIT_QUATERNION")
        actions = [a for a in bundle.values() if a["documentType"] == "action" and a["sceneId"] == scene["sceneId"]]
        if set(scene["actionIds"]) != {a["actionId"] for a in actions}: errors.add("ACTION_REFERENCE")
        for a in actions:
            fr, p = a["frameRange"], a["parameters"]
            if not 0 <= fr["start"] < fr["end"] <= scene["durationFrames"]: errors.add("FRAME_RANGE")
            if entities.get(a["actorId"], {}).get("entityType") != "character": errors.add("ENTITY_REFERENCE")
            claims = {}
            for c in a["resourceClaims"]:
                if c["entityId"] not in entities: errors.add("ENTITY_REFERENCE")
                claims.setdefault(c["entityId"], set()).update(c["channels"])
            for key in ["targetEntityId", "facingTargetEntityId", "receiverId", "seatEntityId", "propId"]:
                if key in p and p[key] not in entities: errors.add("ENTITY_REFERENCE")
            for key, role in [("motionAssetId", "motion_library"), ("audioAssetId", "audio")]:
                if key in p and assets.get(p[key], {}).get("assetType") != role: errors.add("ASSET_ROLE")
            if a["composition"]["policy"] != "exclusive": errors.add("UNSUPPORTED_COMPATIBILITY_PROFILE")
            kind = a["actionType"]
            if kind == "handover":
                if not fr["start"] <= p["receiverContactFrame"] <= p["transferFrame"] <= p["giverReleaseFrame"] < fr["end"]:
                    errors.add("HANDOVER_EVENT_ORDER")
                if p["receiverId"] == a["actorId"]: errors.add("SELF_HANDOVER")
                for actor, hand in [(a["actorId"], p["giverHand"]), (p["receiverId"], p["receiverHand"])]:
                    if hand.replace("hand", "arm") not in claims.get(actor, set()): errors.add("MISSING_CHANNEL_CLAIM")
                prop = entities.get(p["propId"], {})
                grasps = {x["affordanceId"] for x in prop.get("affordances", []) if x["kind"] == "grasp"}
                if not {p["giverGraspAffordanceId"], p["receiverGraspAffordanceId"]} <= grasps: errors.add("AFFORDANCE_REFERENCE")
                grasp_map = {x["affordanceId"]: x for x in prop.get("affordances", []) if x["kind"] == "grasp"}
                for role in ["giver", "receiver"]:
                    grasp = grasp_map.get(p[role+"GraspAffordanceId"])
                    if grasp and p[role+"Hand"] not in grasp["allowedEffectors"]: errors.add("EFFECTOR_NOT_ALLOWED")
            elif kind == "sit" and not fr["start"] <= p["seatContactFrame"] < fr["end"]:
                errors.add("SEAT_EVENT_ORDER")
            elif kind == "speak":
                start, end = p["audioRangeSamples"]["start"], p["audioRangeSamples"]["end"]
                n, d = project["fps"]["numerator"], project["fps"]["denominator"]
                capacity = fr["end"]*d*48000//n - fr["start"]*d*48000//n
                if not 0 < end-start <= capacity: errors.add("AUDIO_CAPACITY")
                offsets = [v["atSample"] for v in p["visemes"]]
                if offsets != sorted(set(offsets)) or any(v >= end-start for v in offsets): errors.add("VISEME_RANGE")
            if p.get("easeInFrames", 0) + p.get("easeOutFrames", 0) > fr["end"]-fr["start"]: errors.add("EASING_DURATION")
        for a, b in combinations(actions, 2):
            if max(a["frameRange"]["start"], b["frameRange"]["start"]) >= min(a["frameRange"]["end"], b["frameRange"]["end"]): continue
            for ca in a["resourceClaims"]:
                for cb in b["resourceClaims"]:
                    if ca["entityId"] == cb["entityId"] and set(ca["channels"]) & set(cb["channels"]): errors.add("CHANNEL_CONFLICT")
            if a["actionType"] == b["actionType"] == "handover" and a["parameters"]["propId"] == b["parameters"]["propId"]: errors.add("PROP_CONFLICT")
        errors |= symbolic_errors(scene, actions)
    for shot in shots.values():
        scene = scenes.get(shot["sceneId"])
        if not scene: errors.add("SCENE_REFERENCE")
        elif not 0 <= shot["frameRange"]["start"] < shot["frameRange"]["end"] <= scene["durationFrames"]: errors.add("FRAME_RANGE")
        c = shot["camera"]
        if c["nearM"] >= c["farM"] or c["positionM"] == c["targetM"]: errors.add("CAMERA_GEOMETRY")
        # Fixed +Z camera up: a vertical viewing direction makes the look-at basis degenerate.
        if c["positionM"][:2] == c["targetM"][:2]: errors.add("CAMERA_GEOMETRY")
    rev = bundle["revision.json"]
    if rev["expectedRevision"] != project["revision"]: errors.add("STALE_REVISION")
    if len({o["operationId"] for o in rev["operations"]}) != len(rev["operations"]): errors.add("DUPLICATE_OPERATION_ID")
    return errors


RESULTS = []
def check(name, condition):
    RESULTS.append((name, bool(condition)))
    print(("PASS " if condition else "FAIL ") + name)


def schema_negative(name, filename, mutation):
    value = deepcopy(BUNDLE[filename])
    mutation(value)
    check(name, not VALIDATOR.is_valid(value))


def semantic_negative(name, filename, mutation, code):
    candidate = deepcopy(BUNDLE)
    mutation(candidate[filename])
    # Prove the meaningful semantic rejection is not merely a shape error.
    check(name, all(VALIDATOR.is_valid(d) for d in candidate.values()) and code in selected_semantic_errors(candidate))


def main():
    Draft202012Validator.check_schema(SCHEMA)
    check("Draft 2020-12 schema self-check", True)
    for filename, document in BUNDLE.items(): check("Schema: " + filename, VALIDATOR.is_valid(document))
    errors = selected_semantic_errors(BUNDLE)
    check("Selected resolve/static/symbolic checks on original fixture", not errors)
    if errors: print("Unexpected fixture errors:", sorted(errors))
    schema_negative("Reject unknown action type", "action-walk.json", lambda d: d.update(actionType="fly_to"))
    schema_negative("Reject action parameter from a different type", "action-walk.json", lambda d: d["parameters"].update(transferFrame=20))
    schema_negative("Reject fractional frames", "action-walk.json", lambda d: d["frameRange"].update(start=0.5))
    schema_negative("Reject malformed asset hash", "project.json", lambda d: d["assets"][0].update(sha256="invented"))
    schema_negative("Reject unsupported rig profile", "character-aya.json", lambda d: d.update(rigProfileId="arbitrary_rig"))
    schema_negative("Reject array-index revision patch", "revision.json", lambda d: d["operations"].__setitem__(0, {"operationId":"op_bad","operation":"replace","path":"/actions/0","value":0}))
    schema_negative("Reject non-atomic revision", "revision.json", lambda d: d.update(atomic=False))
    schema_negative("Reject wrong audio sample rate", "project.json", lambda d: d.update(audioSampleRateHz=44100))
    schema_negative("Reject unknown document field", "scene.json", lambda d: d.update(uncontrolledCode="do_something()"))
    schema_negative("Reject seat missing its foot-zone bounds", "scene.json", lambda d: d["entities"][4]["affordances"][0].pop("footZone"))
    semantic_negative("Reject reversed frame range", "action-walk.json", lambda d: d["frameRange"].update(start=97), "FRAME_RANGE")
    semantic_negative("Reject transfer outside the action", "action-handover.json", lambda d: d["parameters"].update(transferFrame=240), "HANDOVER_EVENT_ORDER")
    semantic_negative("Reject missing receiver arm claim", "action-handover.json", lambda d: d["resourceClaims"][1].update(channels=["torso"]), "MISSING_CHANNEL_CLAIM")
    semantic_negative("Reject overlapping actor/channel writes", "action-expression.json", lambda d: (d.update(actorId="char_aya"), d["frameRange"].update(start=108,end=156), d["resourceClaims"][0].update(entityId="char_aya")), "CHANNEL_CONFLICT")
    semantic_negative("Reject duplicate logical owner records", "scene.json", lambda d: d["initialState"]["ownership"].append({"propId":"prop_cup","ownerId":"char_ren"}), "MULTIPLE_OWNERS")
    semantic_negative("Reject duplicate transform parents", "scene.json", lambda d: d["initialState"]["attachments"].append(deepcopy(d["initialState"]["attachments"][0])), "MULTIPLE_ATTACHMENTS")
    semantic_negative("Reject incorrect starting owner", "scene.json", lambda d: d["initialState"]["ownership"][2].update(ownerId="char_ren"), "OWNERSHIP_CONDITION")
    semantic_negative("Reject digest mismatch for real fixture bytes", "project.json", lambda d: d["assets"][0].update(sha256="0"*64), "ASSET_HASH_MISMATCH")
    semantic_negative("Reject dangling actor reference", "action-walk.json", lambda d: d.update(actorId="char_missing"), "ENTITY_REFERENCE")
    semantic_negative("Reject non-unit quaternion", "scene.json", lambda d: d["entities"][0]["transform"].update(rotationXyzw=[0,0,0,2]), "NON_UNIT_QUATERNION")
    semantic_negative("Reject non-uniform entity scale", "scene.json", lambda d: d["entities"][0]["transform"].update(scale=[1,2,1]), "NON_UNIFORM_SCALE")
    semantic_negative("Reject grasp with the wrong allowed hand", "scene.json", lambda d: d["entities"][5]["affordances"][0].update(allowedEffectors=["left_hand"]), "EFFECTOR_NOT_ALLOWED")
    semantic_negative("Reject degenerate camera up/view basis", "shot-a.json", lambda d: d["camera"].update(positionM=[0,0,2],targetM=[0,0,1]), "CAMERA_GEOMETRY")
    semantic_negative("Reject stale expectedRevision", "revision.json", lambda d: d.update(expectedRevision=6), "STALE_REVISION")
    semantic_negative("Reject oversized source audio interval", "action-speak.json", lambda d: d["parameters"]["audioRangeSamples"].update(end=96001), "AUDIO_CAPACITY")
    semantic_negative("Reject viseme at excluded audio end", "action-speak.json", lambda d: d["parameters"]["visemes"][-1].update(atSample=96000), "VISEME_RANGE")
    shifted = deepcopy(BUNDLE)
    # Test oracle only: materialize the exact documented proposal in memory.
    for name in ["action-handover.json", "action-expression.json"]:
        for bound in ["start", "end"]: shifted[name]["frameRange"][bound] += 24
    for field in ["receiverContactFrame", "transferFrame", "giverReleaseFrame"]:
        shifted["action-handover.json"]["parameters"][field] += 24
    check("Documented coupled +24-frame candidate passes selected checks", all(VALIDATOR.is_valid(d) for d in shifted.values()) and not selected_semantic_errors(shifted))
    check("Revision test leaves on-disk project revision 7 unchanged", read(EX/"project.json")["revision"] == 7)
    summary = {"python":platform.python_version(),"jsonschema":importlib.metadata.version("jsonschema"),"schema_draft":"2020-12","example_documents":len(BUNDLE),"synthetic_assets":len(BUNDLE["project.json"]["assets"]),"passed":sum(p for _,p in RESULTS),"failed":sum(not p for _,p in RESULTS),"checks":[{"name":n,"passed":p} for n,p in RESULTS]}
    (ROOT/"validation-results.json").write_text(json.dumps(summary,indent=2)+"\n",encoding="utf-8",newline="\n")
    print(f"RESULT: {summary['passed']} passed; {summary['failed']} failed")
    return 1 if summary["failed"] else 0


if __name__ == "__main__": sys.exit(main())
