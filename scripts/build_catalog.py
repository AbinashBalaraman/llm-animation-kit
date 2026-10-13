"""Build the shipped schema/catalog and original editable example scenes."""
from pathlib import Path
import json

ROOT=Path(__file__).resolve().parents[1]/"animation_kit"/"data"

def write(relative,value):
    path=ROOT/relative
    path.parent.mkdir(parents=True,exist_ok=True)
    path.write_text(json.dumps(value,indent=2)+"\n",encoding="utf-8")

def obj(properties,required=None):
    return {"type":"object","properties":properties,"required":list(properties) if required is None else required,"additionalProperties":False}

def number(lo,hi): return {"type":"number","minimum":lo,"maximum":hi}
def integer(lo,hi): return {"type":"integer","minimum":lo,"maximum":hi}
def enum(*values): return {"enum":list(values)}
def array(item,lo,hi): return {"type":"array","items":item,"minItems":lo,"maxItems":hi}
ID={"type":"string","pattern":"^[a-z][a-z0-9_-]{0,47}$"}
COLOR={"type":"string","pattern":"^#[0-9a-fA-F]{6}$"}
TEXT={"type":"string","maxLength":90}
CAMERA=obj({"x":number(80,880),"y":number(80,490),"zoom":number(.6,1.7)})
ACTOR=obj({"id":ID,"x":number(80,880),"y":number(300,465),"scale":number(.5,1.2),"color":COLOR,"accent":COLOR,"rig":enum("pip2d_v1")})
PROP=obj({"id":ID,"kind":enum("star","orb","box"),"x":number(40,920),"y":number(90,430),"size":number(8,50),"color":COLOR})
BASE={"id":ID,"actor":ID,"start":integer(0,1439),"end":integer(1,1440)}
ACTIONS=[]
for kind,parameters in {
    "look_at":{"target":ID},
    "expression":{"emotion":enum("neutral","curious","surprised","happy","sad"),"intensity":number(0,1)},
    "gesture":{"variant":enum("wave","reach","celebrate")},
    "move_to":{"x":number(80,880)}
}.items():
    ACTIONS.append(obj(dict(BASE,type={"const":kind},**parameters)))
ACTION={"oneOf":ACTIONS}
SCENE=obj({"schema_version":{"const":"kit.scene/1.0"},"title":TEXT,"subtitle":TEXT,"fps":{"const":24},"frames":integer(24,1440),
           "sound":enum("none","chime"),"actors":array(ACTOR,1,4),"props":array(PROP,0,8),"actions":array(ACTION,0,64),
           "shots":array(obj({"id":ID,"start":integer(0,1439),"end":integer(1,1440),"camera":CAMERA}),1,8)})
SCENE.update({"$schema":"https://json-schema.org/draft/2020-12/schema","$id":"urn:animation-kit:scene:1.0"})
write("scene.schema.json",SCENE)
OPS={"oneOf":[obj({"type":{"const":kind},**params}) for kind,params in {
    "replace_action":{"action":ACTION},"add_action":{"action":ACTION},"remove_action":{"action_id":ID},
    "shift_action":{"action_id":ID,"delta":integer(-1440,1440)},"set_camera":{"shot_id":ID,"camera":CAMERA},
    "set_actor":{"actor":ACTOR},"set_title":{"title":TEXT,"subtitle":TEXT}
}.items()]}

def tool(name,description,params,required=None,readonly=False):
    return {"name":name,"description":description,"inputSchema":obj(params,required),"annotations":{"readOnlyHint":readonly,"destructiveHint":False,"openWorldHint":False}}

