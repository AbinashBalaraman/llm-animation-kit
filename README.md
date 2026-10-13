# LLM Animation Kit

A working first version of the reusable knowledge/tool system for other LLMs to create and revise code-rendered animation. It includes a production skill, six task-specific recipes, three editable example scenes, a native 2D puppet/component library, strict validation, atomic revisions, previews, temporal evidence, review records, MP4 export, MCP stdio and bounded workflow memory. No video-generation model is used.

**Trying this with another LLM?** Start with [the ready-to-use evaluation prompt](docs/TRY-WITH-ANOTHER-LLM.md), then load [the production skill](agent-kit/code-animation/SKILL.md).

The consuming LLM provides direction. Tested code provides the puppet, gestures, expressions, gaze, motion, camera, drawing and encoding. The first backend is original stylized 2D art; Blender/3D interactions remain planned work, recorded in `docs/IMPLEMENTATION.md`.

## Run

Python 3.11+ and the package dependencies are required. FFmpeg comes through imageio-ffmpeg; set `ANIMATION_KIT_FFMPEG` to use another verified executable.

```powershell
python -m venv .venv
.\.venv\Scripts\Activate.ps1
python -m pip install -e .
python -m animation_kit doctor
python -m animation_kit tools
python -m animation_kit call discover_capabilities
```

On macOS/Linux, activate with `source .venv/bin/activate`. On Windows, activation is optional: use `.venv\Scripts\python.exe` for the commands if script activation is unavailable.

Create `arguments.json` containing `{"project_id":"my-scene","example_id":"discovery"}` then run:

```powershell
python -m animation_kit call load_example --input arguments.json
```

Use `{"project_id":"my-scene"}` as the arguments file for `inspect_project` or `preview`. Read exact tool schemas with `tools` before editing. `preview` returns an MP4, contact sheet, trace and source; inspect the result, record a review for the current revision, then call `render_final`. Revisions invalidate review. The default persistent workspace is `.kit-workspace`; set `--workspace` before the command to choose another directory.

## Give the kit to another LLM

Load [the production skill](agent-kit/code-animation/SKILL.md) into a host that supports files/CLI, or expose the same tools over MCP stdio. Example configuration after package installation:

```json
{
  "mcpServers": {
    "animation-kit": {
      "command": "python",
      "args": ["-m", "animation_kit", "--workspace", "/absolute/path/to/animation-workspace", "serve"]
    }
  }
}
```

Change the Python executable and workspace for your host. This repository does not alter host configuration automatically. MCP supports initialize, ping, tools/list, tools/call and explicit PNG image results, using the [official tool contract](https://modelcontextprotocol.io/specification/2025-11-25/server/tools) and [stdio transport](https://modelcontextprotocol.io/specification/2025-11-25/basic/transports). Rendering is synchronous and bounded, with no running-job cancellation API in this version.

Use [mcp.example.json](agent-kit/mcp.example.json) as a template. Set `command` to the absolute Python executable inside your project's virtual environment, and choose an absolute workspace path. Copy the entry into the chosen host's MCP settings.

Use `start_workflow` and `workflow_step` to enforce call/render budgets. Direct tools are also available for expert authoring. The Python `run_agent` loop accepts a provider's typed decisions and records a durable workflow; it does not assume a vendor API or execute model-supplied code.

## Examples and verification

[Worked examples](examples/golden/README.md) contain actual previews, source and revision records. Run the same examples with `python scripts/render_examples.py`. [Behavioral tests](tests/test_kit.py) cover validation, transactions, targeted edits, workflow limits, MCP and actual encoding/cache recovery:

```powershell
python -m unittest discover -s tests -v
```

[The benchmark harness](evals/README.md) records model-produced runs on held-out briefs. No multi-model parity experiment has been run. Tests and authored examples establish working software, not equivalence to a stronger model.

[Release verification](docs/VERIFICATION.md) records the actual checks, packaging smoke test, render measurements and review limits.

Current support: one front-view puppet rig; up to four characters, eight simple props and eight shots; 24 fps; clips up to 60 seconds; preview 640x360, final 1280x720; look_at, expression, gesture (wave/reach/celebrate), and move_to. It does not yet support Blender, arbitrary asset imports, handover, seating, speech/lip-sync or physical contact. Export directories retain editable JSON and checked frame/source manifests.

Runtime source is GPL-3.0-or-later. Original procedural artwork and authored example scenes are CC0-1.0; dependency and FFmpeg-build terms remain separate. See `LICENSES/` and `THIRD-PARTY-NOTICES.md`. No executable FFmpeg or third-party weights are bundled in this repository.
