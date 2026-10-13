# 0.2.0 — 13 October 2026

Production now starts with a script and authored vector artwork. General primitives, hierarchical assets, pose overrides and shot-local keyframes replace the fixed-puppet production vocabulary. There is no default character, setting or plot.

The updated LLM skill covers script interpretation, geometry, articulation, acting, staging and visual review. Context retrieval stops injecting example scenes. Production workflows reject legacy demo loading and preserve the original brief. Review requires actual preview evidence for every requirement and reports whether playback was assessed.

New tools: `get_schema`, `check_story`, `preview_frames`, `review_story`. New revisions: `replace_story`, `replace_shot`, `upsert_asset`. Existing immutable snapshots, optimistic revisions, cache integrity, MCP and workflow budgets remain.

Three separately authored examples exercise character comedy, object animation and an educational diagram. The new evaluation collector separates verified exports from declared visual review and independent quality evidence. No other-model parity result is claimed.

`kit.scene/1.0` and its examples are retained for explicit legacy exercises. New code uses `kit.story/2.0`; see the migration decision and current limits in `docs/IMPLEMENTATION.md`.
