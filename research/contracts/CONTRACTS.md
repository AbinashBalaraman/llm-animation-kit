# Proposed Animation Studio contracts — v0.1.0

This directory is an implementation handoff, not an animation application. `studio.schema.json` is a JSON Schema Draft 2020-12 bundle. The examples describe a 20-second courtyard scene with two characters, a cup, a table, and a chair. They have **two illustrative shots**; they are not the proposed three-shot visual-quality milestone.

**Rendering boundary:** compile and render use editable scene assets, rigged/procedural animation, conventional rendering and compositing. Video-generation models, video-to-video refinement, generative frame interpolation and model fallbacks are excluded. An optional LLM planner emits validated scene data only. This requirement does not change the v0.1.0 schemas or fixture bytes.

**There are no renderable assets here.** The eight files in `examples/fixtures/` are deliberately small JSON descriptors with real SHA-256 hashes calculated from their exact bytes. They contain no usable geometry, rigs, animation curves, or audio. A correct production compiler must reject them as non-renderable, even when schema and fixture checks pass. The schema's rig, style, voice, gesture, and viseme IDs are proposed identifiers, not evidence that compatible production resources have been selected.

## Files and document boundaries

| File / root `$defs` entry | Responsibility |
|---|---|
| `examples/project.json` / `project` | Project revision, rational frame rate, coordinate conventions, immutable asset manifest, document references, shot order, render profile |
| `examples/character-{aya,ren}.json` / `characterRef` | Stable character identity and references to a rig, appearance, voice, and supported actions |
| `examples/scene.json` / `scene` | Persistent world entities, initial transforms, ownership, attachments, contacts, seat occupancy, action IDs, and scene duration |
| `examples/shot-{a,b}.json` / `shot` | A camera and an interval of an existing scene; no duplicate characters or prop state |
| `examples/action-*.json` / `action` | One of seven discriminated action types with typed parameters, resource claims, and pre/postconditions |
| `examples/revision.json` / `revision` | An atomic, named-ID change proposal with a project-wide `expectedRevision` precondition |
| `examples/validation-report.json` / `validationReport` | Example schema-stage report; it does not claim successful production validation |
| `validate_contracts.py`, `VALIDATION.md` | Reproducible fixture QA and the observed result; not a runtime implementation |

The root schema accepts any one of the seven document kinds. To validate an individual type, resolve `#/$defs/<type>` against the same locally loaded bundle. `$id` uses the reserved `.invalid` domain solely as a stable identifier; validation does not require downloading it. No remote asset hashes are invented.

Document IDs are unique in a project registry and immutable across revisions. Entity IDs are unique within their scene; actor and prop references resolve through the action's `sceneId`. Character entities reference a project-level character document. The example intentionally uses `char_aya` as both entity ID and character document ID; implementations must not assume these namespaces are interchangeable. Affordance IDs are unique within the target entity. Operation IDs are unique within their revision proposal.

Document and fixture URIs resolve relative to `project.json`. The first local implementation should accept only files within the resolved bundle root, including after symlink resolution. Downloads, license approval, and adding external assets belong to explicit import workflows. Every repeated asset reference must exactly match its manifest entry. Changing bytes requires a new manifest hash and deliberate revision; a URI alone never identifies cached content.

## Time, audio, and coordinates

- Version: `0.1.0`. Unknown fields and unsupported actions fail schema validation; no silent fallback animation.
- Frames are nonnegative integers. Ranges are zero-based, half-open `[start,end)`: frames `start` through `end-1` are rendered. `end > start`, and all action and shot ranges must fit the scene.
- Action and shot ranges, handover event frames, and `seatContactFrame` are **absolute within the scene**, not relative to an action or the assembled video.
- Project FPS is a reduced positive rational. The fixture uses `24/1`; audio uses `48000` Hz. There are exactly 2,000 audio samples per fixture frame.
- For general rational FPS `n/d`, map frame boundary `f` to sample boundary `floor(f * d * 48000 / n)` with integer arithmetic. An action's audio capacity is the difference between its two boundary mappings; do not round each frame's duration independently.
- `audioRangeSamples` is a half-open interval in the referenced source audio asset. `visemes[].atSample` is an offset from the selected interval's start. It must be sorted, unique, and less than that interval's duration. Source audio must exist, decode at 48 kHz, and fit the action interval; pad unused capacity with silence. Any retiming or resampling must be explicit and produce a new immutable audio asset.
- Fixture speech spans scene frames `[108,156)`: 48 frames / 2 seconds / 96,000 samples. Its descriptor declares this duration but contains no sound. Fixture viseme cues demonstrate shape only and are not measured alignment.
- `shotOrder` concatenates selected scene intervals into the output timeline. World state is evaluated at the selected **scene time**, with preceding actions replayed or restored from a valid checkpoint. A shot starting at frame 240 must not restart the scene at its initial state. This version has cuts only, no transition-duration contract.
- Lengths are meters. World coordinates are right-handed, Z-up. Character local forward is +Y. Quaternions are unit `[x,y,z,w]`; all numbers must be finite. The adapter converts these conventions to its renderer explicitly. Production character scale must be baked to `[1,1,1]` for the frozen rig profile.

