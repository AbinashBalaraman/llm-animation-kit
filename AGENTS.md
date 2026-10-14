# Working in this repository

For creating or revising a video, use `agent-kit/code-animation/SKILL.md` and the shared tools. For implementation work, read `docs/IMPLEMENTATION.md` before the older research proposal. New productions use authored vector 2D `kit.story/2.0`; `kit.scene/1.0` is a legacy exercise backend, and proposed 3D contracts remain separate.

The product packages instructions, animation knowledge, reusable components, tools and evidence so other LLMs can make animation from their scripts. Every frame is produced by code. Video-generation models, synthetic-video enhancement and executable code inside scene documents are outside the runtime. Host-authored scripts may use the general SDK to build declarative geometry/timelines. Never put a story-specific character or plot in the engine or substitute an example for a new brief.

Tool schemas/catalog/examples are built by `scripts/build_catalog.py`; update the source and generated data together. CLI, MCP and the agent loop share `animation_kit.tools.Tools`. Keep canonical scene edits in `Store` transactions. State evaluation must be independent of sampling order. Reports must distinguish technical checks, visual review, and actual model evaluation.

Before production artwork, develop and self-question a complete story and shot script with `plan_story`; preserve its `kit.direction/1.0` plan in `scene.direction`. Use the story-development reference for who/what/when/where/why/how and concrete rewrites. Inspect temporal action evidence and review cause/effect, contact, framing and continuity as well as brief coverage. Structural checks do not certify creative quality.

Run `python -m unittest discover -s tests -v` for changes to these mechanics. Preview changed drawing/controllers and inspect temporal evidence. Do not call a schema fixture or mocked tool result a rendered example. Preserve the user scope and record backend/contract changes in implementation decisions.
