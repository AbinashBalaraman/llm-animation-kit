# 0.3.0 — 14 October 2026

Story development now precedes artwork: explicit who/what/when/where/why/how answers, complete prose, causal beats, a shot script and a self-question/rewrite cycle. New `plan_story` validates `kit.direction/1.0`; new productions include it as `scene.direction`. Explainers and abstract pieces remain supported without forced character plots.

New `preview_motion`, text-hidden diagnostics, `motion.arc` and `follow_anchor` help authors inspect and repair actions. Review now requires five quality dimensions and temporal evidence; old approvals cannot authorize new final exports. The drawing backend remains `kit.story/2.0`.

The crocodile/chicken example includes its written story and directing plan. Prior v0.2 examples remain historical artifacts; creating/exporting them under the new workflow requires a plan and a fresh review. No automatic storytelling quality or model-parity claim is made.

# 0.2.0 — 13 October 2026

Production now starts with a script and authored vector artwork. General primitives, hierarchical assets, pose overrides and shot-local keyframes replace the fixed-puppet production vocabulary. There is no default character, setting or plot.

The updated LLM skill covers script interpretation, geometry, articulation, acting, staging and visual review. Context retrieval stops injecting example scenes. Production workflows reject legacy demo loading and preserve the original brief. Review requires actual preview evidence for every requirement and reports whether playback was assessed.

New tools: `get_schema`, `check_story`, `preview_frames`, `review_story`. New revisions: `replace_story`, `replace_shot`, `upsert_asset`. Existing immutable snapshots, optimistic revisions, cache integrity, MCP and workflow budgets remain.

Three separately authored examples exercise character comedy, object animation and an educational diagram. The new evaluation collector separates verified exports from declared visual review and independent quality evidence. No other-model parity result is claimed.

`kit.scene/1.0` and its examples are retained for explicit legacy exercises. New code uses `kit.story/2.0`; see the migration decision and current limits in `docs/IMPLEMENTATION.md`.
