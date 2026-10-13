---
name: code-animation
description: Create and revise code-rendered 2D character animation using the LLM Animation Kit tools, recipes and editable scenes. Use for video production with this kit.
---

Use the installed animation kit to turn a brief into an editable scene and video. Every frame must come from code, assets, animation and conventional rendering. Video-generation models are excluded.

Discover the tools/capabilities before planning. The shipped backend has one original front-view 2D puppet, gaze, expressions, three gestures, bounded movement, simple props, shot cameras and procedural sound. Other rigs/actions are missing capabilities, not invitations to invent tool fields.

Load `get_context` for the current task. Use its recipes and examples selectively: camera when framing, reaction when acting, timing when revising. The exact schema comes from `discover_capabilities`; tools are listed by the host or `python -m animation_kit tools`.

Start a workflow with an explicit tool/render budget. Use `workflow_step` for production calls so unsuccessful attempts consume budget too. Create a scene or load an example, inspect the project, then apply named-ID revisions with its current revision. Frames are zero-based at 24 fps; intervals are half-open. Gaze, root and expressions persist; gestures return to rest. Overlapping actions on the same channel fail.

Render a preview and inspect its playable clip and temporal contact sheet/action-boundary frames. A screenshot cannot establish motion quality. Vision-capable hosts can request `inspect_artifact` with `include_image: true`; text-only hosts need a disclosed visual reviewer for appeal. Technical diagnostics are useful evidence, not aesthetic approval.

Repair the smallest relevant input. For a camera change preserve actions; for a delay explicitly identify related beats rather than silently shifting the whole scene. Invalid transactions leave the project unchanged. Stop at the workflow budget and record unresolved limitations.

Record a review for the actual current revision before `render_final`. State who reviewed and what they observed. A model review is not an independent parity result. Finish with the exported video, editable source, known limits and any human help. Never mark a workflow complete without the successful final export.

For shell hosts without MCP, read [references/cli.md](references/cli.md). For what to inspect visually, read [references/review.md](references/review.md).
