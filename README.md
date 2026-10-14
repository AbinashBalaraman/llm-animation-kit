# LLM Animation Kit — authored stories, not demo substitution

Give a coding LLM a script. It designs the subjects and settings, writes their artwork and motion, renders previews, and checks the result against the script. **The kit contains no default production character, environment or plot.** All video frames are conventionally drawn by code; no video-generation model is used.

Version **0.3.0** adds a required writing and directing stage. Before drawing, the model answers **who, what, when, where, why and how**, writes a complete story, challenges its weak points, rewrites them and creates a shot script. The earlier workflow could produce recognizable characters while still leaving the story vague. Technical rendering and subject coverage were insufficient.

Read the [story-development guide](agent-kit/code-animation/references/story-development.md) and the new example's [complete story, questions and shot script](examples/stories/crocodile-chicken/story.md). The model does this creative work itself; the tools validate structure and preserve its plan. They do not automatically judge whether the story is good.

## What the LLM can author

- Original vector artwork: ellipses, rounded rectangles, polygons, quadratic/cubic paths and text.
- Articulated assets: nested groups, joint origins, reusable drawings and independent per-instance poses.
- Script-specific motion: position, rotation, scale, opacity and camera tracks with six interpolation choices.
- Multiple sets/shots, captions, story props, timed procedural sound accents and continuous editable source.
- A requirement-to-shot plan, early storyboard images, rendered MP4 previews, actual frame inspection and per-requirement review.

These are general 2D tools. Characters, products, diagrams and abstract scenes use the same engine. A cat election and a toaster launching toast into space are two authored demonstrations—not new runtime presets. New scripts require new creative work by the consuming LLM.

## Try with another LLM

Give it this repository and [the fresh-script testing prompt](docs/TRY-WITH-ANOTHER-LLM.md). It should load [the production skill](agent-kit/code-animation/SKILL.md). The host needs terminal/files access or MCP tools, and visual access for honest review. The kit is not a standalone text-to-video model and makes no automatic claim that every LLM produces excellent animation.

```sh
python -m venv .venv
# Activate the environment, then:
python -m pip install -e .
python -m animation_kit doctor
python -m animation_kit call discover_capabilities
python -m animation_kit call get_schema
```

On Windows use `.venv\Scripts\python.exe` directly if activation is unavailable. Python 3.11+ is supported. Fonts are included. FFmpeg comes through imageio-ffmpeg; an existing verified executable may be selected with `ANIMATION_KIT_FFMPEG`.

The [authoring SDK guide](agent-kit/code-animation/references/authoring.md) explains how a local Python script constructs the scene document. The render server accepts **declarative JSON only**; it does not evaluate executable scene code. Host-authored Python runs with the host's ordinary permissions.

## Production and review

The shared CLI, MCP and provider loop expose the same tools:

1. Preserve the brief. Write the six core answers, complete prose story, causal beats and shot script; question and revise motivation, causality, stakes, clarity, ending and filmability.
2. Start a production workflow and submit `plan_story`. Resolve structural issues before artwork. Include the exact plan in `scene.direction`.
3. Author artwork, poses and shots matching the plan. Create the project and inspect `preview_frames` and `preview_motion`, including text-hidden evidence for visual narratives.
4. Render `preview`; inspect cause and effect, contact, reactions, framing and continuity as well as each brief requirement.
5. Submit `review_story` with requirement and quality evidence, then export `render_final`. Deliver the written story and script alongside the MP4 and editable source.

`check_story` checks authored coverage and visible drawing evidence. It **cannot recognize every subject, judge comedy, or replace visual review**. Acceptance requires observations for each requirement and five quality dimensions. Actions require temporal evidence, and playback scope remains explicit. Source or renderer changes invalidate approval. A model can still write weak answers or misjudge its own output; these gates are not proof of good filmmaking.

Production workflows reject `load_example`, legacy scene documents and changed original briefs. The deprecated `kit.scene/1.0` renderer remains only for explicit exercises and regression compatibility. No complete example is automatically injected by context retrieval.

For shell-assisted production, `scripts/produce_story.py prepare --scene YOUR.json --project YOUR_ID` renders evidence. After inspection, `finish --run RUN.json --review REVIEW.json --output OUTPUT_DIR` accepts a reviewer-written record and exports. See [CLI details](agent-kit/code-animation/references/cli.md). This command never manufactures review approval.

## Demonstrations and evaluation

- [A crocodile and a chicken become friends](examples/stories/crocodile-chicken/README.md): a written story, self-questioning, closer rescue/reaction shots, contact evidence and reciprocal trust. [Authoring script](scripts/create_crocodile_chicken.py).
- [Cat becomes US president](examples/stories/cat-president/README.md): original tabby, campaign, election, office and visual payoff. [Authoring script](scripts/create_cat_president.py).
- [Space toaster](examples/stories/space-toaster/README.md): entirely different subject, setting and action using the same engine. [Authoring script](scripts/create_space_toaster.py).
- [Stack explainer](examples/stories/stack-explainer/README.md): an educational diagram with no character narrative. [Authoring script](scripts/create_stack_explainer.py).
- [Fresh-script evaluation](evals/README.md): test unseen scripts, preserve prompts, record failures and require independent review to make quality comparisons.
- [Verification and known limits](docs/VERIFICATION.md); [design decisions](docs/IMPLEMENTATION.md); [web/plugin research](docs/OVERHAUL-RESEARCH.md).

```sh
python -m unittest discover -s tests -v
python scripts/build_catalog.py
```

The catalog command regenerates schemas, recipes and authored example sources. Rendered demonstrations are produced separately through the normal tools. Software tests and demonstrations do not establish parity between models.

The three v0.2 films and their review records remain historical evidence. Their saved sources are still readable, but a new production/export under v0.3 requires an authored `direction` plan and the new quality review. Add a plan when adapting them; do not relabel an old approval as a current review.

## MCP and host integration

Use [mcp.example.json](agent-kit/mcp.example.json) with the absolute virtual-environment Python path and an absolute workspace path. The stdio command is `python -m animation_kit --workspace /absolute/workspace serve`. No global host settings are modified automatically. [Host integration guidance](docs/LLM-INTEGRATION.md) covers portable instructions, MCP and terminal agents.

## Current boundaries

Portable vector 2D; 24/30/60 fps, up to 120 seconds, 40 shots and 2,500 expanded nodes per shot. Output is landscape 640×360 preview / 1280×720 final. No 3D meshes, physics/contact solver, automatic narration/lip-sync, raster imports, nested asset instances or running-job cancellation. Different scripts can require additional conventional rendering capabilities; the agent must disclose those needs instead of substituting a demo. Other-model transfer and normal-speed independent human review are not yet established.

Runtime source: GPL-3.0-or-later. Original example artwork: CC0-1.0. Bundled fonts: SIL OFL 1.1. Dependencies retain their own terms; see [notices](THIRD-PARTY-NOTICES.md).
