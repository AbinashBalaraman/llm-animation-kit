# Implemented release and boundaries

13 October 2026. Release 0.1.0 is an operating local 2D capability kit. The research handoff remains useful background; its proposed 3D contract/rig profile was not silently reinterpreted.

**ADR-014:** ship the first consumable capability kit on an original native 2D renderer because the host has Python/Pillow and a usable wheel-supplied FFmpeg, while Blender is absent. This is a recorded implementation choice under the user's request to implement the kit. All frames are drawn by reviewed code. Blender remains future backend work, rather than a hidden prerequisite or falsely advertised capability.

The runtime uses a separate `kit.scene/1.0` contract with 960x540 design-pixel coordinates and a front-view puppet. It does not claim compatibility with the research package's proposed metre-based 3D `studio.schema.json`. The latter's 45 fixture checks are independent of the runtime tests.

Implemented: consuming production skill; indexed bounded recipe/context retrieval; original puppet, stage, prop, camera and four action components; strict schema and selected semantics; immutable snapshots, atomic transactions and undo; native frame/video rendering; verified cache/resume; temporal contact sheets, state traces and editable exports; explicit review records; shared CLI/MCP tools; durable workflow budgets; provider-independent agent loop; benchmark collection/scoring tooling.

Not yet implemented: 3D adapter, compatible Blender rigs/performance library, handover/seating, speech/lip-sync, physical contact, asynchronous cancellation, vendor model adapters and completed comparative model evaluation. The generic provider loop and host tools can be used by another LLM now, but actual transfer results must be collected. The provided actor movement is stylized and is not certified physical locomotion.

Render cache keys include the full scene, profile, renderer/component source, Pillow and FFmpeg build strings. This version conservatively rerenders changed scenes; it does not yet provide per-shot dependency caching. Resume reuses verified frames and rechecks every output. A crashed writer may leave a lock; investigate the recorded PID before removing it. The kit operates within a configured workspace but is not an OS sandbox for untrusted plugins.
