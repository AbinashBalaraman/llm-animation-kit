---
name: code-animation
description: Turn a script or brief into original code-rendered 2D animation by authoring its artwork, articulated motion and shot sequence, then reviewing the actual output against the request. Use for production with the LLM Animation Kit.
---

Create the requested animation. The host LLM is the writer, illustrator and animator; the kit supplies a general drawing/timeline engine and production tools. There is no default character, set, genre or story. Every frame is conventionally rendered from authored geometry. Video-generation models and synthetic-video enhancement are excluded.

Preserve the user's original brief in `brief.prompt`. Extract visible acceptance requirements from the actual script: subjects, important actions, setting, outcome and tone as applicable. Do not impose a fixed number of shots, a comedy plot, a cat, or any other example's content on a different request. A diagram or abstract animation can be one shot. A longer narrative needs enough shots to communicate its events.

Read `discover_capabilities` and retrieve task guidance with `get_context`. Use `get_schema` for the exact `kit.story/2.0` contract. For terminal authoring, read [the authoring reference](references/authoring.md); it explains local coordinates, reusable art and motion without requiring a huge hand-written JSON file. Host-authored Python may use `animation_kit.authoring` to build JSON. The renderer never executes code inside a scene document.

Plan the visible action before writing geometry. Invent the characters, props and environments the script actually needs. Draw distinctive silhouettes and identifying details; naming a generic shape after the requested subject is insufficient. Build articulated parts as groups with meaningful joint origins. Reuse those authored assets across shots and pose their parts with keyframes. Consult [story and acting guidance](references/story-and-acting.md) for narrative, comedy, continuity and contact.

**Do not load, recolor or retitle a demonstration to fulfil a fresh brief.** `load_example` and `kit.scene/1.0` are archived exercises; production workflows reject them. Example authoring scripts demonstrate how to construct artwork, not which subject or story to deliver. If a visual is missing, author it from vector primitives. If the request exceeds the available backend, explain the specific gap and propose an appropriate code-rendered approach; retain the requested subject and meaning.

Start a `production` workflow using the exact original prompt. Use `workflow_step` for production calls so failures count against the budget. Create a project with your authored story. For edits, inspect its current revision and use `apply_revision` with `replace_shot`, `upsert_asset`, or `replace_story`; invalid changes publish nothing. Undo creates a new revision.

Inspect early, while corrections are cheap. Use `preview_frames` to check identity, layout and story beats. Open the resulting image. Then render `preview` and inspect the clip and critical frame ranges. `check_story` verifies declared coverage and visible geometry; it cannot decide whether the drawing is recognizable or the joke works. Read [the review reference](references/review.md) before approval.

Use `review_story` to report a separate observation and actual preview frames for every requirement. Mark unmet or unreviewed requirements honestly. Declare `playback_reviewed` only if normal-speed playback was actually assessed; sampled frames do not establish motion or sound quality. A host without visual access must finish as `needs_review`, not invent acceptance. Accepted current evidence enables `render_final`; it is a declared review, not independent proof of model parity.

Deliver the MP4, editable source/authoring script, review scope and concrete remaining limitations. Do not claim the requested story succeeded merely because encoding succeeded. For CLI and MCP calling details, read [references/cli.md](references/cli.md).
