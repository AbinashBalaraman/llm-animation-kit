"""Behavioral checks for transactions, tool protocol, budgeting and real export."""
import copy
import json
import subprocess
import sys
import tempfile
import unittest
from pathlib import Path

from animation_kit.agent import run_agent
from animation_kit.components import evaluate
from animation_kit.contracts import KitError, loads, packaged_json, validate
from animation_kit.render import render
from animation_kit.store import Store, digest
from animation_kit.tools import Tools
from animation_kit.transport import dispatch


class KitTests(unittest.TestCase):
    def setUp(self):
        self.temp=tempfile.TemporaryDirectory()
        self.addCleanup(self.temp.cleanup)
        self.api=Tools(self.temp.name)
        self.scene=packaged_json("examples/discovery.json")

    def create(self):
        self.assertTrue(self.api.call("create_project",{"project_id":"demo","scene":self.scene,"legacy_exercise":True})["ok"])

    def test_examples_validate(self):
        for name in ("discovery","two_friends","quiet_wave"):
            self.assertTrue(validate(packaged_json(f"examples/{name}.json"))["valid"])

    def test_strict_json(self):
        for text in ('{"x":1,"x":2}','{"x":NaN}','{"x":Infinity}','{"x":1e999}'):
            with self.assertRaises(KitError): loads(text)

    def test_non_json_python_arguments_fail_cleanly(self):
        response=self.api.call("get_context",{"task":"Test","max_chars":float("nan")})
        self.assertFalse(response["ok"])
        self.assertEqual(response["error"]["code"],"non_json_arguments")

    def test_schema_rejects_unknown_and_executable_fields(self):
        self.scene["python"]="print('not allowed')"
        self.assertFalse(validate(self.scene)["valid"])

    def test_overlap_rejected_but_independent_channels_allowed(self):
        self.assertTrue(validate(self.scene)["valid"])
        self.scene["actions"].append(dict(self.scene["actions"][1],id="conflict",start=30,end=60))
        self.assertIn("channel_conflict",[x["code"] for x in validate(self.scene)["issues"]])

    def test_reference_and_timing_errors(self):
        self.scene["actions"][0]["target"]="absent"
        self.scene["actions"][0]["end"]=193
        codes={x["code"] for x in validate(self.scene)["issues"]}
        self.assertTrue({"timing","missing_target"}.issubset(codes))

    def test_shots_cover_scene_once(self):
        self.scene["shots"][1]["start"]+=1
        self.assertFalse(validate(self.scene)["valid"])

    def test_path_escape_and_missing_project(self):
        for ident in ("../outside","C:/temp","Demo"):
            response=self.api.call("inspect_project",{"project_id":ident})
            self.assertFalse(response["ok"])
        self.assertEqual(self.api.call("inspect_project",{"project_id":"missing"})["error"]["code"],"not_found")

    def test_atomic_failure_and_stale_revision(self):
        self.create()
        before=self.api.store.load("demo")
        failed=self.api.call("apply_revision",{"project_id":"demo","expected_revision":0,"operations":[
            {"type":"shift_action","action_id":"wonder","delta":6},
            {"type":"shift_action","action_id":"celebrate","delta":200}]})
        self.assertFalse(failed["ok"])
        self.assertEqual(self.api.store.load("demo"),before)
        good=self.api.call("apply_revision",{"project_id":"demo","expected_revision":0,"operations":[{"type":"shift_action","action_id":"wonder","delta":6}]})
        self.assertTrue(good["ok"])
        stale=self.api.call("apply_revision",{"project_id":"demo","expected_revision":0,"operations":[{"type":"shift_action","action_id":"wonder","delta":1}]})
        self.assertEqual(stale["error"]["code"],"stale_revision")

    def test_camera_edit_preserves_world_state(self):
        self.create()
        before=evaluate(self.scene,90)["actors"]
        response=self.api.call("apply_revision",{"project_id":"demo","expected_revision":0,"operations":[{"type":"set_camera","shot_id":"reaction","camera":{"x":470,"y":300,"zoom":1.1}}]})
        self.assertTrue(response["ok"])
        after=self.api.store.load("demo")["scene"]
        self.assertEqual(evaluate(after,90)["actors"],before)
        self.assertEqual(after["actions"],self.scene["actions"])

    def test_undo_is_new_revision(self):
        self.create()
        self.api.call("apply_revision",{"project_id":"demo","expected_revision":0,"operations":[{"type":"set_title","title":"Changed","subtitle":"Changed"}]})
        restored=self.api.call("undo",{"project_id":"demo","expected_revision":1,"target_revision":0})
        self.assertEqual(restored["result"]["revision"],2)
        self.assertEqual(self.api.store.load("demo")["scene"],self.scene)

    def test_snapshot_corruption_detected(self):
        self.create()
        path=Path(self.temp.name)/"demo"/"snapshots"/"000000.json"
        value=json.loads(path.read_text())
        value["scene"]["title"]="tampered"
        path.write_text(json.dumps(value))
        self.assertEqual(self.api.call("inspect_project",{"project_id":"demo"})["error"]["code"],"corrupt_snapshot")

    def test_state_sampling_is_order_independent(self):
        first=evaluate(self.scene,145)
        evaluate(self.scene,12)
        self.assertEqual(first,evaluate(self.scene,145))
        self.assertEqual(first["actors"]["pip"]["emotion"],"happy")
        self.assertEqual(evaluate(self.scene,191)["actors"]["pip"]["gesture"],"none")

    def test_context_is_relevant_and_bounded(self):
        result=self.api.call("get_context",{"task":"camera zoom crop framing","max_chars":3000})["result"]
        self.assertEqual(result["recipes"][0]["id"],"camera")
        self.assertLess(len(json.dumps(result)),3150)

    def test_workflow_errors_consume_budget(self):
        state=self.api.call("start_workflow",{"brief":"Test","max_calls":1})["result"]
        ident=state["workflow_id"]
        step=self.api.call("workflow_step",{"workflow_id":ident,"tool":"inspect_project","arguments":{"project_id":"missing"}})
        self.assertTrue(step["ok"])
        self.assertFalse(step["result"]["response"]["ok"])
        exhausted=self.api.call("workflow_step",{"workflow_id":ident,"tool":"discover_capabilities","arguments":{}})
        self.assertEqual(exhausted["error"]["code"],"budget_exhausted")

    def test_false_completion_rejected(self):
        ident=self.api.call("start_workflow",{"brief":"Test"})["result"]["workflow_id"]
        response=self.api.call("finish_workflow",{"workflow_id":ident,"outcome":"complete","summary":"No real export yet"})
        self.assertEqual(response["error"]["code"],"missing_evidence")

    def test_final_requires_current_review(self):
        self.create()
        self.assertEqual(self.api.call("render_final",{"project_id":"demo"})["error"]["code"],"review_required")
        self.api.call("record_review",{"project_id":"demo","expected_revision":0,"accepted":True,"notes":"Test-only review record, no aesthetic claim","reviewer":"model"})
        self.api.call("apply_revision",{"project_id":"demo","expected_revision":0,"operations":[{"type":"set_title","title":"Changed","subtitle":"Changed"}]})
        self.assertEqual(self.api.call("render_final",{"project_id":"demo"})["error"]["code"],"review_required")

    def test_mcp_tools_and_error_contract(self):
        init=dispatch(self.api,{"jsonrpc":"2.0","id":1,"method":"initialize","params":{"protocolVersion":"2025-11-25"}})
        self.assertIn("tools",init["result"]["capabilities"])
        tools=dispatch(self.api,{"jsonrpc":"2.0","id":2,"method":"tools/list"})
        self.assertTrue({"get_schema","create_project","review_story","preview_frames"}.issubset({t["name"] for t in tools["result"]["tools"]}))
        result=dispatch(self.api,{"jsonrpc":"2.0","id":3,"method":"tools/call","params":{"name":"inspect_project","arguments":{"project_id":"missing"}}})
        self.assertTrue(result["result"]["isError"])
        self.assertIsNone(dispatch(self.api,{"jsonrpc":"2.0","method":"notifications/initialized"}))

    def test_stdio_has_only_protocol_output(self):
        messages='{"jsonrpc":"2.0","id":1,"method":"ping"}\n{"jsonrpc":"2.0","id":2,"method":"tools/list"}\n'
        result=subprocess.run([sys.executable,"-m","animation_kit","--workspace",self.temp.name,"serve"],input=messages,capture_output=True,text=True,timeout=60)
        self.assertEqual(result.returncode,0,result.stderr)
        self.assertEqual([json.loads(line)["id"] for line in result.stdout.splitlines()],[1,2])

    def test_agent_iterations_are_bounded(self):
        class BadProvider:
            def decide(self,context): return {"tool":"inspect_project","arguments":{"project_id":"absent"}}
        response=run_agent(BadProvider(),self.api,"Test bounded repair",max_calls=2)
        self.assertEqual(response["result"]["status"],"budget_exhausted")
        self.assertEqual(response["result"]["calls"],2)

    def test_agent_context_budget_stops_before_provider(self):
        class MustNotRun:
            def decide(self,context): raise AssertionError("Context overflow must stop before the provider")
        response=run_agent(MustNotRun(),self.api,"Test small context",max_context_chars=500)
        self.assertEqual(response["result"]["status"],"budget_exhausted")
        self.assertEqual(response["result"]["calls"],0)

    def test_eval_records_unsupported_without_fake_export(self):
        from evals.evaluate import collect
        workflow=self.api.call("start_workflow",{"brief":"Unsupported verified handover"})["result"]
        ident=workflow["workflow_id"]
        self.api.call("finish_workflow",{"workflow_id":ident,"outcome":"unsupported","summary":"No handover/contact component installed."})
        record=collect(self.temp.name,ident,"unsupported-handover","other-full","test-harness",0)
        self.assertTrue(record["annotated_checks_passed"])
        self.assertIsNone(record["artifact"])
        self.assertTrue(record["human_review_required"])

    def test_eval_does_not_certify_unexported_task(self):
        from evals.evaluate import collect
        ident=self.api.call("start_workflow",{"brief":"Unfinished wave"})["result"]["workflow_id"]
        record=collect(self.temp.name,ident,"delayed-wave","other-full","test-harness",0)
        self.assertFalse(record["annotated_checks_passed"])

    def test_real_encode_cache_and_corrupt_frame_repair(self):
        scene=packaged_json("examples/quiet_wave.json")
        scene["frames"]=24
        scene["actions"]=[]
        scene["shots"][0]["end"]=24
        self.api.store.create("tiny",scene)
        first=render(self.api.store,"tiny")
        self.assertEqual(first["decoded_frame_count"],24)
        self.assertTrue(Path(first["video_path"]).is_file())
        second=render(self.api.store,"tiny")
        self.assertTrue(second["cached"])
        frame=Path(second["manifest_path"]).parent/"frames"/"000004.png"
        frame.write_bytes(b"corrupt")
        repaired=render(self.api.store,"tiny")
        self.assertEqual(repaired["resumed_frames"],23)
        self.assertEqual(repaired["status"],"succeeded")
        image_result=dispatch(self.api,{"jsonrpc":"2.0","id":4,"method":"tools/call","params":{"name":"inspect_artifact","arguments":{"project_id":"tiny","job_id":repaired["job_id"],"frame":4,"include_image":True}}})
        self.assertEqual(image_result["result"]["content"][1]["mimeType"],"image/png")


if __name__=="__main__": unittest.main()
