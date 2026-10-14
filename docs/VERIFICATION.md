# Verified release 0.3.0

14 October 2026. Machine-readable results are in `verification-results.json`; v0.2 and v0.1 results are retained separately.

- **45 behavioral/integration tests passed**, zero failures (34.293 seconds in the final local run). New checks cover required writing plans, unresolved self-questions, narrative structure, shot-plan drift, workflow ordering, temporal review evidence, rejection of old approvals, text-hidden diagnostic images, render budgets and exact anchor/arc positions. Existing transaction, determinism, schema, MCP and real encode/decode checks remain.
- The consuming skill passed its validator. Generated schemas and recipes were rebuilt from their sources.
- A v0.3.0 wheel was built and installed into a new isolated virtual environment. An isolated Python process imported that installed copy, loaded the direction schema, exercised both motion helpers, rendered a real image strip and encoded/decoded a 12-frame MP4 using packaged fonts. This is a mechanical fixture test, not a creative rendered example. The clean install used Pillow 12.3.0, jsonschema 4.26.0 and imageio-ffmpeg 0.6.0.
- **A new 22-second, 528-frame, 1280×720 crocodile/chicken short** was rendered through the shared workflow. It includes the full prose story, six core answers, causal beats, shot script, explicit self-review, source, MP4, render manifest and declared visual review. Artifact hashes and decoded frame count were verified.
- The author inspected real overview and contact images, including text-hidden strips. Revisions addressed the egg path, deposit, nest continuity and flower placement. `review-overview.png` and `review-contact.png` come from integrity-checked current preview frames. The final render took 135.958 seconds on this machine; that is an observation, not a hardware-independent benchmark.

**Review scope:** sampled frames and temporal strips only. Normal-speed playback, audio listening and independent audience ratings were not assessed. Flower pickup is briefly partly occluded and cuts compress some crocodile travel. The result remains simple stylized 2D animation, not a claim of professional film quality.

**Model evaluation:** the user supplied another external animation result, which motivated these changes. No second LLM was invoked to produce the revised example or test the new instructions. Written-plan and visual-review gates require structured work and evidence; they cannot certify a coherent story or honest self-review. Model parity remains unestablished.

The earlier cat, toaster and stack films retain their original v0.2 sources and reviews as historical evidence. New production/export under v0.3 requires a direction plan and current quality review.
