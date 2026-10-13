# Verified release 0.1.0

13 October 2026. Actual results are also recorded in `verification-results.json`.

- 24 behavioral tests passed, zero failed. The suite includes strict decoding, schema/semantic rejection, atomic failure, stale revisions, undo, camera edits preserving world state, corrupt-snapshot rejection, bounded context/workflow/agent loops, MCP stdio/image results, evaluation records, real MP4 decoding, cache reuse and damaged-frame recovery.
- The skill-creator validator passed for `agent-kit/code-animation`.
- An ordinary distribution wheel was built. Its ZIP integrity, schema/recipe/example resources and full license texts were checked. The wheel was extracted into an isolated temporary directory and its tools created/inspected a fresh example project there.
- Three original preview packages and a final MP4 were generated. The final is 1280x720, 24 fps, exactly 192 decoded frames (eight seconds). Local measured final render/assembly time was 55.48 seconds. This is a measurement on this host and scene, not a hardware throughput promise.
- The demo workflow uses actual public tool calls, including preview, artifact inspection, explicit review and final export. Before/after contact sheets were visually inspected by the implementation model. No normal-speed independent human/audio review was performed.

The examples are authored demonstrations. No second model was invoked and no model-parity score exists. The release establishes usable software and reproducible evidence paths; it does not establish professional animation quality or equivalence to a stronger model. Blender/3D, speech and physical interaction remain outside the shipped backend.
