# CLI transport

Install the repository package once with `python -m pip install -e <repository-path>`. Use a fixed workspace for the project. The production tools are shared with MCP.

```text
python -m animation_kit --workspace <workspace> tools
python -m animation_kit --workspace <workspace> call discover_capabilities
python -m animation_kit --workspace <workspace> call get_context --input <arguments.json>
```

Write exact JSON tool arguments to a file and pass `--input`; this avoids shell quoting mistakes. The response is `{ok,result}` or `{ok:false,error}` with a code, pointer and repair hint. CLI failure exits nonzero. The scene schema and arguments must match discovery; do not infer field names from prose.

For MCP stdio use `python -m animation_kit --workspace <workspace> serve`. It exposes the same tools with JSON-RPC. A host should provide its normal tool controls and image display. Tools perform no remote model or asset downloads.

Projects hold immutable snapshots, a current pointer, render manifests, frames, review records and editable scene JSON. Keep the workspace between agent sessions. Never edit generated snapshots directly; apply a revision or undo through tools.
