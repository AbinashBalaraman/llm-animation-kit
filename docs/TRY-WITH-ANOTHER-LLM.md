# Try the project with another LLM

Give an agent with terminal/files access the repository URL and the prompt below. A text-only chat without code execution cannot run the kit. An MCP host can instead connect the tools using `agent-kit/mcp.example.json` after installing the package.

```text
Use this project to make a new code-rendered animation:
https://github.com/AbinashBalaraman/llm-animation-kit

Clone it into a fresh directory. Read README.md, AGENTS.md and
agent-kit/code-animation/SKILL.md. Create a Python 3.11+ virtual environment,
install the package with pip install -e ., and run the doctor command.

Use the installed tools and knowledge recipes. Do not modify the runtime to
make this task pass. No video-generation models or generated executable code.

Create a five-second scene with a mint character who notices a small gold star
on the left, pauses, then becomes happy and waves. Keep the face, hand and star
visible. This should be a new editable scene, not a copied demo export.

Start a recorded workflow with at most 24 tool calls and 3 render attempts.
Discover capabilities, retrieve relevant guidance, and validate the scene.
Render a preview and inspect its temporal contact sheet/clip if your host can.
Then delay only the wave by six frames and change only the camera zoom to 1.1.
Check that unrelated actions and character colors are preserved.

Record who reviewed the visuals and what was actually observed. If you cannot
view images/video, report that limitation and finish as needs_review; do not
invent visual approval. If you can review and accept it, render the final MP4
and retain editable source and the workflow record.

Report output paths, actual commands/tool calls, failures and repairs, human
help, render time and unsupported requirements. Passing software checks is
not evidence that your animation equals a stronger model's output.
```

For a structured comparison use the separate briefs and collection instructions in `evals/README.md`. Keep the same runtime/assets and disclose differences in model tools, visual access and assistance. The runtime currently supports front-view 2D animation; Blender/3D and physical handover are not implemented.
