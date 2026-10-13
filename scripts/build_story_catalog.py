"""Generate the v2 interface and knowledge. Called after the legacy fixture catalog."""
from pathlib import Path
import json
from animation_kit.story_schema import schema, obj, arr, ID, TEXT, FRAME

ROOT=Path(__file__).resolve().parents[1]/"animation_kit"/"data"
def write(name,value):
    (ROOT/name).write_text(json.dumps(value,indent=2)+"\n",encoding="utf-8",newline="\n")

write("story.schema.json",schema())
tools=json.loads((ROOT/"tools.json").read_text())
by_name={t["name"]:t for t in tools}
by_name["create_project"]["inputSchema"]["properties"]["scene"]={"type":"object","description":"Authored kit.story/2.0 document; fetch get_schema first."}
by_name["create_project"]["inputSchema"]["properties"]["legacy_exercise"]={"type":"boolean","description":"Explicit opt-in to archived v1 puppet exercises; never use for a new story."}
by_name["create_project"]["description"]="Create a new authored story from the actual user brief and custom vector artwork. No default character or environment."
by_name["validate_proposal"]["inputSchema"]["properties"]["scene"]={"type":"object"}
by_name["load_example"]["description"]="LEGACY EXERCISE ONLY. Reproduce a v1 fixture; prohibited in production workflows. Does not fulfil a fresh brief."
by_name["inspect_project"]["inputSchema"]["properties"]["frame"]=FRAME
by_name["inspect_artifact"]["inputSchema"]["properties"]["frame"]=FRAME
by_name["get_context"]["description"]="Retrieve task-specific authoring, storytelling and review guidance. Never injects a complete demo scene."
by_name["start_workflow"]["inputSchema"]["properties"]["purpose"]={"enum":["production","legacy_exercise"]}
by_name["start_workflow"]["inputSchema"]["properties"]["max_calls"]["maximum"]=100
by_name["start_workflow"]["inputSchema"]["properties"]["max_previews"]["maximum"]=12
by_name["record_review"]["description"]="Legacy exercise review only. Authored stories require review_story with per-requirement frame evidence."
ops=by_name["apply_revision"]["inputSchema"]["properties"]["operations"]["items"]["oneOf"]
for kind,field in [("replace_story","story"),("replace_shot","shot"),("upsert_asset","asset")]:
    ops.append(obj({"type":{"const":kind},field:{"type":"object"}}))
def tool(name,description,fields,required=None,readonly=False):
    tools.append({"name":name,"description":description,"inputSchema":obj(fields,required),
                  "annotations":{"readOnlyHint":readonly,"destructiveHint":False,"openWorldHint":False}})
tool("get_schema","Retrieve the exact authored story contract on demand; keeps discovery/context small.",{"version":{"enum":["story","legacy"]}},[],True)
tool("check_story","Check that every brief requirement has visible drawing evidence at its planned beat. This is structural, not semantic visual approval.",{"project_id":ID},readonly=True)
tool("preview_frames","Render selected storyboard/acting frames without encoding a movie; returns an inspectable PNG.",{"project_id":ID,"frames":arr(FRAME,1,32)},["project_id"])
tool("review_story","Record a source-bound visual review for EVERY brief requirement, citing actual preview frames. Disclose whether normal-speed playback was reviewed.",{
    "project_id":ID,"expected_revision":{"type":"integer","minimum":0},
    "preview_job_id":{"type":"string","pattern":"^[a-f0-9]{24}$"},
    "accepted":{"type":"boolean"},"reviewer":{"enum":["human","model"]},
    "coverage":arr(obj({"requirement_id":ID,"status":{"enum":["pass","fail","unreviewed"]},
                         "frames":arr(FRAME,1,16),"observation":{"type":"string","minLength":12,"maxLength":1200}}),1,24),
    "playback_reviewed":{"type":"boolean"},"notes":TEXT})
write("tools.json",tools)
write("capabilities.json",{
    "kit_version":"0.2.0","backend":"authored2d_v2","scene_schema":"kit.story/2.0","video_generation_models":False,
    "default_artwork":None,"authoring":"Original vector geometry, hierarchical groups, reusable assets, per-part pose overrides, per-shot keyframes; optional Python authoring SDK compiles to JSON.",
    "shapes":["ellipse","rect","polygon","path (M/L/Q/C/Z)","text","group","instance"],
    "motion":["x","y","scale_x","scale_y","rotation","opacity","camera x/y/zoom"],
    "easing":["linear","hold","smooth","in_cubic","out_cubic","out_back"],
    "profiles":{"preview":[640,360],"final":[1280,720]},"fps":[24,30,60],"max_seconds":120,
    "coordinates":"960x540 design pixels; x right/y down; local transforms compose through groups; tracks use local shot frames; beats use global frames.",
    "audio":"Authored procedural bell/pop/purr cues; no voice synthesis or video model.",
    "review":"Brief coverage, visible drawing evidence, current preview, per-requirement observations and disclosed playback scope.",
    "limitations":["Vector 2D only; no full 3D/physics/automatic lip sync","Renderer does not infer story from text: the host LLM authors artwork, beats and keyframes","Declared visual reviews cannot automatically prove semantic correctness or comedy","No parity benchmark across other LLMs yet","Synchronous rendering; host Python code is not sandboxed by the kit"],
    "legacy":"kit.scene/1.0 retained only for explicit regression/exercise use; prohibited in production workflows",
    "schema_tool":"get_schema","authoring_sdk":"animation_kit.authoring",
    "license":"GPL-3.0-or-later runtime; original authored artwork CC0; bundled fonts SIL OFL 1.1"})

