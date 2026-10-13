# Contract fixture validation

Observed on **13 October 2026** using Python **3.13.1** and `jsonschema` **4.26.0** already installed in the workspace environment. No packages were installed and no remote assets were downloaded.

**Result: 45 checks passed, 0 failed.** The exact check names and outcomes are saved in `validation-results.json`. This result validates a proposed contract and its synthetic fixture, not an animation system.

## Reproduce

From the repository root:

```powershell
python research/contracts/validate_contracts.py
```

The script exits nonzero if a recorded check fails. It reads the schema, examples, and eight fixture assets and rewrites only `validation-results.json`. It does not modify the example project or run an application.

For deliberate regeneration of the canonical fixture before validation:

```powershell
python research/contracts/_build_fixture.py
python research/contracts/validate_contracts.py
```

The generator recreates `studio.schema.json`, the 15 example documents, and the eight descriptor assets. It uses UTF-8 and explicit LF newlines so asset bytes and SHA-256 hashes are stable across operating systems. Regeneration overwrites those generated files; edit the canonical generator if changing the contract. `CONTRACTS.md` and this result narrative are separately maintained documentation.

## What actually passed

- Draft 2020-12 schema self-validation and positive validation of **all 15 example documents**, including one example for each of the seven action types.
- Selected resolve checks: project/document identity and manifest membership, all **eight exact fixture-file SHA-256 digests**, repeated character asset references, role/profile labels, selected action/entity references, and bundle-relative asset paths.
- Selected static checks: ordered and bounded frame ranges; reduced rational FPS; normalized world, attachment, and affordance rotations; uniform positive scale; camera near/far and nondegenerate view/up basis; handover event ordering; required giver/receiver arm claims; grasp identities and allowed hands; overlapping channel writes; duplicate ownership and attachment records; audio interval capacity and viseme offsets; expected project revision.
- A **symbolic, metadata-only event walkthrough** verifies declared ownership/contact/seat assertions for the example handover and sit. It checks the transfer requires receiver contact and that ownership/contact persist through later assertions. It does not solve poses, attachment matrices, collision, or motion.
- An in-memory test oracle materializes the documented coupled revision: handover and reaction move by 24 frames, including all three handover event frames. The resulting candidate passes the same selected checks. The on-disk project remains revision **7**. No production revision service, commit, or concurrency mechanism was exercised.
- **26 intentionally invalid cases** were rejected: ten at the schema layer and sixteen that remain schema-valid but fail the selected semantic checks.

## Negative coverage

| Layer | Cases deliberately rejected |
|---|---|
| Schema — 10 | Unknown action; parameters from another action type; fractional frames; malformed digest; unsupported rig ID; array-index patch; non-atomic revision; wrong audio sample rate; unknown field; seat missing foot-zone bounds |
| Selected semantics — 16 | Reversed frame interval; transfer outside its action; missing receiver arm claim; overlapping writes to one actor/channel; duplicate logical ownership; multiple transform parents; incorrect initial owner; actual hash mismatch; dangling actor; non-unit rotation; nonuniform scale; disallowed grasp hand; degenerate camera; stale revision; audio longer than its action; viseme at the excluded end sample |

Each semantic negative first passes JSON Schema validation. This demonstrates why schema validity alone is insufficient. Negative candidates are modified copies in memory; the valid fixture files remain unchanged.

## Limits and unperformed checks

**There are no renderable assets.** The eight hashed files contain synthetic descriptor JSON, not meshes, a skeleton, usable animation, or audio samples. Passing the digest checks only proves those descriptor bytes match the manifest. The two-shot, 20-second sample is an interface illustration, not the three-shot production milestone or a finished animation.

The script is a bounded fixture QA harness. It does not implement every normative rule in `CONTRACTS.md`. In particular, the following remain unimplemented or untested:

- Full asset decoding, complete reference/cycle validation, licenses, production rig topology/rest pose, facial mappings, action/gesture/voice/style registries, and real motion compatibility.
- A complete trusted action registry that derives every mandatory condition, channel claim, transition, and persistent effector reservation independently of the submitted JSON. The QA checks selected handover requirements; it is not sufficient to trust arbitrary generated actions.
- Spatial proximity, reachability, navigation, collision, IK/contact tolerances, foot planting, prop-world-transform continuity when reparenting, seat fitting, or preservation of a held cup during actual sitting. Oriented affordance fields are structurally checked; their geometric suitability is not established.
- Production handling of compatible channel composition. The harness rejects every overlapping write and accepts no compatibility profile. It does not prove a speech/expression blend or a hold-preserving sit solver.
- Real audio decoding, duration against a source waveform, phoneme recognition, lip-sync quality, general rational-FPS boundary cases, cross-scene continuity, or rendering after a nonzero scene-time checkpoint.
- Revision locking/compare-and-swap under concurrency, transactional storage/rollback, idempotent retries, generic operation execution, complete downstream invalidation, or cache determinism.
- Compilation, render frames, sound, encoding, artistic quality, performance, memory, GPU requirements, monetary cost, or comparison against online reference videos and video models.

Production `resolve`, `semantic`, and `compile` stages must perform the complete checks and reject these descriptor fixtures as non-renderable. A successful schema-stage report is not a successful render report. See `CONTRACTS.md` for the proposed stage boundaries and invariants.
