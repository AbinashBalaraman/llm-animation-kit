# Implementation decisions

## ADR-016: write and question the story before geometry

14 October 2026. Release 0.3.0 retains the authored vector 2D `kit.story/2.0` drawing backend and introduces the nested writing contract `kit.direction/1.0`. This is not a 3D contract or a video-model pipeline.

The next user-supplied transfer clip depicted a crocodile, chicken and egg but relied on captions for an ambiguous rescue and an abrupt friendship. The user clarified that proper story development must precede animation: the model should ask and answer who, what, when, where, why, how and story-specific questions itself.

The host must now supply six concrete answers, a complete prose story, causal beats, a shot script and a self-review of motivation, causality, stakes, clarity, ending and filmability. `plan_story` validates the host's work; it does not generate answers or certify creative quality. Narrative plans require setup/turn/resolution and cannot skip those questions; explainer and abstract modes permit justified inapplicable checks. Unresolved rewrites block structural readiness.

New project creation requires `scene.direction`. Production workflows require a successful `plan_story` call with the exact plan before creation or rendering. Plan and scene must preserve the same prompt and ordered shot IDs/durations; editorial changes require revalidation. The direction schema is optional only for reading historical v0.2 sources. Explicit legacy exercise loading does not bypass the new final-production gate.

`preview_motion` renders bounded temporal strips; `hide_text` provides a diagnostic without altering canonical data. `review_story` version 2 requires separate evidence for visual clarity, cause/effect, motion/contact, framing and continuity. A passed motion review needs three distinct rendered frames, including a nearby pair in one shot. Historical reviews cannot approve a new final export. These are evidence and declaration requirements, not a semantic oracle or an independent audience rating.

Host-side `motion.arc` and `follow_anchor` compile ordinary tracks for trajectories and contact points. There is still no physics solver, runtime scene code or video-generation model. The revised crocodile/chicken example is authored with these tools; its specific artwork and plot remain outside the engine. Reports distinguish software tests, author-reviewed pixels and actual other-model evaluation.

13 October 2026. Release 0.2.0 introduces `authored2d_v2` / `kit.story/2.0` as the production path.

## ADR-015: scripts require authoring, not a finite puppet menu

The first transfer attempt took a cat-president brief and produced humanoid puppets on the example's night stage. The v1 system offered one rig, one environment and three gestures; it had no way to create the requested subjects or events. Example retrieval and a generic acceptance note let a technically valid result be mistaken for completing the brief.

The replacement exposes general vector geometry, local coordinate hierarchies, reusable static assets, instance-specific articulated poses, shot-local keyframes, cameras and timed sound cues. Nothing in the engine names a cat, president, toaster, campaign or other story content. Original drawings and narrative decisions live in host-authored scripts and exported JSON. The Python authoring SDK constructs declarative data; the CLI/MCP renderer does not execute scene-supplied code.

Each document preserves its original brief, reviewable requirements, shot purposes and visual evidence beats. A production workflow cannot load legacy examples, accept the legacy backend or silently switch prompts. Context retrieval no longer injects an entire demo scene. Missing artwork is authored; missing backend capabilities are reported specifically.

`preview_frames` supports inexpensive drawing/timing inspection. `check_story` checks planned drawing visibility, not meaning. `review_story` requires a current rendered preview and an observation with actual frames for every requirement. It rejects absent, title-only and invisible evidence; it does not certify semantic correctness or detect every occlusion. Review scope is explicit. The final gate checks source, preview integrity and renderer/font fingerprint. Self-review remains self-review.

The reusable knowledge and host instructions now describe script interpretation, shape construction, articulation, acting, continuity, physical contact authored by hand, comedy where appropriate and prompt-based review. They do not impose the regression example's plot on unrelated scripts.

## Compatibility and invariants

`kit.scene/1.0` remains an explicit legacy exercise path. Its tools/tests preserve existing snapshots, while new project creation requires v2 unless `legacy_exercise: true` is deliberately supplied. Production workflows still reject it. Proposed research 3D schemas remain separate; this release does not claim Blender compatibility.

CLI/MCP/provider adapters share `Tools`. Store mutations validate before atomically publishing immutable hashed snapshots. Undo is a new revision. Every frame is evaluated directly from its frame number and source, independent of sampling order. Render cache keys include source, renderer, components, fonts, Pillow and FFmpeg. Existing verified frames can resume interrupted work. Invalid/corrupt artifacts fail checks.

## Current limits

This is a general authored vector 2D backend, not an unrestricted film engine. No full 3D, automatic physical simulation, voice/lip-sync, external raster assets, nested asset instances, offscreen group-opacity compositing or asynchronous cancellation. Output is fixed landscape 16:9. Paths support M/L/Q/C/Z, with independent filled contours. Camera/keyframe values are bounded. A crashed writer may leave a lock; investigate the PID before removing it. The kit is not an OS sandbox for host-authored scripts.

## Historical ADR-014

0.1.0 shipped the original native 2D puppet because Python/Pillow/FFmpeg were available and Blender was not. That decision established a working renderer and transaction/tool infrastructure, but the closed artwork/action vocabulary did not fulfil the broader LLM capability-transfer goal. Its 24 tests and original examples were real technical evidence, not evidence of general script adaptation or professional quality. The older research proposal is background, not the current production API.
