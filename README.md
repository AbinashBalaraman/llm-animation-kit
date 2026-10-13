# LLM Animation Kit — authored stories, not demo substitution

Give a coding LLM a script. It designs the subjects and settings, writes their artwork and motion, renders previews, and checks the result against the script. **The kit contains no default production character, environment or plot.** All video frames are conventionally drawn by code; no video-generation model is used.

Version **0.2.0** replaces the fixed-puppet production workflow. The old release could render a puppet reliably but could not create the missing artwork/actions a different story needed. Its example-loading behavior encouraged substituting a demonstration for the requested story. That was a product failure, not a successful script adaptation.

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

1. Preserve the original brief and extract visible acceptance requirements.
2. Author artwork, poses, shots and story beats in `kit.story/2.0`.
3. Start a production workflow, create the project, and inspect `preview_frames`.
4. Render `preview`; compare actual frames and playback with each requirement.
5. Submit `review_story`, then export `render_final` and retain editable source.

`check_story` checks authored coverage and visible drawing evidence. It **cannot recognize every subject, judge comedy, or replace visual review**. Acceptance records cite an actual preview and every requirement, and disclose whether playback was assessed. Source or renderer changes invalidate approval.

Production workflows reject `load_example`, legacy scene documents and changed original briefs. The deprecated `kit.scene/1.0` renderer remains only for explicit exercises and regression compatibility. No complete example is automatically injected by context retrieval.

For shell-assisted production, `scripts/produce_story.py prepare --scene YOUR.json --project YOUR_ID` renders evidence. After inspection, `finish --run RUN.json --review REVIEW.json --output OUTPUT_DIR` accepts a reviewer-written record and exports. See [CLI details](agent-kit/code-animation/references/cli.md). This command never manufactures review approval.

## Demonstrations and evaluation

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

## MCP and host integration

Use [mcp.example.json](agent-kit/mcp.example.json) with the absolute virtual-environment Python path and an absolute workspace path. The stdio command is `python -m animation_kit --workspace /absolute/workspace serve`. No global host settings are modified automatically. [Host integration guidance](docs/LLM-INTEGRATION.md) covers portable instructions, MCP and terminal agents.

## Current boundaries

Portable vector 2D; 24/30/60 fps, up to 120 seconds, 40 shots and 2,500 expanded nodes per shot. Output is landscape 640×360 preview / 1280×720 final. No 3D meshes, physics/contact solver, automatic narration/lip-sync, raster imports, nested asset instances or running-job cancellation. Different scripts can require additional conventional rendering capabilities; the agent must disclose those needs instead of substituting a demo. Other-model transfer and normal-speed independent human review are not yet established.

Runtime source: GPL-3.0-or-later. Original example artwork: CC0-1.0. Bundled fonts: SIL OFL 1.1. Dependencies retain their own terms; see [notices](THIRD-PARTY-NOTICES.md).
