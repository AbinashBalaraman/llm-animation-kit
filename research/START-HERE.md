# LLM animation capability kit — research and design

Completed 13 October 2026; external research checked 12 October 2026.

**Implementation now available:** see [the working repository](../README.md) and [release boundaries](../docs/IMPLEMENTATION.md). The first operating backend is native 2D with its own `kit.scene/1.0` contract. The proposed Blender/3D components below remain future work. The research fixture validation and runtime verification are separate.

**Hard requirement: no video-generation models.** All frames are produced through code, editable assets, animation, rendering and conventional compositing. LLMs may translate instructions into structured scene data. Video models appear in the research only as external comparison targets; there is no enhancement or hybrid-generation path in the product or roadmap.

Start with [the LLM animation capability-kit design](LLM-ANIMATION-KIT.md). The main product packages instructions, knowledge, tools, reusable components, examples and feedback so other LLMs can produce better animation. The renderer is infrastructure inside that product. Model parity remains a target to evaluate.

Then read [the architecture and implementation report](animation-studio-architecture.md). It contains the A–J research deliverables, a concrete stack decision, production architecture, fair comparison plan, and dependency-aware implementation tasks.

- [Data contracts and semantics](contracts/CONTRACTS.md)
- [JSON Schema bundle](contracts/studio.schema.json)
- [Representative project fixture](contracts/examples/project.json)
- [Validation results](contracts/VALIDATION.md)
- [Core component evidence](evidence/core-components.md)
- [Video models and REA evidence](evidence/video-models-and-rea.md)
- [Fixed implementation decisions](DECISIONS.md)
- [Task status](IMPLEMENTATION-STATUS.md)
- [Coding-agent template](CODING-AGENT-TEMPLATE.md)

This is a specification package, not a working capability kit or animation application. The included asset descriptors are synthetic contract fixtures. No real animation or model-comparison videos have been generated. Begin K00 (knowledge/tool and evaluation design), T00 (visual/toolchain feasibility) and T01 (contract loader) together. Test another LLM on a small real scene as soon as tools work; retain the 20-second three-shot proof for interaction/continuity qualification.
