# Research scope and reproducibility record

External sources checked 12 October 2026. Report assembly/consistency review completed 13 October 2026. The source dates in the two evidence memos describe the original research pass; prices and API availability must be rechecked when actually used.

Methods used: official documentation and repository README/license reads; selected source-file inspection; GitHub API metadata reads; authors' paper abstracts/HTML; contract-fixture validation described separately in `../contracts/VALIDATION.md`. No repository installer was run. No scene renderer or hosted/local video model was exercised. No generated videos were viewed or ranked.

Selected repository metadata captured through the GitHub API:

| Repository | Branch snapshot | Commit time (UTC) | Observed status / license metadata |
|---|---|---|---|
| showlab/Code2Video | `1142d8e14cdc2806df85aedb0fbb5dca474caa0f` | 2026-08-24 11:00:47 | Not archived; MIT |
| ahujasid/mcp-for-blender | `7a0373ec9199183cb460068c4f96aed9c579fb4f` | 2026-10-06 15:07:57 | Not archived; MIT repository declaration |
| ggml-org/llama.cpp | `8bb3cf0d216a5ae48360179f2931daf284be4d01` | 2026-10-12 14:39:55 | Not archived; MIT |
| AcademySoftwareFoundation/OpenTimelineIO | `00c22fa3a64256d8d3dcafbc7276492185dd970d` | 2026-10-09 04:57:59 | Not archived; Apache-2.0 |
| morluto/rea | `428eee00fdd0406cdf2b734c9ea14a2bb02da279` | See pinned repository history | Selected source/package inspection; MIT-authored code plus other terms |

These snapshots are provenance aids, not selected production dependencies or maintenance guarantees. The report links inspected Code2Video and Blender-bridge source to the captured commits. The REA evidence memo pins its package, protocol and implementation sources. Sources linked to moving branches must be locked and validated by the implementation task that adopts them.

The official Code2Video agent implementation was inspected for per-section generation, render/debug retries, visual feedback and usage tracking. The Blender bridge's `execute_code` method was inspected for its direct Python execution surface. This is a limited functional inspection, not a security audit. Blender/Rigify and graphics-library example inspections are documented in the core evidence memo.

Reference-film production articles were used to understand workflow and limitations. No user-supplied video references were available, so there is no evidence here of perceptual parity with a specific online clip. Paper and vendor quality claims were not independently reproduced.

The report was independently reviewed for comparison fairness and architecture consistency. Corrections included aligning the canonical pilot, requiring planner intent fulfillment, deriving action constraints from trusted definitions, specifying affordance information, clarifying vetted driver policy, and distinguishing Blender worker/UI boundaries.

On 13 October 2026 the user clarified that avoiding video-generation models is the purpose of the project. The earlier optional enhancement recommendation was an incorrect interpretation and has been removed. The report, architecture diagram, roadmap, ADR-008, task T14, agent instructions and supporting evidence now enforce zero video-generation models in the product. Research about those models is retained strictly for external comparison. An independent read-only audit found no video-generation hooks in the existing schemas or fixtures; those files were not changed, and the prior 45-check result remains a contract-fixture result rather than evidence of a working renderer. The delivery ZIP was refreshed with these corrections.

The user further clarified that the main product should enable other LLMs through packaged instructions, tools, components and expert knowledge. `LLM-ANIMATION-KIT.md` now defines that objective, separates production-time skills from coding-agent development prompts, specifies a bounded preview/repair workflow and adds K00–K04 plus H09 for capability-transfer evaluation. The report's T12 work now starts alongside the engine instead of deferring the whole model-facing layer. These are design changes, not evidence of a working kit or parity between models. Existing contract/schema/fixture bytes remain unchanged; no new external research or model runs were required for this clarification.
