# Test on a fresh script

Use a coding agent with terminal/files or MCP, and image/video access for review. Replace the script block with your own request. Do not use only the shipped demonstrations to assess generality.

```text
Use https://github.com/AbinashBalaraman/llm-animation-kit at version 0.2.0 or newer.
Clone it into a fresh directory, install in a Python 3.11+ virtual environment,
and read README.md, AGENTS.md and agent-kit/code-animation/SKILL.md.
Run the doctor command and discover capabilities.

SCRIPT / BRIEF:
[Paste my complete script or request here.]

Preserve that exact brief in the production workflow and scene document.
Extract its visible requirements. Author the needed characters, objects, sets
and actions using the general SDK or kit.story/2.0 JSON. Start with an empty
document. You may write an authoring script; do not modify the engine to add
a special-case renderer for this request. No video-generation models.

Do not copy a demonstration's character, environment or plot unless my script
actually asks for those things. Do not silently replace a missing capability
with an unrelated example. Report the specific gap if a requirement exceeds
the installed backend.

Use a recorded production workflow (up to 60 calls and 10 renders). Inspect
storyboard images early, render a preview, and review actual output against
every requirement. Repair problems you observe. Record truthful frame evidence
with review_story. Mark playback_reviewed only if you actually assessed normal-
speed playback. If you cannot see the output, finish as needs_review.

When accepted, render the final MP4. Deliver the video, editable JSON and
authoring script, and the review/evaluation record. Report remaining gaps,
tool failures, human assistance and whether playback/audio was assessed.
An encoded file alone is not success.
```

Try substantially different scripts: an animal comedy, a product mechanism, an educational diagram, a dialogue scene or an abstract motion graphic. Judge fidelity and output quality separately from technical rendering. Speech and 3D requirements may need additional backends. The three shipped films are exposed regression demonstrations, not held-out benchmark results.
