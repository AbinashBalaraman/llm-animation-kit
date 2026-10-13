# Video-model alternatives, REA, and a fair comparison protocol

Source check: **12 October 2026**. Scope: public documentation, published research, and one REA source file inspected. No model was run, repository installed, API purchased, or output benchmarked. **Documented** below means the cited source states the capability; it is not independent verification of quality. **Inference** means an engineering judgment to test.

**Product boundary clarified 13 October 2026:** the studio excludes video-generation models entirely, including optional refinement. This memo retains them as external comparison targets because the user asked how code-driven animation compares with them. None of the model capabilities below is a proposed product dependency or enhancement path.

## What a better system must beat

The opportunity is a production system with persistent, editable scene state: characters, rigs, props, relationships, action timing, camera curves, lighting, and revisions. Current generative video already has references and editing. A comparison that labels all video models uncontrollable would be misleading. The defensible hypothesis is that a structured studio can improve reproducibility, exact revision scope, recurring-cast production, and cost per accepted shot within a chosen visual style. General cinematic or photorealistic superiority is unproven.

## Hosted comparators

### Gemini Omni Flash

**Documented:** Google's video landing page recommends Omni Flash as the default and presents conversational editing and combined multimodal reasoning as advantages. Its superiority language is Google's claim, not our benchmark. [Video overview](https://ai.google.dev/gemini-api/docs/video)

The detailed guide currently names `gemini-omni-1.1-flash`, supports generated audio, image/video references, natural-language multi-turn editing, first/last-frame tags, and video extension. Output defaults to 720p; 1080p and 4K are described as upscaled. Uploaded editing/extension inputs are limited to ten seconds; the extension guidance describes continuing generated videos to forty seconds. The limitations say uploaded audio references and voice editing are unsupported. This is narrower than the general multimodality description. The landing page's recommendation of Veo for extension also does not mean Omni lacks extension: the detailed guide now documents it. Any separately requested external benchmark must verify the exact available API/version rather than assume that summary pages are synchronized; this is not a studio adapter proposal. [Omni generation/editing guide](https://ai.google.dev/gemini-api/docs/omni)

**Inference:** Include Omni in the edit-locality benchmark, especially changing an object or camera while preserving other scene details. Natural-language editing does not itself expose a reusable rig or editable 3D scene.

### Veo 3.1

**Documented:** Native audiovisual generation; 4/6/8-second clips; up to three image references; first/last-frame conditioning; extension of previously generated Veo video. Reference-image and 1080p/4K generation require eight seconds. The documentation explicitly says the seed does not guarantee determinism. [Veo API guide](https://ai.google.dev/gemini-api/docs/veo)

**Inference:** A relevant comparator for cinematic appearance, sound, and visual variety. Reference conditioning should be tested for continuity rather than equated with fixed identity. No reviewed documentation establishes deterministic object-contact constraints or delivery of an editable scene graph.

### Runway Gen-4.5 and Aleph 2.0

**Documented:** Gen-4.5 supports text/image-to-video, 2–10-second clips, 720p, and 24/25fps. The reviewed Gen-4.5 specification did not establish native audio, so this memo does not claim audio parity with Veo. [Gen-4.5 specifications](https://help.runwayml.com/hc/en-us/articles/46974685288467-Creating-with-Gen-4-5)

Aleph 2.0 powers Edit Studio. It can use an edited keyframe and references to change objects, characters, backgrounds, lighting, or style, with optional motion instructions. Edits can target a selected time range; the guide covers input sequences up to thirty seconds. These are substantial existing editing capabilities. [Edit Studio guide](https://help.runwayml.com/hc/en-us/articles/51683104370451-Creating-with-Edit-Studio)

**Inference:** Benchmark targeted semantic edits against Aleph, including untouched regions and later shots. A structured studio must offer more than a background-replacement prompt.

### Cost anchors, not a production quote

Current official USD rates: Omni Standard charges by tokens, approximately **$0.10/output second at 720p**, plus input/text costs. Veo 3.1 Standard is **$0.40/second at 720p/1080p**; Fast is **$0.10 at 720p** and **$0.12 at 1080p**. [Google pricing](https://ai.google.dev/gemini-api/docs/pricing)

Runway API credits cost $0.01 each: Gen-4.5 uses twelve credits per second (**$0.12**); Aleph uses twenty-eight (**$0.28**, two-second minimum). Provider, format, and resolution can change charges. [Runway API pricing](https://docs.dev.runwayml.com/guides/pricing/)

One accepted sixty-second output is not necessarily sixty purchased seconds. Track all discarded generations, edit passes, asset creation, sound, upscaling, and human correction. Avoid using subscription marketing limits as API unit costs.

## Local / open-weight candidates

| Candidate | Documented capability and deployment | Practical interpretation |
|---|---|---|
| Wan2.2 TI2V-5B | Text/image-to-video at 720p/24fps. Official offloaded example requires at least 24GB VRAM. Repository reports a five-second 720p generation under nine minutes on a consumer GPU. | Permissively licensed local baseline; the vendor runtime claim requires reproduction on the user's hardware. |
| Wan2.2 A14B / S2V-14B | Larger model examples specify 80GB VRAM. Speech-to-video accepts audio and image with optional pose video; duration can follow input audio. Repository models use Apache 2.0. | Pose/audio conditioning is relevant, but not a complete interaction planner. Wan2.2 is this specific open release, not a claim about the latest hosted Wan. |

[Official Wan2.2 repository, requirements and license statement](https://github.com/Wan-Video/Wan2.2)

**LTX-2.5 — documented:** The current model card describes synchronized audio/video, native multishot generation, configurable frame count, keyframe image conditioning, and trainable weights. It also acknowledges that prompts may not be followed perfectly. Multishot identity claims remain vendor claims until evaluated. [Official model card](https://huggingface.co/Lightricks/LTX-2.5)

The inference repository lists keyframe interpolation, IC-LoRA transformations, and audio-to-video pipelines. Its higher-fidelity DFR path uses added detailing and more memory/runtime. [Official inference repository](https://github.com/Lightricks/LTX-2)

The desktop app's local Windows/Linux floor is a CUDA GPU with at least 15 GiB VRAM; it recommends 32GB system RAM and describes about 72GB of disk for the 2.5 core pack. These are app admission requirements, not a promise that every duration/resolution/pipeline fits. Local 2.5 Fast lacks the local Retake/Extend support documented for 2.3 Fast. [Desktop requirements and feature matrix](https://github.com/Lightricks/LTX-Desktop)

LTX weights use the **LTX-2.x Community License**, with a paid commercial license requirement for entities at or above $10M annual revenue and additional conditions, including fine-tune distribution. The desktop app's Apache license does not replace weight terms. [Model license](https://github.com/Lightricks/LTX-2/blob/main/LICENSE-2_x)

**Inference for external comparison only:** hardware ownership removes per-call billing, not electricity, GPU time, maintenance, or revision cost. Do not make a minimum-spec promise before measuring actual assets, frame counts, resolution, precision, and offload settings. These model requirements are not requirements for our studio; no local video-generation backend will be added.

## Related hybrid research, excluded from the product

I2V3D (ICCV 2025) is relevant related work: a coarse 3D scene and conventional animation/camera controls provide guidance; an image model refines keyframes; geometry-guided video interpolation fills between them. The authors demonstrate object/camera manipulation from coarse renders. Its generative refinement and frame synthesis are outside our architecture. Its results do not establish that a wholly code-rendered system will match the same appearance. [Paper](https://arxiv.org/abs/2503.09733), [authors' project](https://bestzzhang.github.io/I2V3D/)

**Required implementation boundary:** every output frame is produced from editable assets, explicit animation and conventional rendering/compositing. Quality improvements come from character design, rig deformation, authored/retargeted motion, procedural controllers, contact correction, expressive timing, camera, lighting and materials. There is no video-model refinement, generated-frame interpolation, or fallback. An optional text LLM translates direction into validated scene data; it does not synthesize final pixels.

## Supplied REA repository

**Documented role:** REA is an agent/CLI investigation tool for binaries, JavaScript/Electron applications, websites, and runtime behavior. It can recover evidence about a feature and help an agent implement an analogous feature. Static JavaScript/.NET inspection does not require a native decompiler. Native analysis uses providers such as Ghidra, Hopper, or IDA. REA is therefore an optional research aid, not an animation renderer, training system, or video-quality improvement engine. [Repository README](https://github.com/morluto/rea)

The inspected main snapshot was **`428eee00fdd0406cdf2b734c9ea14a2bb02da279`**. Its package declares version **6.4.0**, MIT, and Node `^22.19.0 || ^24.11.0 || >=26.0.0`; this does not establish the installed or latest npm release. Dependencies/providers retain their own licensing. [Pinned package](https://github.com/morluto/rea/blob/428eee00fdd0406cdf2b734c9ea14a2bb02da279/package.json), [license](https://github.com/morluto/rea/blob/428eee00fdd0406cdf2b734c9ea14a2bb02da279/LICENSE)

**Architecture/tool surface:** MCP and CLI call shared analysis workflows. Evidence records expose `normalized_result`, `evidence_id`, raw provider output, and analysis-profile identity. Relevant operations include `analyze_javascript_application`, `trace_application_feature`, `compare_application_versions`, `compare_source_to_bundle`, and `inspect_analysis_view`. `tools/list` includes unavailable tools; `binary_session` reports availability for the current host/provider/target. Retained evidence lets follow-ups avoid re-running analysis, and bundles allow export. [MCP contracts](https://github.com/morluto/rea/blob/428eee00fdd0406cdf2b734c9ea14a2bb02da279/docs/mcp-contracts.md)

**Code inspected:** `JavaScriptApplicationWorkflowService.ts` validates request schemas and evidence identities, parses application/native evidence, calls graph tracing or version/export-shape comparison functions, and wraps results into evidence with source IDs. Failure becomes a typed protocol error. This confirms evidence-processing plumbing rather than merely a README promise; it does not establish correctness on any animation application. [Pinned source](https://github.com/morluto/rea/blob/428eee00fdd0406cdf2b734c9ea14a2bb02da279/src/application/javascript/JavaScriptApplicationWorkflowService.ts)

**Windows caveat:** The Ghidra path is explicitly experimental, with twenty-five read-only analysis operations, Windows x64, local fixed NTFS paths, operator-installed Ghidra 12.1.x, and a compatible full JDK. Native x86/x64 PE targets are the documented boundary; GUI state, annotations, and broader parity are excluded. Reparse/UNC paths and other filesystems have restrictions. Check the published-package/main boundary before integration. [Windows Ghidra guide](https://github.com/morluto/rea/blob/428eee00fdd0406cdf2b734c9ea14a2bb02da279/docs/windows-ghidra-p0.md)

**Recommendation:** use ordinary source inspection first for open projects. Use REA selectively when an app's packaging, IPC, undocumented behavior, or native subsystem obstructs understanding. Useful design lessons to adopt independently are schema-validated inputs, explicit provenance, bounded evidence views, immutable artifact identities, and clear unavailable/unknown states. Do not make REA a runtime dependency of the studio.

## Proposed fair benchmark

Run the native/manual pilot after a prototype exists; no scores are implied here. Video-model comparisons begin with published evidence. Newly generated model baselines would require a separate research request and remain outside the studio; they are not required for implementation or delivery.

1. **Freeze a common brief and assets.** The main report's canonical pilot is an original twenty-second, three-shot courtyard scene: two consistent characters converse, exchange a cup, and one reacts and sits. Include wardrobe, prop count, story beats, action times, camera specification, sound, and delivery format. Use short compatible subshots when a service's length limit requires them; report extra assembly work. Other settings, including a boat, belong to later held-out tests rather than defining the product scope.
2. **Keep the product and comparators separate.** Compare our native render with manual Blender production and online reference aesthetics first. For any separately requested model experiment, give each system the same written brief and character/style references, declaring unavailable controls. An external guided condition may use approved rough animation/keyframes to assess a competitor fairly; it never becomes the studio's delivery path. Give each comparator its normal best tools and record additional operator work.
3. **Apply identical revisions.** Delay the handoff by twenty-four frames (one second at 24 fps); change only the camera; change one reaction; retain character identity across three shots. Score the revised output and how much unrelated content changes. Rerender an unchanged project to assess repeatability separately from editability. This aligns with the main report's first milestone.
4. **Use human-made online references as aesthetic anchors.** Record links, timestamps, creator, style, and relevant strengths. Ask for the user's preferred examples. Compare acting, silhouettes, composition, lighting, linework, pacing, and sound; do not claim to know reference production costs or retry counts. Use original benchmark characters/story rather than copying reference assets.
5. **Pre-register the sampling rule.** For a pilot, use five independent attempts per stochastic condition and three revision branches. Record every attempt and any prompt adjustment; show first attempt, best result, and acceptance rate. For larger decisions, expand the sample and estimate uncertainty. Separate equal-budget and best-achievable comparisons.
6. **Measure production success.** Blind randomized human review for appeal/acting/story clarity; frame inspection for contact, penetration, foot slip, prop permanence, identity drift, and event timing. Record unwanted-region changes, hands-on minutes, wall time, GPU-hours/VRAM, API charges, and assets prepared. Automated scores assist review; they are not final aesthetic truth.

Define acceptance criteria before seeing results. Report **total run/revision cost divided by accepted delivered seconds**, plus a separate fully loaded cost including asset preparation and human labor. If no take is accepted, mark the workflow failed at that budget rather than divide by zero. Show one-time cast/rig costs and amortized costs across later episodes. This can establish where the proposed system is better; showcase clips alone cannot.
