# Production entry point

Load `agent-kit/code-animation/SKILL.md` for the consuming model's workflow. Retrieve task-specific guidance through `get_context`; six maintained recipes live in the package's data/recipes directory, so CLI and MCP return the same content.

The runtime supports direct structured authoring, MCP stdio and a provider-independent bounded agent loop (`animation_kit.agent.run_agent`). Model providers implement `decide(context)` and return a typed tool decision or an explicit finish. No model credential or paid API is required by the core. The host supplies the model; the kit supplies instructions, context, components, tool execution and recorded evidence.

Development instructions and the consuming skill have different purposes. Use the consuming skill to make videos, and the architecture/research packet when implementing new reviewed components.
