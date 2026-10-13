# Measure whether the kit helps another LLM

Use `heldout.json` as evaluation briefs, not production examples. Keep the exact held-out artifacts out of the model's example context. Run three conditions: stronger reference model + full kit; chosen other model + full kit; the same other model + basic tool documentation without recipes/example/repair guidance. Keep the engine, assets, target format, allowed assistance and budgets explicit. A model host supplies actual model runs; this harness neither calls a paid API nor fabricates a model's decisions.

Give each session the task brief and record operations through `start_workflow` / `workflow_step`. Preserve the entire workflow, including rejected actions and corrections. Finish explicitly. Run:

```text
python evals/evaluate.py --workspace <workspace> --workflow-id <id> --task delayed-wave --condition other-full --model <actual-model-id> --human-minutes <observed-minutes> --out <run.json>
```

Optional `--ratings <file.json>` accepts independently assigned `appeal`, `acting_clarity`, `staging`, `revision_correctness`, each 1–5. Randomize output order for visual reviewers. Report tool failures, acceptance, rescue minutes, render time and provider-side token/spend measurements. Do not let the generating model certify its own parity.

The evaluator checks explicit annotated scene properties and whether the source matches the final export. Those predicates cover only part of each brief; complete instruction fulfillment and visual quality still need review. Only matched repeated runs with disclosed uncertainty can support a comparable-performance claim. No model comparison has been executed in this release.
