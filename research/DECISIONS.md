# Proposed implementation baseline

Design 0.1.0 • 13 October 2026 • Status: specification, application not implemented.

| ID | Decision | Rationale | Change requires |
|---|---|---|---|
| ADR-001 | Python orchestration + Blender worker + FFmpeg finishing | Minimal core with real editable character animation | Renderer/worker contract and fixture migration |
| ADR-002 | JSON production document is authoritative for story/state; native `.blend` assets are authoritative for authored art/rig/clip data | Rebuildable shots without losing artist-authored content | Storage and override migration |
| ADR-003 | Scene time is zero-based integer half-open frames, rational fps; 48 kHz audio | Explicit timing and edit semantics | Versioned migration and boundary tests |
| ADR-004 | Metres, right-handed Z-up, character +Y, quaternion xyzw | Consistent asset and rig integration | Import conversion and schema migration |
| ADR-005 | One approved humanoid rig profile and seven action families initially | Testable supported capabilities | New profile/action contracts and visual tests |
| ADR-006 | LLM outputs are validated scene data; reviewed implementations execute actions | Bounded repair and repeatability | Explicit new execution design |
| ADR-007 | Immutable assets and project snapshots; expectedRevision transactions | Reliable rollback, continuity and concurrency | Transaction/migration tests |
| ADR-008 | Zero video-generation models in the product, including optional enhancement, video-to-video refinement and generative frame interpolation | User's explicit purpose: code, assets, rigs, animation and conventional rendering produce the video | Only an explicit user change of scope; quality experiments cannot override this requirement |
| ADR-009 | Validate tools with direct structured inputs; develop the knowledge/tool/planner lane alongside the engine | Distinguish renderer quality from capability transfer while testing both early | Written alternative experiment |
| ADR-010 | Human art direction and performance cleanup are explicit work | Engine capability does not equal appealing automated output | Evidence, not a marketing assertion |
| ADR-011 | Proposed GPL-3.0-or-later application; each dependency/asset/model retains its own terms | Simple intended Blender-compatible distribution | Actual package-level license review |
| ADR-012 | Main product is an animation capability kit for other LLMs: instructions, knowledge, verified examples, tools, components and feedback | User wants expertise made reusable by other models, not only an animation application or prompts for coding its implementation | Explicit user scope change |
| ADR-013 | Measure transfer using held-out tasks, a stronger reference and the same target model with/without the full kit | Comparable performance is an empirical target; prompts cannot guarantee general model parity | Preregistered evaluation change and disclosed evidence |
| ADR-014 | First shipped kit uses original procedural 2D art and a separate kit.scene/1.0 contract; Blender/3D remains planned | Deliver a functioning portable capability kit on the available runtimes; see ../docs/IMPLEMENTATION.md | Backend-specific contract, reviewed assets/components and qualification evidence |

These decisions guide future coding tasks. An agent must record a deliberate change, affected interfaces, migration and tests; it must not silently replace the architecture. Implementation status is in IMPLEMENTATION-STATUS.md. The detailed semantics in contracts/CONTRACTS.md and schema files take precedence over abbreviated examples.
