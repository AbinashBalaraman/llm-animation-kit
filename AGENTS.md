# Working in this repository

For creating or revising a video, use `agent-kit/code-animation/SKILL.md` and the shared tools. For implementation work, read `docs/IMPLEMENTATION.md` before the older research proposal; the shipped backend is 2D `kit.scene/1.0`, and proposed 3D contracts remain separate.

The product packages instructions, animation knowledge, reusable components, tools and evidence so other LLMs can make animation. Every video frame is produced by code. Video-generation models, synthetic-video enhancement and model-supplied executable code are outside the runtime.

Tool schemas/catalog/examples are built by `scripts/build_catalog.py`; update the source and generated data together. CLI, MCP and the agent loop share `animation_kit.tools.Tools`. Keep canonical scene edits in `Store` transactions. State evaluation must be independent of sampling order. Reports must distinguish technical checks, visual review, and actual model evaluation.

Run `python -m unittest discover -s tests -v` for changes to these mechanics. Preview changed drawing/controllers and inspect temporal evidence. Do not call a schema fixture or mocked tool result a rendered example. Preserve the user scope and record backend/contract changes in implementation decisions.