recipes=[
("story",["story","script","funny","cat","president","narrative","brief"],"Turn the user's request into visible events",[
"Preserve the original prompt in brief.prompt. Extract independently reviewable requirements: identity, setting, key event/outcome, tone.",
"Write a short causal sequence: desire, obstacle, attempt, changed situation, payoff. A label announcing the outcome does not depict it.",
"Each shot has a purpose and evidence nodes. Link requirements to beats with specific global evidence frames.",
"Comedy needs an expectation followed by a readable violation and a reaction/hold. Show the physical action that causes the joke.",
"Start from an empty document. Invent the necessary artwork and motion; examples teach technique and are not a substitute for the requested story."]),
("staging",["stage","character","asset","draw","art","silhouette","layout"],"Author recognizable characters and environments",[
"Draw new subjects from ellipses, polygons, cubic paths and groups. Reuse your own asset definitions across shots.",
"List identifying visual features before drawing. A cat needs recognizably feline silhouette and face, not a humanoid named cat.",
"Separate articulated parts into groups whose local origin is the joint. Pose them with instance overrides.",
"Build the setting needed by the script: architecture, furniture and story props. The engine has no default environment.",
"Check silhouette, focal point, readable type and foreground/character/background layering before animating."]),
("camera",["camera","shot","crop","zoom","framing","composition"],"Frame story-specific actions",[
"Design coordinates are 960x540. Camera x480/y270/zoom1 shows the whole canvas.",
"Use an establishing shot to orient, then frame the gesture/prop interaction large enough to understand. Camera is optional.",
"Camera tracks use local shot frames. Shots partition the full global timeline without gaps.",
"Preserve underlying acting when revising a camera. Check both sides of cuts and leave space around ears, paws and important props."]),
("gesture",["gesture","motion","pose","walk","tail","arm","paw","acting"],"Build action from articulated poses",[
"Author anticipation, action, contact and settle with per-part transforms; motion is not restricted to named preset gestures.",
"Keep the root and prop movement coordinated at contact. There is no contact solver: inspect the actual overlap frame.",
"Use small offsets for tail, ears and follow-through, while the main pose stays readable.",
"Use scale_y around a sensible pivot for blink/squash, and rotation around the shoulder/elbow for a paw gesture.",
"Evaluate any frame independently. Use keyframe tracks rather than mutable step-by-step state."]),
("timing",["timing","delay","pause","frame","revision","easing"],"Time visible action and comedy",[
"Shot-local tracks have strictly increasing integer frames; beats cite global frames. Easing belongs to the destination key.",
"Use hold for discrete changes, smooth for balanced motion, out_cubic for settling, out_back for restrained overshoot.",
"Hold the setup long enough to read before the payoff. A reaction pause can sell a joke more clearly than constant motion.",
"Replace the affected shot or asset in an atomic revision, or replace_story for a structural rewrite. Reviews become stale."]),
("repair",["review","repair","failure","error","quality","unsupported"],"Reject technical success that misses the brief",[
"Render selected frames with preview_frames, then inspect actual pixels. Fix identity/staging before spending on full preview.",
"Run check_story: it checks visible drawing and coverage, not whether the drawing truly is a cat or the story is funny.",
"Review every brief requirement against actual preview frames. A title-only or invisible drawing claim fails structural evidence.",
"State playback_reviewed truthfully. Sampled frames cannot establish smooth motion, timing at normal speed or audio quality.",
"Use review_story, then render_final. If a requirement remains unmet, record rejection and revise; never relabel a fixture as success."])
]
for ident,keywords,purpose,rules in recipes:
    write(f"recipes/{ident}.json",{"id":ident,"version":"2.0","backend":"authored2d_v2","keywords":keywords,"purpose":purpose,"rules":rules})
# The old reaction recipe remains specifically labelled as a legacy exercise.
print("Generated authored-story schema, production tools and v2 knowledge.")