An entity's transform is its initial world-space placement unless an initial attachment exists. **For attached props, `attachment.localTransform` relative to the named parent socket is authoritative**; the standalone entity transform is an import/reference pose and must not be applied a second time. Reject attachment cycles and ambiguous multiple parents. Actual socket transforms are unavailable in these fixtures.

## Typed action contract

| `actionType` | Typed parameters | Required semantics beyond JSON shape |
|---|---|---|
| `walk_to` | destination, facing target, speed, motion asset | Find a supported, collision-checked path and timing; reach the destination without foot sliding. Fail if requested speed, duration, and path cannot be reconciled within the selected motion profile. |
| `look_at` | target entity, optional target affordance, influence, ease-in frames | Resolve target and gaze limits; duration must accommodate easing. This action claims gaze only unless an adapter declares additional head/torso claims. |
| `gesture` | gesture ID, hand, intensity, motion asset | Resolve an existing compatible gesture and claim all affected channels. Preserve live contacts. |
| `speak` | text, language, immutable audio reference, source sample range, viseme cues | Verify actual audio and rig viseme support; route audio without generating or replacing it during render. Claims voice and face. |
| `handover` | prop, receiver, hands, grasp affordances, contact/transfer/release frames, style, motion asset | Reserve both actors' affected channels and the prop. Enforce ownership, free receiver hand, grasp validity, reach, and event ordering. |
| `sit` | seat, seat affordance, contact frame, motion asset | Reserve the seat; ensure it is reachable and unoccupied. Preserve held-object constraints throughout the movement. |
| `expression` | named expression, intensity, ease-in/out frames | Resolve the rig's expression mapping. Easing intervals must fit its duration. Claims face. |

Only the frozen `rig_humanoid_v1` profile is accepted in this version. Before a real compiler is implemented, that profile must freeze skeleton topology, bone roles, rest pose, socket transforms, facial controls, and supported motion/retarget rules against actual licensed assets. The string by itself is insufficient. Rigged motion and characters must match the selected profile; environment, rigid prop, and audio assets use `rigProfileId: null`.

The versioned, trusted action registry is authoritative. Each registered definition supplies its minimum affected channels, preconditions, state transitions, persistent constraints, postconditions, and supported motion/profile combinations. These must be derived even if an LLM omits them from JSON. Supplied declarations must cover the registry's requirements and may add stricter assertions; they cannot weaken, replace, or remove them. For example, an empty handover `preconditions` array never permits transferring an unowned cup, and a missing arm claim never grants an unreserved arm. Reject a contradictory declaration rather than guessing. The fixture QA checks selected required handover claims and symbolic state only; a complete trusted registry is still a required implementation task.

Production registry entries must freeze: `actionType`; `registryVersion`; minimum channels by actor role; required pre/postcondition templates; deterministic transition/event definitions; supported rig ID; motion asset hashes; named clip ID and source frame range; allowed duration/speed ranges; parameter bounds; effector/contact policies; and exact compatibility profile IDs. A rig profile must freeze bone-role mappings, rest transforms, hand/foot socket transforms, allowed joint ranges, facial-expression and viseme mappings, root-motion convention, and adapter version. These are **mandatory compiler inputs still to be authored against actual assets**, not metadata inferred from fixture labels. Until they exist, production `resolve`/`compile` validation must fail. Fixture descriptor flags such as `containsRig: false` deliberately prevent a successful production claim.

