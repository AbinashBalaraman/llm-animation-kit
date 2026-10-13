"""V2 regression checks exercise authored geometry, script fidelity gates and actual output."""
import copy
import tempfile
import unittest
from pathlib import Path
from unittest.mock import patch
from animation_kit.authoring import story, shot, group, rect, ellipse, instance, track, beat, text, path
from animation_kit.contracts import validate, packaged_json
from animation_kit.story import evaluate, draw_frame, value_at, visible_evidence
from animation_kit.story_review import preflight
from animation_kit.tools import Tools


def tiny_story():
    s=story("A turquoise satellite unfolds its orange solar panel.",[("satellite","Show a turquoise satellite unfolding an orange panel.")])
    s["frames"]=12
    s["assets"]=[{"id":"satellite","description":"Box and articulated solar panel", "nodes":[
        rect("body",60,50,"#44CCBB"),group("hinge",rect("panel",60,20,"#FF9955"),x=60,y=20)]}]
    s["shots"]=[shot("unfold",0,12,"Satellite unfolds", "#122334",
        instance("satellite","satellite",x=400,y=260,overrides={"hinge":{"rotation":track((0,-90),(11,0))}}))]
    s["beats"]=[beat("unfolded","unfold",11,"Panel is extended",["satellite"],["satellite"])]
    return s


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
        p=call("preview",{"project_id":"test"})
        self.assertTrue(p["ok"],p);preview=p["result"]
        review={"project_id":"test","expected_revision":0,"preview_job_id":preview["job_id"],"accepted":True,
                "reviewer":"model","coverage":[{"requirement_id":"satellite","status":"pass","frames":[0,11],
                "observation":"Test harness: the turquoise body and orange panel are rendered at two distinct articulated poses."}],
                "playback_reviewed":False,"notes":"Synthetic test evidence only, not an independent aesthetic review."}
        self.assertEqual(self.api.call("render_final",{"project_id":"test"})["error"]["code"],"review_required")
        missing=dict(review,coverage=[dict(review["coverage"][0],requirement_id="wrong")])
        self.assertEqual(self.api.call("review_story",missing)["error"]["code"],"review_coverage")
        good=call("review_story",review);self.assertTrue(good["ok"],good)
        self.assertFalse(good["result"]["playback_reviewed"])
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


if __name__=="__main__": unittest.main()
