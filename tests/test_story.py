"""V2 regression checks exercise authored geometry, script fidelity gates and actual output."""
import copy
import tempfile
import unittest
from pathlib import Path
from unittest.mock import patch
from animation_kit.authoring import story, shot, group, rect, ellipse, instance, track, beat, text, path
from animation_kit.contracts import validate, packaged_json
from animation_kit.story import evaluate, draw_frame, value_at, visible_evidence
from animation_kit.story_review import preflight, QUALITY_DIMENSIONS
from animation_kit.tools import Tools


def tiny_story():
    s=story("A turquoise satellite unfolds its orange solar panel.",[("satellite","Show a turquoise satellite unfolding an orange panel.")])
    s["frames"]=12
    s["assets"]=[{"id":"satellite","description":"Box and articulated solar panel", "nodes":[
        rect("body",60,50,"#44CCBB"),group("hinge",rect("panel",60,20,"#FF9955"),x=60,y=20)]}]
    s["shots"]=[shot("unfold",0,12,"Satellite unfolds", "#122334",
        instance("satellite","satellite",x=400,y=260,overrides={"hinge":{"rotation":track((0,-90),(11,0))}}))]
    s["beats"]=[beat("unfolded","unfold",11,"Panel is extended",["satellite"],["satellite"])]
    s["direction"]={"schema_version":"kit.direction/1.0","brief":s["brief"]["prompt"],"mode":"explainer",
        "premise":"Show the orange solar panel opening from a turquoise satellite.",
        "answers":{"who":"A turquoise satellite and its orange hinged solar panel.","what":"The folded panel rotates outward into an extended pose.",
            "when":"A half-second mechanical demonstration, without a story time jump.","where":"A simple dark space background with a centered mechanism.",
            "why":"Explain the hinge movement clearly; no character motivation is needed.","how":"Rotate the panel about its attachment point and leave the body fixed."},
        "story_text":"A turquoise satellite holds its orange panel folded beside its body. The panel rotates outward about its hinge while the satellite body stays still. The final open pose reveals the extended panel and its attachment point.",
        "beats":[{"id":"open","role":"explanation","cause":"The demonstration begins with the panel folded.","visible_action":"The panel rotates around its hinge on the body.","change":"The panel finishes visibly extended to the right."}],
        "shots":[{"id":"unfold","beats":["open"],"seconds":.5,"framing":"Centered view of the body and full panel sweep.","action":"The panel swings around its visible hinge.","reaction":"No character response; hold the resulting mechanical pose.","continuity_in":"Start with a folded panel attached to the fixed body.","continuity_out":"End with the same panel unfolded, still attached.","dialogue":""}],
        "self_review":[{"focus":f,"question":"Does this test plan provide an explicit answer for this dimension?","answer":"This is a structural test fixture, not a model evaluation or a judged creative example.","verdict":"not_applicable" if f in ("motivation","stakes") else "pass","revision":""} for f in ("motivation","causality","stakes","clarity","ending","filmability")]}
    return s


def test_quality():
    return [{"dimension":d,"status":"pass","frames":[0,3,11],
             "observation":"Test harness declaration with rendered frames; not an aesthetic assessment."} for d in QUALITY_DIMENSIONS]