Affordances are kind-discriminated in the schema. A grasp has a local position/orientation, allowed hand effectors, position tolerance in meters, and angular tolerance in degrees. A seat has a local position/orientation, one-occupant capacity, and oriented foot-zone and clearance boxes with positive half extents. Its oriented +Y axis is the seated character's desired forward direction. A support surface has a local position/orientation and positive two-dimensional half extents in its oriented XY plane, with +Z as its surface normal. Every local field is relative to the owning entity; local boxes have their own rotation. Grasp frame alignment is defined against the frozen rig's hand socket frame, not arbitrary bone axes. These bounds aid validation but do not replace geometry/collision meshes. Normalize all rotations and require uniform positive entity scale; production rig scale is exactly one. The example dimensions are synthetic and have not been fitted to geometry.

`resourceClaims` are mandatory declarations, not a way to opt out of conflicts. The action compiler derives minimum claims and verifies that declarations cover them. Two overlapping intervals cannot write the same entity/channel unless **both** reference the same explicitly implemented, supported `compatibilityProfileId`. Naming a profile does not create a blend rule. In particular, `speak` and `expression` both claim `face`; their overlap must fail unless a tested profile splits or composes the actual facial controls. v0.1 fixture QA supports no compatibility profiles and rejects all conflicting writes.

Channel declarations also do not replace world-resource reservations: overlapping handovers cannot manipulate the same prop, and simultaneous sit actions cannot acquire one seat. Avoid a generic physics fallback for unsupported actions. Emit a structured error and an actionable missing capability.

An active hand contact persists as an effector reservation after the action that created it ends. A later gesture using that hand must fail unless its registered motion/solver explicitly preserves that contact. This is distinct from two concurrent animation actions both writing the arm. The proposed `sit` capability may claim both arms while satisfying an inherited held-prop constraint only when its trusted registry declares and its solver implements `preserve_existing_hand_contacts` for those effectors. It does not suspend the reservation or discard the contact. A solver failure rejects the sit. No generic `compatible` flag authorizes this behavior. The fixture describes the intended sit-with-cup behavior; it does not establish that any actual clip can perform it.

## Persistent state and handover ordering

At a frame boundary, finish prior intervals and validate their postconditions, check starting-action preconditions, then apply that frame's interaction events in deterministic order before sampling animation and rendering. Frames at an action's `end` are outside that action. Preconditions are assertions about the current state; postconditions are assertions about the compiler's actual result, not instructions to falsify state into compliance.

For a handover `[s,e)`, require:

`s <= receiverContactFrame <= transferFrame <= giverReleaseFrame < e`

The giver must own and hold the prop when the action starts. The receiver must differ from the giver and have a free receiving hand. Both referenced grasp affordances must exist. The action must include the giver and receiver arm channels and any other channels used by the selected motion.

At the beginning of `receiverContactFrame`, establish the receiver's secondary contact. At the beginning of `transferFrame`, atomically change the single logical owner and the single authoritative attachment from giver to receiver. Preserve the prop's world transform when computing its new socket-relative transform. At the beginning of `giverReleaseFrame`, remove the giver contact. If events share a frame, their order is contact, transfer, release. Temporary dual **contact** is allowed; dual ownership or dual transform parenting is never allowed. Failed contact/reach verification aborts the transfer; it must not teleport the prop.

The fixture transfers ownership at frame 180. The giver contact remains until frame 184, acting as a secondary constraint after transfer. After the action ends, Ren continues to own and hold the cup, including across the camera cut and the sit action. An action ending releases its animation-channel claims, **not persistent object ownership, attachment, contact, or seat occupancy**. A sit adapter must satisfy the inherited cup contact; if its clip cannot do this, compilation fails instead of dropping the cup.

Locomotion leaves the actor at its resolved destination. Sitting leaves seat occupancy active. Expression and speaking controls return to the profile's neutral facial state at their end; gaze returns to the profile's default gaze unless another valid action takes over. World-changing results persist until an explicit supported interaction changes them. This small action set has no standing, dropping, generic release, or cross-scene continuity operation yet; adding these requires an intentional contract extension. No JSON example proves physical reachability, collision clearance, or appealing motion.

## Atomic revisions and invalidation

`expectedRevision` is a compare-and-swap precondition against the **project's** current revision. The fixture proposal expects revision 7. IDs identify targets; array indices and generic JSON Pointer patches are not permitted. Descriptive `intent` is inert text.

Apply operations in order to a private candidate snapshot. Validate all identities, references, schemas, timing, conflicts, and interaction state against the candidate, then either commit all operations and increment the project revision exactly once or commit nothing. The comparison and commit must be serialized so two clients cannot both apply against revision 7. The mutation API returns the new revision and invalidated build-node IDs. Validation errors leave project files and caches untouched. Persist revision IDs and result digests to distinguish an identical retry from reuse with a different payload.

