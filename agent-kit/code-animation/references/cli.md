# CLI and MCP production

Install in a Python 3.11+ virtual environment using `python -m pip install -e .`; run `python -m animation_kit doctor`. Fonts are packaged; FFmpeg comes from imageio-ffmpeg. Rendering needs no hosted model/account.

`python -m animation_kit tools` prints tool schemas. Call with `python -m animation_kit --workspace .kit-workspace call TOOL --input arguments.json`. Use real JSON files for shell-safe arguments. `get_schema` defaults to v2; `{'version':'legacy'}` is for old exercises only.

1. Write a complete story and self-question it using `references/story-development.md`. Retrieve `get_schema` with `version: direction` for its contract.
2. `start_workflow` with the original brief and a call/render budget, e.g. 36 calls and 8 renders. Keep its `workflow_id`.
3. Use `workflow_step` with `workflow_id`, `tool`, and `arguments`. Nested tool failures appear in `result.response`; inspect that result too.
4. Call `plan_story` with the finished plan. When structurally ready, author artwork and include that plan as `scene.direction`. `create_project` takes `project_id` and the authored document as `scene`. `check_story` checks structural evidence; `preview_frames` and `preview_motion` render images; `preview` encodes an MP4.
5. `inspect_artifact` takes project and preview `job_id`. Add `frame` and `include_image: true` for an explicit PNG in a vision-capable MCP host.
6. Use `review_story`, `render_final`, then `finish_workflow` with a truthful outcome: `complete`, `needs_review`, `unsupported`, or `budget_exhausted`.

For a shell workflow, `scripts/produce_story.py prepare --scene YOUR.json --project YOUR_ID` creates/previews through those tools and returns a run file. After actual inspection, write the review fields described in `review.md` (the run supplies project/revision/job identity), then run `scripts/produce_story.py finish --run RUN.json --review REVIEW.json --output OUTPUT_DIR`. It never manufactures approval. Rejected work needs repair and a new preview through the shared tools.

For MCP, run `python -m animation_kit --workspace /absolute/workspace serve` as stdio; see `agent-kit/mcp.example.json`. Configure the host with the absolute virtual-environment Python path.

The server consumes JSON and does not execute model-supplied scene code. Authoring Python is ordinary code running in the chosen host, with that host's permissions; the kit does not sandbox it. The package calls no LLM unless a consuming application supplies a provider to its optional agent loop.
