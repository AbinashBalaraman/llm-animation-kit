# Review the requested animation

Inspect actual pixels against `brief.prompt` and each requirement. Record the preview job and source revision; edits invalidate approval.

- Is the intended subject recognizable without a title naming it?
- Are essential script events depicted, with readable actions and results?
- Does every shot contribute to the requested meaning? Identify decorative repetition or unexplained identity/setting changes.
- Is the desired emotional/comic beat readable where required? Do not impose narrative on an informational graphic.
- Would a viewer describe substantially the requested scene after watching?

Check silhouette, facial features, scale, identity, prop placement and legible typography. Inspect anticipation, action and settle around a gesture. At contact, compare hand/paw and prop across neighboring frames; authored motion has no grasp solver. Compare both sides of cuts.

Use 8–16 readable overview frames and targeted samples around fast changes. At a brief contact/reveal, inspect roughly 100–250 ms intervals and the exact contact frame. Open these images with the host's image tool. Geometry checks cannot detect every occlusion, prove identity or rate comedy.

Play the video with sound if possible. Check holds, transitions, motion and audible accents. If only frame inspection is available, set `playback_reviewed: false` and retain that limitation. Never infer listening from the presence of an audio track.

Use `preview_motion` with inclusive global `start`/`end` and `step` (default 3 frames) to inspect an action. At most 32 samples fit a strip; split longer actions into meaningful intervals. `hide_text: true` on this tool or `preview_frames` produces a diagnostic without changing the canonical scene. For visual narratives, describe what you can actually see with captions hidden. A diagram may need labels to retain its meaning.

`review_story` takes `project_id`, `expected_revision`, `preview_job_id`, `accepted`, `reviewer`, `coverage`, `quality`, `playback_reviewed`, and `notes`. Coverage rows have `requirement_id`, `status` (`pass`, `fail`, `unreviewed`), global `frames`, and a concrete `observation`. For passes, cite frames from a shot with a beat associated with that requirement.

Supply one `quality` row per dimension with `dimension`, `status`, `frames`, and `observation`. Status is `pass`, `fail`, `unreviewed`, or `not_applicable`; explain an inapplicable check specifically. Failed or unreviewed dimensions block acceptance.

| Dimension | What to inspect | Minimum frames for a pass |
| --- | --- | --- |
| `visual_clarity` | Recognizable subjects; the actual action communicates the intended event. | 1 |
| `cause_and_effect` | Cause precedes consequence; reactions explain decisions. | 2 |
| `motion_and_contact` | Anticipation/action/settle; paths, contact and ownership do not jump or pass through bodies. | 3, with a pair within 250 ms in the same shot |
| `framing` | The important event is readable; space and camera moves serve a purpose. | 1 |
| `continuity` | Positions, facing, props, condition and emotion carry across cuts. | 2 |

These are evidence minima, not sampling targets. Inspect every critical action and both sides of important cuts. Cite actual full-preview frames, even when the text-hidden diagnostic helped find a problem. Do not declare animation inapplicable to avoid examining it.

The tool checks real frame files, source match, coverage and visible non-text drawing. This prevents empty/title-only evidence; it does not certify semantic understanding. Accept only when all requirements have been visually assessed and met. Otherwise record rejection and repair before another review.

Reviews use `review_version: 2`. Historical approvals need a direction plan and a fresh quality review before a new final export. The authoring model may review its own output, with disclosure. Structural gates require evidence and specific answers; they cannot prevent dishonest claims or guarantee compelling filmmaking. This is not an independent model-parity experiment.
