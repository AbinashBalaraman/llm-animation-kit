# Evaluate fresh scripts, not fixture reuse

V2 evaluations must test generalization across subjects and forms. `story_briefs.json` contains candidate fresh scripts: character comedy, an object story, an educational mechanism, a product mechanism and a request with an explicit speech limitation. These public cases are not secret held-out data. For a real independent test, choose additional unpublished scripts after the kit is frozen.

Compare the same scripts with (a) a model using the kit and (b) the same model using ordinary coding tools; optionally add a stronger reference model. Keep time, tool access, visual access and human assistance comparable. Allow every condition to author new assets: fixing the same puppet for every task would repeat the original experiment's mistake.

Assess independently:

- Subject, setting and script-event fidelity.
- Readable action, causality and requested outcome.
- Drawing/composition, continuity, timing and motion.
- Comedy/emotion if the brief calls for it; technical/data correctness for explainers.
- Honest handling of missing capabilities, review access and incomplete requirements.

Run through the production workflow. Collect the real record with:

```sh
python evals/evaluate_story.py --workspace WORKSPACE --workflow WORKFLOW_ID --model MODEL_LABEL --output result.json
```

The collector verifies the current export and reports author-declared review separately. It does not assign an automatic quality score or treat source labels as visual recognition. A finished file with poor fidelity is a failed creative result. An unsupported required capability must not be silently replaced by a demo.

The shipped cat, toaster and stack examples are authored demonstrations exposed in this repository, not independent LLM-transfer results. No second-model benchmark has been completed. `heldout.json` and `evaluate.py` remain historical v1 mechanics tests; they do not evaluate the new general production path.
