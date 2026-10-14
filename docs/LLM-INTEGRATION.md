# Give another LLM the capability kit

The host LLM does the creative work. The package does not hide a remote model, auto-write a story from text or execute code returned by an API. An agent needs a place to author files or emit JSON, permission to run the renderer, and visual access (or a disclosed reviewer).

## Terminal agents

Clone/install the repository and have the agent read `agent-kit/code-animation/SKILL.md`, then its story-development reference before artwork. The host writes and questions a complete story and shot script; `plan_story` structurally checks it before production. Keep it as `scene.direction`. Load the authoring reference when geometry/keyframe syntax is needed. The prose, self-review, generated JSON and render evidence are reviewable artifacts.

## MCP hosts

Configure the stdio entry in `agent-kit/mcp.example.json` with an absolute Python path and workspace. Use `discover_capabilities`, then `get_schema` with `version: direction` to develop the writing plan. `get_context` retrieves guidance without injecting a stock scene. `inspect_artifact`, `preview_frames` and `preview_motion` return PNG content through MCP; the host still needs to inspect it. CLI, MCP and provider loops use the same planning and review gates.

## Optional provider loop

`animation_kit.agent.run_agent` accepts a host-supplied `Provider.decide(context)` method. It enforces iteration/context/workflow budgets. The provider returns a tool decision or finish outcome, not executable scene code. Vendor credentials, network requests and model selection belong to the host. This interface has behavioral tests, not a completed multi-model quality benchmark.

## Plugins and other code renderers

The project consumes general lessons from Remotion's agent skills and frame-based rendering, Motion Canvas's scene/timing model, and installed Tesseract motion/review guidance. These are references, not secretly installed dependencies. See `OVERHAUL-RESEARCH.md` for consulted sources and the plugin discovery result.

A host already using Remotion, Manim, Blender or Tesseract can use the script/story/review principles, but their native documents are not accepted by this renderer. No adapter is claimed without an implementation and actual export test. Do not invent a plugin connection or claim a plugin rendered a clip produced by the local vector engine.
