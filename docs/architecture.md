# Architecture Notes

## Design goals

- Demonstrate end-to-end reliability testing for tool-using agents
- Keep the repo runnable offline for portfolio review and CI
- Preserve a clear upgrade path to live OpenAI or MCP-backed tools
- Make failure modes explicit and testable

## Layers

### 1. Orchestration layer
The orchestrator classifies intent and delegates to a specialist agent.

### 2. Specialist layer
- `order_specialist`
- `billing_specialist`
- `knowledge_specialist`

### 3. Tool layer
Each tool is registered in a `ToolRegistry` so tool calls are logged and scored.

### 4. Trace layer
Every key decision is captured as a trace event:
- scenario start
- agent decisions
- handoffs
- tool calls
- injected faults
- recovery actions

### 5. Evaluation layer
Runs scenarios from a dataset and computes a weighted reliability score.

## Reliability dimensions

- task success
- tool precision
- handoff accuracy
- state retention
- recovery effectiveness
- safety policy adherence

## Upgrade path

- replace mock backend with MCP servers
- route traces to OpenTelemetry / LangSmith
- use OpenAI Agents SDK handoffs and guardrails
- add prompt or model comparison harness