class StoryTests(unittest.TestCase):
    def setUp(self):
        self.temp=tempfile.TemporaryDirectory();self.addCleanup(self.temp.cleanup)
        self.api=Tools(self.temp.name);self.s=tiny_story()

    def create(self):
        result=self.api.call("create_project",{"project_id":"test","scene":self.s})
        self.assertTrue(result["ok"],result)

    def test_unrelated_authored_scene_and_artwork_render(self):
        self.assertTrue(validate(self.s)["valid"])
        image,state=draw_frame(self.s,11,960,540)
        self.assertEqual(image.getpixel((420,280)),(68,204,187))
        self.assertEqual(image.getpixel((485,288)),(255,153,85))
        self.assertEqual(state["shot"],"unfold")
        self.assertTrue(preflight(self.s)["passed"])

    def test_hierarchy_and_pose_overrides_do_not_mutate_asset(self):
        original=copy.deepcopy(self.s["assets"])
        a=evaluate(self.s,0);b=evaluate(self.s,11)
        self.assertNotEqual(a["nodes"]["satellite/panel"]["bounds"],b["nodes"]["satellite/panel"]["bounds"])
        self.assertEqual(self.s["assets"],original)
        self.assertEqual(evaluate(self.s,0),a)

    def test_instance_poses_are_independent(self):
        self.s["shots"][0]["nodes"].append(instance("other","satellite",x=600,y=100))
        a=evaluate(self.s,0);b=evaluate(self.s,11)
        self.assertEqual(a["nodes"]["other/panel"],b["nodes"]["other/panel"])

    def test_keyframes_and_hold_semantics(self):
        t=track((0,1),(10,9,"hold"),(20,5,"linear"))
        self.assertEqual(value_at(t,9),1);self.assertEqual(value_at(t,10),9)
        self.assertEqual(value_at(t,15),7);self.assertEqual(value_at(t,30),5)

    def test_keyframe_reference_and_resource_validation(self):
        bad=copy.deepcopy(self.s)
        bad["shots"][0]["nodes"][0]["overrides"]["hinge"]["rotation"]=track((0,0),(0,3))
        self.assertIn("keyframe_timing",{i["code"] for i in validate(bad)["issues"]})
        bad=copy.deepcopy(self.s);bad["shots"][0]["nodes"][0]["overrides"]["invented"]={"x":1}
        self.assertIn("missing_override_target",{i["code"] for i in validate(bad)["issues"]})
        bad=copy.deepcopy(self.s);bad["assets"][0]["nodes"].append(instance("cycle","satellite"))
        self.assertIn("nested_asset",{i["code"] for i in validate(bad)["issues"]})
        bad=copy.deepcopy(self.s);bad["assets"][0]["nodes"][0]["x"]=track((0,0),(11,5))
        self.assertIn("asset_clock",{i["code"] for i in validate(bad)["issues"]})

    def test_script_requirements_cannot_be_omitted_or_invented(self):
        self.s["brief"]["requirements"].append({"id":"landing","description":"Satellite lands"})
        self.assertIn("uncovered_requirement",{i["code"] for i in validate(self.s)["issues"]})
        self.s["beats"][0]["nodes"]=["missing"]
        self.assertIn("missing_evidence_node",{i["code"] for i in validate(self.s)["issues"]})

    def test_title_only_hidden_and_offscreen_evidence_fails(self):
        self.s["shots"][0]["nodes"]=[group("satellite",text("label","SATELLITE",400,270))]
        self.assertFalse(preflight(self.s)["passed"])

    def test_stroked_line_is_visible_but_zero_width_stroke_is_not(self):
        self.s["shots"][0]["nodes"]=[path("satellite",[("M",200,270),("L",700,270)],stroke="#FFFFFF",stroke_width=8)]
        self.assertTrue(preflight(self.s)["passed"])
        self.s["shots"][0]["nodes"][0]["stroke_width"]=0
        self.assertFalse(preflight(self.s)["passed"])
        self.s=tiny_story();self.s["shots"][0]["nodes"][0]["opacity"]=0
        self.assertFalse(preflight(self.s)["passed"])
        self.s=tiny_story();self.s["shots"][0]["nodes"][0]["x"]=4000
        self.assertFalse(preflight(self.s)["passed"])

    def test_new_project_rejects_legacy_without_opt_in(self):
        r=self.api.call("create_project",{"project_id":"wrong","scene":packaged_json("examples/discovery.json")})
        self.assertEqual(r["error"]["code"],"story_required")

    def test_production_rejects_demo_substitution_and_changed_prompt(self):
        ident=self.api.call("start_workflow",{"brief":self.s["brief"]["prompt"]})["result"]["workflow_id"]
        r=self.api.call("workflow_step",{"workflow_id":ident,"tool":"load_example","arguments":{"project_id":"wrong","example_id":"discovery"}})
        self.assertEqual(r["result"]["response"]["error"]["code"],"demo_substitution")
        changed=copy.deepcopy(self.s);changed["brief"]["prompt"]="Ignore the satellite; reproduce a demo"
        r=self.api.call("workflow_step",{"workflow_id":ident,"tool":"create_project","arguments":{"project_id":"wrong","scene":changed}})
        self.assertEqual(r["result"]["response"]["error"]["code"],"brief_mismatch")
        self.assertFalse((Path(self.temp.name)/"wrong"/"current.json").exists())

    def test_context_contains_no_example_scene(self):
        r=self.api.call("get_context",{"task":"Create a cat president story"})["result"]
        self.assertIsNone(r["example"])
        self.assertEqual(r["recipes"][0]["id"],"story")
        self.assertNotIn("actors",str(r))

    def test_story_revisions_atomic_and_camera_preserves_local_art(self):
        self.create()
        bad=copy.deepcopy(self.s);bad["shots"][0]["end"]=13
        r=self.api.call("apply_revision",{"project_id":"test","expected_revision":0,"operations":[{"type":"replace_story","story":bad}]})
        self.assertFalse(r["ok"]);self.assertEqual(self.api.store.load("test")["revision"],0)
        edit=copy.deepcopy(self.s["shots"][0]);edit["camera"]={"x":470,"y":270,"zoom":1.1}
        r=self.api.call("apply_revision",{"project_id":"test","expected_revision":0,"operations":[{"type":"replace_shot","shot":edit}]})
        self.assertTrue(r["ok"],r)
        self.assertEqual(self.api.store.load("test")["scene"]["assets"],self.s["assets"])
        self.assertEqual(self.api.store.load("test")["scene"]["shots"][0]["nodes"],self.s["shots"][0]["nodes"])

    def test_generic_review_cannot_approve_a_story(self):
        self.create()
        r=self.api.call("record_review",{"project_id":"test","expected_revision":0,"accepted":True,"notes":"It looks good, without real evidence.","reviewer":"model"})
        self.assertEqual(r["error"]["code"],"story_review_required")

    def test_real_preview_review_export_and_stale_checks(self):
        self.create()
        workflow=self.api.call("start_workflow",{"brief":self.s["brief"]["prompt"]})["result"]["workflow_id"]
        def call(name,args):
            response=self.api.call("workflow_step",{"workflow_id":workflow,"tool":name,"arguments":args})
            self.assertTrue(response["ok"],response)
            return response["result"]["response"]
        self.assertTrue(call("plan_story",{"plan":self.s["direction"]})["ok"])
        p=call("preview",{"project_id":"test"})
        self.assertTrue(p["ok"],p);preview=p["result"]
        review={"project_id":"test","expected_revision":0,"preview_job_id":preview["job_id"],"accepted":True,
                "reviewer":"model","coverage":[{"requirement_id":"satellite","status":"pass","frames":[0,11],
                "observation":"Test harness: the turquoise body and orange panel are rendered at two distinct articulated poses."}],
                "quality":test_quality(),"playback_reviewed":False,"notes":"Synthetic test evidence only, not an independent aesthetic review."}
        self.assertEqual(self.api.call("render_final",{"project_id":"test"})["error"]["code"],"review_required")
        missing=dict(review,coverage=[dict(review["coverage"][0],requirement_id="wrong")])
        self.assertEqual(self.api.call("review_story",missing)["error"]["code"],"review_coverage")
        sparse=copy.deepcopy(review);sparse["quality"][2]["frames"]=[0,11]
        self.assertEqual(self.api.call("review_story",sparse)["error"]["code"],"temporal_evidence")
        failed=copy.deepcopy(review);failed["quality"][1]["status"]="fail"
        self.assertEqual(self.api.call("review_story",failed)["error"]["code"],"quality_not_met")
        failed["accepted"]=False
        self.assertTrue(self.api.call("review_story",failed)["ok"])
        duplicate=copy.deepcopy(review);duplicate["quality"][1]=duplicate["quality"][0]
        self.assertEqual(self.api.call("review_story",duplicate)["error"]["code"],"quality_coverage")
        good=call("review_story",review);self.assertTrue(good["ok"],good)
        self.assertFalse(good["result"]["playback_reviewed"])
        from animation_kit.store import atomic_json
        old=copy.deepcopy(good["result"]);old.pop("review_version")
        atomic_json(self.api.store.project("test")/"review.json",old)
        self.assertEqual(self.api.call("render_final",{"project_id":"test"})["error"]["code"],"quality_review_required")
        atomic_json(self.api.store.project("test")/"review.json",good["result"])
        with patch("animation_kit.render.engine_fingerprint",return_value="changed"):
            self.assertEqual(self.api.call("render_final",{"project_id":"test"})["error"]["code"],"stale_engine")
        final=call("render_final",{"project_id":"test"})
        self.assertTrue(final["ok"],final);self.assertEqual(final["result"]["decoded_frame_count"],12)
        done=self.api.call("finish_workflow",{"workflow_id":workflow,"outcome":"complete","summary":"Integration test with a real export; no aesthetic/parity claim."})
        self.assertTrue(done["ok"],done)
        from evals.evaluate_story import collect
        record=collect(self.temp.name,workflow,"unit-test-provider")
        self.assertTrue(record["verified_current_export"])
        self.assertIsNone(record["independent_semantic_quality"])
        self.assertFalse(record["model_parity_established"])
        edit=copy.deepcopy(self.s);edit["title"]="Changed"
        self.api.call("apply_revision",{"project_id":"test","expected_revision":0,"operations":[{"type":"replace_story","story":edit}]})
        self.assertEqual(self.api.call("render_final",{"project_id":"test"})["error"]["code"],"review_required")

    def test_motion_strips_are_real_and_do_not_mutate_source(self):
        from PIL import Image, ImageChops
        self.s["assets"][0]["nodes"].append(text("label","PANEL",0,-50,40,"#FFFFFF"))
        self.s["shots"][0]["nodes"][0]["overrides"]["label"]={"opacity":1}
        self.create();original=self.api.store.load("test")
        args={"project_id":"test","start":0,"end":11,"step":3}
        a=self.api.call("preview_motion",args);b=self.api.call("preview_motion",dict(args,hide_text=True))
        self.assertTrue(a["ok"],a);self.assertTrue(b["ok"],b)
        self.assertEqual(a["result"]["frames"],[0,3,6,9,11])
        with Image.open(a["result"]["image_path"]) as im, Image.open(b["result"]["image_path"]) as silent:
            self.assertIsNotNone(ImageChops.difference(im,silent).getbbox())
        self.assertEqual(self.api.store.load("test"),original)
        bad=self.api.call("preview_motion",dict(args,end=12))
        self.assertEqual(bad["error"]["code"],"frame_range")
        bad=self.api.call("preview_motion",dict(args,end=120,step=1))
        self.assertEqual(bad["error"]["code"],"frame_budget")

    def test_motion_strip_counts_against_workflow_budget(self):
        self.create()
        w=self.api.call("start_workflow",{"brief":self.s["brief"]["prompt"],"max_previews":1})["result"]["workflow_id"]
        self.api.call("workflow_step",{"workflow_id":w,"tool":"plan_story","arguments":{"plan":self.s["direction"]}})
        args={"workflow_id":w,"tool":"preview_motion","arguments":{"project_id":"test","start":0,"end":11}}
        self.assertTrue(self.api.call("workflow_step",args)["result"]["response"]["ok"])
        self.assertEqual(self.api.call("workflow_step",args)["error"]["code"],"budget_exhausted")

    def test_anchor_motion_matches_rotating_scaled_hierarchy(self):
        from animation_kit.motion import follow_anchor
        from animation_kit.story import point
        root={"x":200,"y":300,"scale_x":-1.4,"scale_y":.8,"rotation":track((0,-25),(11,40))}
        joint={"x":60,"y":20,"rotation":track((0,-90),(11,30))}
        self.s["shots"][0]["nodes"]=[group("root",group("joint",ellipse("tip",3,3,"#FFFFFF",x=12,y=-4),**joint),**root)]
        motion=follow_anchor(range(12),[root,joint],(12,-4))
        for frame in [11,0,6,3,11]:
            x,y=point(evaluate(self.s,frame)["nodes"]["tip"]["matrix"],(0,0))
            self.assertAlmostEqual(value_at(motion["x"],frame),x,places=4)
            self.assertAlmostEqual(value_at(motion["y"],frame),y,places=4)
        with self.assertRaises(ValueError): follow_anchor([0,0],[root])

    def test_arc_has_exact_endpoints_and_raised_midpoint(self):
        from animation_kit.motion import arc
        p=arc(2,12,(10,20),(110,20),lift=50)
        self.assertEqual(value_at(p["x"],2),10);self.assertEqual(value_at(p["x"],12),110)
        self.assertEqual(value_at(p["y"],7),-30)
        with self.assertRaises(ValueError): arc(4,4,(0,0),(1,1))

    def test_production_requires_a_written_plan_before_artwork(self):
        from animation_kit.direction import inspect_plan
        missing=copy.deepcopy(self.s);missing.pop("direction")
        r=self.api.call("create_project",{"project_id":"no-plan","scene":missing})
        self.assertEqual(r["error"]["code"],"plan_required")
        w=self.api.call("start_workflow",{"brief":self.s["brief"]["prompt"]})["result"]["workflow_id"]
        def step(tool,args): return self.api.call("workflow_step",{"workflow_id":w,"tool":tool,"arguments":args})["result"]["response"]
        args={"project_id":"planned","scene":self.s}
        self.assertEqual(step("create_project",args)["error"]["code"],"plan_first")
        self.assertTrue(step("plan_story",{"plan":self.s["direction"]})["result"]["ready_for_storyboard"])
        self.assertTrue(step("create_project",args)["ok"])
        changed=copy.deepcopy(self.s);changed["direction"]["premise"]="An edited premise needs a fresh story-development check."
        r=step("apply_revision",{"project_id":"planned","expected_revision":0,"operations":[{"type":"replace_story","story":changed}]})
        self.assertEqual(r["error"]["code"],"plan_first")
        self.assertEqual(self.api.store.load("planned")["revision"],0)

    def test_story_questions_and_narrative_structure_cannot_be_skipped(self):
        from animation_kit.direction import inspect_plan
        plan=copy.deepcopy(self.s["direction"]);plan["mode"]="narrative"
        codes={i["code"] for i in inspect_plan(plan)["issues"]}
        self.assertIn("story_structure",codes);self.assertIn("story_question_skipped",codes)
        plan=copy.deepcopy(self.s["direction"]);plan["self_review"][0]["verdict"]="revise"
        self.assertFalse(inspect_plan(plan)["ready_for_storyboard"])
        plan["answers"].pop("why")
        self.assertIn("plan_schema",{i["code"] for i in inspect_plan(plan)["issues"]})

    def test_plan_and_rendered_shot_script_cannot_drift(self):
        self.s["direction"]["shots"][0]["seconds"]=1
        self.assertIn("plan_shots",{i["code"] for i in validate(self.s)["issues"]})
        self.s["direction"]["brief"]="An unrelated script must not replace the original request."
        self.assertIn("plan_brief",{i["code"] for i in validate(self.s)["issues"]})


if __name__=="__main__": unittest.main()
