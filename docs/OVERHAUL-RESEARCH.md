# Sources consulted for the overhaul

13 October 2026. These sources informed original implementation decisions; this repository does not vendor their runtimes or claim compatibility with their native scene formats.

| Source | Relevant lesson | Implemented consequence |
|---|---|---|
| [Remotion: core idea](https://www.remotion.dev/docs/idea) | A frame-driven composition can author arbitrary visuals. | Deterministic evaluation from frame number; fresh geometry instead of a finite story-preset menu. |
| [Remotion: agent skills](https://www.remotion.dev/docs/ai/skills) | Agents benefit from task-focused authoring/render guidance. | Portable production skill, progressive authoring/acting/review references, compact discovery and on-demand schema. |
| [Motion Canvas: animation flow](https://motioncanvas.io/docs/flow/) | Timing and scene sequencing deserve explicit authoring tools. | Independent shot clocks, coordinated part tracks and explicit story beats. The implementation uses pure keyframe evaluation, not generator execution. |
| [Manim: Scene](https://docs.manim.community/en/stable/reference/manim.scene.scene.Scene.html) | A scene contains authored objects and animations with explicit composition/draw order. | General geometry/groups/assets separate from story content. |

The installed **Tesseract motion plugin** was consulted locally, particularly `references/motion-design.md` and `references/filmstrip-review.md`: editable layer hierarchy, purposeful movement, early sampled-frame inspection, and the distinction between still-frame review and playback. Its runtime was not used for these renders. The built-in **Skill Creator** guidance informed the rewritten consuming skill; **Plugin Management** was used to search for code-animation integrations.

Plugin directory searches for Remotion/Tesseract and animation-code capabilities did not return a relevant new code-rendering integration in the available results. Results included design services, infrastructure and video-generation services; none was installed or made a dependency. The user excludes video-generation models. Existing native tools and the installed guidance were sufficient to implement the portable engine. Directory results are not an exhaustive claim about plugin availability.

No single source proves the new kit produces good films or equalizes LLMs. Those claims require observed outputs and independent tests on fresh scripts.
