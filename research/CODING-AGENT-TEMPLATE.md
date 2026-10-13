# Bounded implementation task packet

Use this after choosing a task from section J of animation-studio-architecture.md. The report contains three filled prompts for T01, T02, and T04.

This template is for agents building the product. The product itself is the instructions, knowledge, tools, examples, components and feedback loop that other LLMs use to create animation; see [the capability-kit design](LLM-ANIMATION-KIT.md) and tasks K00–K04. Completing this template does not establish that the consuming kit exists or transfers animation capability.

```text
Task: <ID and concrete outcome>
Architecture version: 0.1.0
Prerequisites verified: <completed task IDs and artifact evidence>
Read only this minimal context: <report sections, relevant schema definitions,
                               prerequisite API signatures, fixtures>
You own: <explicit files/directories>
Required interface: <function/wire schema and version>
Deliver: <observable behavior and artifacts>
Acceptance: <named positive, negative, and integration checks>
Out of scope: <explicit exclusions>

Implement the assigned behavior using the fixed architecture and contracts.
Do not invent missing actions/assets or execute model-generated code.
Never add a video-generation model, video-to-video refinement, or generative
frame-interpolation stage. LLM planning returns structured scene data only.
Do not change public schemas, timing, coordinates, storage, or another module's
contract to make your implementation easier. Record a proposed ADR if a shared
change is truly necessary; preserve compatible work while it is resolved.
Keep unrelated changes out. When a prerequisite is missing, name the exact
missing artifact/interface and complete independent work that remains useful.
Run the acceptance checks appropriate to this task. Report actual results,
not intended results. Update STATUS with files, commands, limitations and the
next ready task. Rendering success alone does not prove animation quality.
```

Supply the schema version and selected definitions as files, not an approximate prose rewrite. Supply only completed prerequisite interfaces. Keep evidence memos available for investigation without putting every source page in the model's context. Do not treat the synthetic JSON descriptors as real geometry, audio, rig or motion data.