Supported operation shapes are `shift_action`, `set_expression`, `replace_shot_camera`, `replace_action`, `add_action`, `remove_action`, and `replace_entity_transform`. Their semantics are deliberately narrow:

- `shift_action` shifts start/end **and every action-internal absolute scene event frame** by `deltaFrames`: the three handover frames or a sit's contact frame. Source audio sample ranges and viseme offsets are asset-local and stay unchanged. Never infer movement from any arbitrary numeric field.
- `set_expression` targets an existing expression action. `replace_action` preserves the target action ID and project/scene identity. `add_action` uses a new ID and atomically updates the scene and project registries. `remove_action` removes both registry references and must fail if it leaves invalid dependencies.
- Camera changes target a shot only. Entity transform changes target an existing scene entity and must respect attachment authority; changing an attached prop's inactive reference transform cannot be presented as moving the rendered prop.
- Dependent timing changes must be included explicitly in the same proposal. Do not silently ripple-edit unrelated actions. Revalidate state at every downstream use even when its JSON did not change.

The sample proposal shifts the handover by 24 frames and shifts the reaction by the same amount. It changes handover `[144,216)` to `[168,240)` and its contact/transfer/release frames from `176/180/184` to `200/204/208`; reaction `[184,240)` becomes `[208,264)`. The sit remains `[264,336)` and retains the transferred cup. Commit would produce project revision 8. The checked fixture on disk remains revision 7; no runtime transaction has been implemented or executed.

Invalidate action compilation, affected scene-state checkpoints, shot evaluations, final composites, and output audio alignment according to actual dependencies. A camera-only change can reuse world animation; an earlier ownership change can invalidate a later shot even if that shot's camera and JSON remain identical. Cache keys must include immutable asset hashes, contract version, adapter version, rig profile version, source action data, and relevant upstream state. Whole-project invalidation is an acceptable correct first implementation.

## Runtime API alignment and validation stages

The research handoff proposes these boundaries; this directory supplies their data contract, not callable implementations:

| Proposed boundary | Contract responsibility |
|---|---|
| `load_project(path) -> ProjectBundle` | Resolve the project manifest, documents, and immutable assets into a typed bundle. |
| `validate(bundle, stage) -> ValidationReport` | Return issues with `code`, `severity`, `document_id`, `json_pointer`, `message`, and `repair_hint`. |
| `plan(intent, catalog, world, budget) -> Proposal` | Produce a candidate bundle or revision within a supplied planning budget; never execute instructions hidden in descriptive text. |
| `compile(bundle, shot_id, profile) -> BuildPlan` | Verify supported capabilities and evaluate persistent scene state at the shot interval. Include the selected profile digest in the plan. |
| `render(plan, profile) -> Job` | Profile must match the plan digest. Use job statuses `planned`, `running`, `succeeded`, `failed`, `cancelled`; status is separate from validation results. |
| `apply_revision(bundle, revision) -> {new_revision, invalidated_nodes}` | Atomic application with an expected revision and complete dependency validation. |

Validation stages are `schema`, `resolve`, `semantic`, `compile`, `render`, and `review`; report status is `passed`, `failed`, or `not_run`. No stage may imply that later stages passed. Reports with error-severity issues cannot be `passed`.

1. **Schema:** types, required fields, enum values, discriminator-specific parameters, fixed conventions, closed objects.
2. **Resolve:** unique IDs, document membership, manifest consistency, path safety, bytes/hashes, supported resource registries and actual decoders.
3. **Semantic:** ordered/bounded intervals, exact audio mapping, unit rotations, complete channel claims, interactions, seat reservations, ownership/contact state, supported rig compatibility, revision preconditions.
4. **Compile:** motion fitting, reach, constraints, safe transforms, continuity checkpoints, supported adapters and deterministic build dependencies.
5. **Render:** actual output frames/audio, completion, encoding, and diagnostics.
6. **Review:** visual appeal, contact/foot sliding, expressions, continuity, dialogue intelligibility, shot composition, and comparison with references.

`validate_contracts.py` performs schema checks and a documented **subset** of resolve/semantic checks on these fixtures, including symbolic handover state and negative cases. It does not implement a general scene solver, rig loader, planner, revision service, compiler, renderer, or perceptual evaluator. `VALIDATION.md` records exactly what was run.