project={"project_id":ID}
TOOLS=[
tool("discover_capabilities","List installed tools, native render capabilities, examples and unsupported requests.",{},readonly=True),
tool("get_context","Retrieve bounded animation recipes and relevant example scenes; no model calls.",{"task":{"type":"string","maxLength":1200},"max_chars":integer(1500,16000)},["task"],True),
tool("load_example","Create a project from an original editable example.",dict(project,example_id=enum("discovery","two_friends","quiet_wave"))),
tool("create_project","Create an immutable revision-zero project from a validated typed 2D scene.",dict(project,scene=SCENE)),
tool("inspect_project","Inspect source and evaluated state at a frame.",dict(project,frame=integer(0,1439)),["project_id"],True),
tool("validate_proposal","Validate a new scene or proposed transaction without publishing changes.",{"scene":SCENE},readonly=True),
tool("apply_revision","Atomically apply named-ID operations. Stale revisions and semantic conflicts fail without mutation.",dict(project,expected_revision=integer(0,1000000),operations=array(OPS,1,16))),
tool("undo","Restore an earlier snapshot as a new revision.",dict(project,expected_revision=integer(0,1000000),target_revision=integer(0,1000000))),
tool("preview","Render a 640x360 native preview, temporal contact sheet, state trace and editable source. Bounded synchronous job; existing valid frames resume.",project),
tool("inspect_artifact","Inspect a verified job and optional frame image for a vision-capable host.",dict(project,job_id={"type":"string","pattern":"^[a-f0-9]{24}$"},frame=integer(0,1439),include_image={"type":"boolean"}),["project_id","job_id"],True),
tool("record_review","Record explicit visual-review evidence for this project revision. Notes do not constitute independent proof of quality.",dict(project,expected_revision=integer(0,1000000),accepted={"type":"boolean"},notes={"type":"string","minLength":10,"maxLength":3000},reviewer=enum("human","model"))),
tool("render_final","Export 1280x720 video from the currently accepted reviewed revision. All pixels are rendered by code.",project),
tool("start_workflow","Start durable workflow budget/memory. Use workflow_step to enforce per-session tool and preview limits.",{"brief":{"type":"string","minLength":1,"maxLength":3000},"max_calls":integer(1,60),"max_previews":integer(1,8)},["brief"]),
tool("workflow_step","Call one installed production tool inside a bounded recorded workflow; tool errors consume call budget.",{"workflow_id":{"type":"string","pattern":"^[a-f0-9]{16}$"},"tool":{"type":"string","maxLength":40},"arguments":{"type":"object"}}),
tool("finish_workflow","Finish with explicit evidence and outstanding limitations, rather than assuming a valid scene is a good video.",{"workflow_id":{"type":"string","pattern":"^[a-f0-9]{16}$"},"outcome":enum("complete","needs_review","unsupported","budget_exhausted"),"summary":{"type":"string","minLength":1,"maxLength":3000}})
]
write("tools.json",TOOLS)
write("capabilities.json",{
    "kit_version":"0.1.0","backend":"puppet2d_v1","scene_schema":"kit.scene/1.0","video_generation_models":False,
    "rigs":["pip2d_v1"],"actions":["look_at","expression","gesture","move_to"],"gesture_variants":["wave","reach","celebrate"],
    "expressions":["neutral","curious","surprised","happy","sad"],"profiles":{"preview":[640,360],"final":[1280,720]},
    "fps":24,"max_seconds":60,"max_actors":4,"max_props":8,"sound":["none","procedural chime/ambient bed"],
    "coordinate_system":"2D design pixels: x right, y down, 960x540 world; actor y is foot baseline",
    "action_semantics":"Half-open frame intervals; move/gaze/expression persist; gestures return to rest. Same-channel overlap rejected.",
    "limitations":["One original 2D puppet rig, front view; no arbitrary art import","No 3D backend, handover, seating, speech/lip-sync, physics, or contact solver yet","No measured parity with other models; no trained model shipped","Render tools synchronous; no running-job cancellation API","Text-only agents need a disclosed visual reviewer"],
    "examples":["discovery","two_friends","quiet_wave"],"license":"GPL-3.0-or-later runtime; original artwork/examples CC0-1.0"
})
PIP={"id":"pip","x":370,"y":445,"scale":.95,"color":"#9bd4c8","accent":"#f7c66c","rig":"pip2d_v1"}
STAR={"id":"spark","kind":"star","x":650,"y":267,"size":30,"color":"#f7c66c"}
scene={"schema_version":"kit.scene/1.0","title":"The little discovery","subtitle":"A glance. A pause. A little wonder.","fps":24,"frames":192,"sound":"chime",
       "actors":[PIP],"props":[STAR],"actions":[
           dict(BASE,id="notice",actor="pip",start=16,end=42,type="look_at",target="spark"),
           dict(BASE,id="question",actor="pip",start=24,end=57,type="expression",emotion="curious",intensity=.8),
           dict(BASE,id="wonder",actor="pip",start=64,end=96,type="expression",emotion="surprised",intensity=1),
           dict(BASE,id="reach",actor="pip",start=76,end=112,type="gesture",variant="reach"),
           dict(BASE,id="delight",actor="pip",start=113,end=144,type="expression",emotion="happy",intensity=1),
           dict(BASE,id="celebrate",actor="pip",start=120,end=184,type="gesture",variant="celebrate")],
       "shots":[{"id":"wide","start":0,"end":64,"camera":{"x":480,"y":270,"zoom":1}},
                {"id":"reaction","start":64,"end":112,"camera":{"x":455,"y":315,"zoom":1.35}},
                {"id":"release","start":112,"end":192,"camera":{"x":480,"y":270,"zoom":1}}]}
# Remove the schema descriptors included in BASE: every concrete action field is overwritten.
write("examples/discovery.json",scene)
import copy
friends=copy.deepcopy(scene)
friends.update(title="An unexpected hello",subtitle="Two friends. One shared moment.",frames=144)
friends["actors"]=[dict(PIP,x=310),dict(PIP,id="poppy",x=665,color="#ee9d96",accent="#b7cedd")]
friends["props"]=[]
friends["shots"]=[{"id":"wide","start":0,"end":144,"camera":{"x":480,"y":270,"zoom":1}}]
friends["actions"]=[{"id":"glance","actor":"pip","start":10,"end":34,"type":"look_at","target":"poppy"},
                    {"id":"hello","actor":"pip","start":30,"end":80,"type":"gesture","variant":"wave"},
                    {"id":"reply","actor":"poppy","start":56,"end":100,"type":"gesture","variant":"wave"},
                    {"id":"smile_a","actor":"pip","start":34,"end":70,"type":"expression","emotion":"happy","intensity":.9},
                    {"id":"smile_b","actor":"poppy","start":68,"end":100,"type":"expression","emotion":"happy","intensity":.8},
                    {"id":"return_glance","actor":"poppy","start":24,"end":48,"type":"look_at","target":"pip"}]
