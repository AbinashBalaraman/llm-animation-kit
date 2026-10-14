# Write the film before drawing it

Use this before authoring a production. The host model does the writing;
`plan_story` validates a supplied plan and does not generate one. Answer these
questions yourself using the brief and reasonable creative choices. Ask the
user only about consequential ambiguity. Preserve supplied events, characters,
dialogue and constraints when adapting an existing screenplay.

## Develop specific answers

Retrieve `get_schema` with `version: direction`. Create a `kit.direction/1.0`
plan preserving the exact original `brief`.

| Question | Decisions the answer must make |
| --- | --- |
| Who? | Who wants something? What are they like initially? Who helps or opposes them? How will the viewer recognize each subject? |
| What? | What happens, what is the immediate goal, and what changes? Name observable events, rather than a theme such as friendship. |
| When? | When does this happen, how long does the encounter take, and are there time jumps? What establishes a change of time? |
| Where? | What place enables the action? Where are characters, hazards, exits and important props relative to one another? |
| Why? | Why does each character act now? What would happen if they did nothing? Why does a change of emotion or judgment make sense? |
| How? | Which visible decisions and actions change the situation? What causes the turning point? How is the outcome achieved and shown? |

Extend these with questions specific to the request. For friendship, ask what
separates the characters, which act earns trust, who witnesses it, and how the
other character responds. For a mystery, ask when a clue changes the viewer's
interpretation. For an explainer, ask which relationship is being demonstrated,
which values must stay correct and what the viewer should understand afterward.
Do not impose a rescue, gift, joke, villain or fixed shot count on every script.

## Write a complete story and challenge it

Write `story_text` as connected prose with a beginning, development and ending.
It must make sense before any drawing exists. A list of labels such as
“meet / problem / friends” is not a story. A choice must follow from what a
character knows and wants at that moment.

Write a concise, visible question-and-answer review. These are production notes
for users and other agents, not hidden reasoning. Cover the six `self_review`
focuses with specific evidence from the story:

- **Motivation:** What does each participant want? What exact event changes a decision? Is a change of heart earned?
- **Causality:** Why does this event follow the previous one? Would removing its supposed cause leave the same outcome? Find unexplained arrivals, rescues or coincidences.
- **Stakes:** What can be lost or gained? Is that established early enough? Stakes may be small, personal or comic.
- **Clarity:** What would the viewer understand at each point? Which essential fact currently exists only in prose, a caption or the author's intention?
- **Ending:** Does the resolution answer the original situation? Which choice or image proves the change? Include the response to a solved problem when it matters.
- **Filmability:** Can the installed backend stage every important action? Which contact, expression or transition needs a closer view? Is there enough time to read the beats?

Do not answer with generic assurances such as “yes, it is clear.” If a question
exposes a weakness, use `verdict: revise`, describe the correction in `revision`,
and rewrite the affected prose, beats and shots. Reassess after the rewrite.
The tool rejects unresolved plans; changing a verdict without fixing its cause
is dishonest self-review. Read the complete story again after the changes.

For an explainer or abstract piece, `not_applicable` requires a specific reason.
A diagram need not have a frightened protagonist or emotional stakes. Narrative
mode must address all six checks. Structural validity is not a creative score.

## Translate the story into a filmable script

Create causal `beats` with `cause`, `visible_action` and `change`. A narrative
needs a setup, a meaningful turn and a resolution; add what the story needs.
Avoid sequences of unrelated “and then” events.

Write `shots` with duration, framing, action, reaction, continuity entering and
leaving, and any dialogue. Assign every beat to a shot. For each shot decide:

1. What does the viewer learn or feel here?
2. Where should attention start and end? Is the important action large enough to see?
3. What visible response explains the next choice or emotional change?
4. Which positions, object ownership, conditions, knowledge and emotions carry into the next shot?

Establish the geography, then use closer views where the story needs them.
Repeating a wide composition with different headings rarely communicates a
character story. These are directing considerations, not a compulsory shot
template. Dialogue may reveal character or supply needed information; it should
not merely explain missing visual action. Do not promise voiced dialogue when
the selected backend cannot deliver it.

Submit the plan through `plan_story` in a production workflow before artwork.
Copy the exact plan into `scene.direction`. The tool checks structure, coverage
and unresolved revisions, not story quality. The plan's ordered shot IDs and
durations must match the rendered shot list. After editorial changes, revise and
resubmit the plan, then apply a `replace_story` transaction.

Deliver the prose story and shot script with the video. Compare the actual
frames with what the script says the audience should understand. For visual
narratives, inspect a text-hidden diagnostic; keep essential labels when
reviewing diagrams or kinetic typography. A good written plan remains a
hypothesis until the images communicate it.
