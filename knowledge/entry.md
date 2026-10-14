# The reusable capability

The host LLM first develops and questions a complete story: who, what, when, where, why, how, motivations, causal events, reactions and resolution. It turns the rewritten story into a shot script before designing subjects, sets or motion. `plan_story` checks the supplied plan; it does not generate the creative answers. The kit then supplies geometry, articulated assets, timelines, inspection tools and source-bound reviews. There is no default artwork to rename.

Begin with [the production skill](../agent-kit/code-animation/SKILL.md), retrieve focused guidance with `get_context`, and look up fields with `get_schema`. [The authoring SDK](../agent-kit/code-animation/references/authoring.md) builds arbitrary 2D artwork; the server consumes declarative JSON.

Production preserves the brief, requires the validated plan in `scene.direction`, and rejects loading a legacy demo. Visual acceptance covers the actual script plus clarity, cause/effect, motion/contact, framing and continuity. Read [story development](../agent-kit/code-animation/references/story-development.md) before artwork. Structural checks and author-declared reviews are not a semantic oracle or proof of model parity.