write("examples/two_friends.json",friends)
quiet=copy.deepcopy(friends)
quiet.update(title="A quiet hello",subtitle="Let the gesture breathe.",frames=96,sound="none")
quiet["actors"]=[dict(PIP,x=480)]
quiet["actions"]=[{"id":"wave","actor":"pip","start":20,"end":76,"type":"gesture","variant":"wave"},
                  {"id":"smile","actor":"pip","start":28,"end":60,"type":"expression","emotion":"happy","intensity":.7}]
quiet["shots"][0]["end"]=96
write("examples/quiet_wave.json",quiet)

RECIPES=[
("reaction",["emotion","expression","surprise","react","acting","happy","sad","curious"],"Build a readable reaction",[
"Give the viewer a clear target and a gaze change before the strongest expression.",
"For this rig at 24 fps, begin by testing 8–16 frames of attention, a 6–12 frame pause, then a 12–24 frame expression onset. These are adjustable starting points, not universal timing.",
"Use separate gaze, face and gesture channels; same-channel intervals cannot overlap.",
"An expression persists after its interval. Add a later expression to return to neutral.",
"Inspect onset, maximum expression and the next beat. Change one timing or intensity parameter before rewriting the scene."],"discovery"),
("camera",["camera","shot","crop","zoom","framing","composition"],"Frame poses and reactions",[
"Use 960x540 design coordinates. A camera at x480,y270,zoom1 matches the wide stage.",
"The actor y coordinate is the foot baseline; its head sits about 220*scale pixels above it.",
"Check the raised hands, ears and antenna, not only the face. Text occupies screen-space y29–80.",
"A camera edit should preserve actions and actor positions. Revise only the named shot camera.",
"Shots partition [0,frames), with no overlaps/gaps. Review both sides of a cut for consistent gaze and identity."],"discovery"),
("gesture",["wave","gesture","reach","celebrate","movement","arms"],"Choose and time a supported gesture",[
"Wave, reach and celebrate are the available variants. Reach is expressive posing, not a guaranteed grasp/contact.",
"Gesture controls blend from rest and back using an explicit envelope. Leave a hold before the next gesture.",
"Longer intervals slow the gesture; do not stretch unsupported physical actions into this vocabulary.",
"For a wave, keep the arm silhouette separate from the head and review multiple frames for direction/readability.",
"Gesture and expression may overlap, but two gestures on one actor may not."],"quiet_wave"),
("timing",["timing","delay","pause","duration","frame","revision"],"Retiming without damaging other beats",[
"Frames are integer and zero-based at 24 fps; one second equals 24 frames. Intervals are half-open.",
"shift_action moves start and end by the same delta. Other actions remain fixed.",
"When delaying a reaction, decide whether its gesture should follow. Shift both explicitly if the brief asks for that relationship.",
"Validate all edits as one atomic transaction. If an overlap/end overflow appears, repair the schedule before applying.",
"Inspect before proposing a revision; expected_revision prevents stale edits. Undo creates a new revision."],"discovery"),
("staging",["stage","story","two","character","attention","layout","walk","move"],"Make the action legible",[
"Choose one clear shot purpose: establish a target, reveal a reaction, or resolve the beat.",
"Keep faces and important props separated in silhouette. Put gaze targets inside the view.",
"For two characters, establish a shared wide shot before a closer reaction; front-view rig does not support arbitrary perspective.",
"move_to controls a bounded stylized walk. It does not provide collision avoidance or a contact solver.",
"Reuse locked colors/rig IDs across shots. Review silent playback for the intended emotional beat."],"two_friends"),
("repair",["error","repair","overlap","missing","invalid","failure","unsupported"],"Repair from evidence",[
"Schema error: inspect the exact tool/scene schema instead of guessing another field.",
"Channel conflict: sequence that actor's actions on the indicated channel; do not disable validation.",
"Framing warning: adjust the affected shot's camera and compare its boundary frames.",
"Weak acting: inspect the temporal contact sheet/clip, then adjust gaze lead, pause, expression intensity or gesture timing.",
"Missing capability: report it and retain valid work. Never call a video-generation fallback or execute model-supplied Python.",
"Stop at workflow limits; record unresolved issues rather than declaring quality from a valid export."],"discovery")]
for ident,keywords,purpose,rules,example in RECIPES:
    write(f"recipes/{ident}.json",{"id":ident,"version":"1.0","backend":"puppet2d_v1","purpose":purpose,"keywords":keywords,"rules":rules,"example":example,
                                  "inspection":"Playable preview plus contact sheet/action-boundary frames; human or vision review for appeal.","stop":"Stop when requested effect is reviewed or workflow budget is exhausted."})
print("Catalog, strict schemas, six recipes and three editable examples generated.")
