# The reusable capability

The host LLM adapts a script, designs subjects and sets, authors geometry/motion, and judges the result. The kit supplies a vector scene graph, articulated assets, keyframes, shot clocks, inspection tools and source-bound review records. There is no default artwork to rename.

Begin with [the production skill](../agent-kit/code-animation/SKILL.md), retrieve focused guidance with `get_context`, and look up fields with `get_schema`. [The authoring SDK](../agent-kit/code-animation/references/authoring.md) builds arbitrary 2D artwork; the server consumes declarative JSON.

Production preserves the brief and rejects loading a legacy demo. Visual acceptance covers identity, action, setting and outcome as applicable. Geometry checks and author-declared reviews are useful evidence, not a semantic oracle or proof of model parity.
