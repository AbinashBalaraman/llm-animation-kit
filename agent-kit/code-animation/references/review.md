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

`review_story` takes `project_id`, `expected_revision`, `preview_job_id`, `accepted`, `reviewer`, `coverage`, `playback_reviewed`, and `notes`. Every coverage row has `requirement_id`, `status` (`pass`, `fail`, `unreviewed`), global `frames`, and a concrete `observation`. For passes, cite frames within a beat associated with that requirement.

The tool checks real frame files, source match, coverage and visible non-text drawing. This prevents empty/title-only evidence; it does not certify semantic understanding. Accept only when all requirements have been visually assessed and met. Otherwise record rejection and repair before another review.

The authoring model may review its own output, with disclosure. This is not an independent model-parity experiment.
