---
name: code-animation
description: Develop a clear story through explicit questions, answers and rewrites, then direct and render original code-based 2D animation with the LLM Animation Kit. Use for new productions and story or animation revisions.
---

Create the requested animation. The host LLM is the writer, illustrator and animator; the kit supplies a general drawing/timeline engine and production tools. There is no default character, set, genre or story. Every frame is conventionally rendered from authored geometry. Video-generation models and synthetic-video enhancement are excluded.

Preserve the user's original brief in `brief.prompt`. Extract visible acceptance requirements from the actual script: subjects, important actions, setting, outcome and tone as applicable. Do not impose a fixed number of shots, a comedy plot, a cat, or any other example's content on a different request. A diagram or abstract animation can be one shot. A longer narrative needs enough shots to communicate its events.

Read `discover_capabilities` and retrieve task guidance with `get_context`. Use `get_schema` for the exact `kit.story/2.0` contract. For terminal authoring, read [the authoring reference](references/authoring.md); it explains local coordinates, reusable art and motion without requiring a huge hand-written JSON file. Host-authored Python may use `animation_kit.authoring` to build JSON. The renderer never executes code inside a scene document.

**Write a clear story before drawing.** Read [story development](references/story-development.md). Answer who, what, when, where, why and how; write the complete prose story; question its motivation, causality, stakes, clarity, ending and filmability. Rewrite concrete weaknesses before storyboarding. Translate it into causal beats and a shot script with framing, action, reaction, continuity and duration. The model must do this work itself, rather than passing the entire questionnaire to the user. Preserve an existing screenplay instead of inventing a replacement.

Invent the characters, props and environments that script needs. Draw distinctive silhouettes and identifying details; naming a generic shape after a subject is insufficient. Build articulated parts as groups with meaningful joint origins. Reuse the authored assets and pose their parts with keyframes. Consult [story and acting guidance](references/story-and-acting.md) for staging, continuity and contact.

**Do not load, recolor or retitle a demonstration to fulfil a fresh brief.** `load_example` and `kit.scene/1.0` are archived exercises; production workflows reject them. Example authoring scripts demonstrate how to construct artwork, not which subject or story to deliver. If a visual is missing, author it from vector primitives. If the request exceeds the available backend, explain the specific gap and propose an appropriate code-rendered approach; retain the requested subject and meaning.

Start a `production` workflow using the exact original prompt. Use `workflow_step` for production calls so failures count against the budget. Call `plan_story` with the written `kit.direction/1.0` plan before creating the project; resolve issues and put the exact plan in `scene.direction`. For edits, inspect the current revision and use `apply_revision` with `replace_shot`, `upsert_asset`, or `replace_story`; invalid changes publish nothing. Editorial changes require a matching revised plan and a new `plan_story` call. Undo creates a new revision.

Inspect early. Use `preview_frames` for identity and layout, and `preview_motion` for before/action/after sequences, contacts and reactions. For visual narratives, use `hide_text: true` to expose dependence on captions. Open the images, repair unclear events, then render `preview` and inspect the clip and critical frames. `check_story` verifies declared coverage and visible geometry; it cannot decide whether a drawing is recognizable or a story works. Read [the review reference](references/review.md) before approval.

Use `review_story` to report actual frame evidence for every requirement and for visual clarity, cause and effect, motion/contact, framing and continuity. Mark failures honestly; a single still cannot prove an action. Declare `playback_reviewed` only if normal-speed playback was actually assessed. A host without visual access must finish as `needs_review`. Accepted current evidence enables `render_final`; it is a declared review, not independent proof of model parity.

Deliver the prose story, shot script, MP4, editable source/authoring script, review scope and concrete remaining limitations. Do not claim the story succeeded merely because encoding succeeded. For tool calling details, read [references/cli.md](references/cli.md).
