# Actual authored examples

Run `python scripts/render_examples.py` from the repository. It uses the same public tools provided to other LLMs and creates three native preview packages:

- `discovery-before/`: eight-second glance, curious pause, surprise, reach and celebration.
- `discovery-after/`: a 12-frame reaction/reach delay and camera revision. A naive edit is rejected for overlapping gestures; the record contains the explicit repair.
- `two-friends/`: a six-second greeting using the same rig with two different color identities.

Each contains playable MP4, contact sheet, evaluated trace, source JSON and render manifest. `run-record.json` preserves transaction inputs/results, timings and the rejected attempt. `visual-review.json` records the actual inspection when completed. These are demonstrations authored by this implementation session; they are not a multi-model experiment or a professional-quality rating.

Per-frame PNG sequences stay in the local render workspace; their recorded hashes are retained in the manifests, while this folder packages the video, source, trace, contact sheet and procedural audio. To regenerate the final after inspecting a preview, use `scripts/export_demo.py --reviewer human --review-notes "Your actual observations and limits"`; the script requires explicit notes and does not invent a new review.

The quiet-wave template is also available through tools; its schema and rendering components are tested, but it is not listed as a separately reviewed golden video here.
