# AWS Agents vs LangChain

## The naming, sorted out

AWS actually has a few distinct things people lump together as "the Bedrock agent framework":

- **Amazon Bedrock Agents** ("Classic") — the original, low-code/no-code managed agent builder from 2023. You configure it through the console/API rather than writing an orchestration loop yourself. It's now called "Amazon Bedrock Agents Classic" and will stop accepting new customers starting July 30, 2026, with AWS steering everyone toward AgentCore instead.
- **Amazon Bedrock AgentCore** — the current focus. This is a *platform*, not a framework — it's designed to work with whatever framework and model you want, providing the production infrastructure (runtime, memory, identity, gateway, observability) around your agent code. You can start with LangChain, OpenAI Agents SDK, Claude Agent SDK, Strands SDK, or your own framework, and deploy it the same way.
- **Strands Agents SDK** — AWS's own open-source *agent-building* framework (the actual LangChain/LangGraph competitor). It's a lightweight, model-driven Python SDK released by AWS in May 2025. It's what people usually mean when they ask "what's AWS's answer to LangChain."

So: **Strands = the framework**, **AgentCore = the deployment platform**, **Bedrock Agents Classic = the old low-code option being sunset**.

## Strands vs. LangChain / LangGraph / LangSmith

| | Strands | LangChain / LangGraph | LangSmith |
|---|---|---|---|
| What it is | Agent-building SDK | Agent-building SDK + orchestration layer | Observability/eval platform |
| Control model | Model-driven — the model decides when to call tools and when to stop; the SDK just dispatches | Developer-first with explicit chains; LangGraph adds DAG-based, developer-defined workflows for fine-grained control | N/A |
| Multi-agent | Built-in Graph, Swarm, and agents-as-tools patterns | Pushes you to LangGraph for anything beyond basic AgentExecutor | — |
| MCP support | Native — can run an agent as an MCP server or consume MCP tools with no glue code | No native MCP support historically; relies on its own tool catalog instead | — |
| Ecosystem breadth | Smaller but growing; deep AWS/Bedrock integration | Wider array of built-in connectors given its maturity, historically strong with OpenAI and third-party services | Deep tracing/eval tied to LangChain ecosystem |
| Deployment target | Pairs natively with Bedrock AgentCore for hosted runtime, identity, and observability | Cloud-agnostic; deploy anywhere | Cloud-agnostic |

A practical rule of thumb that keeps showing up in comparisons: pick Strands if your deploy target is Bedrock AgentCore or MCP is central to your integration story; pick LangChain if you need RAG over a specific vector store, multiple model providers behind one interface, or LangSmith's evaluation tooling. And a common production pattern on AWS is to start with Strands + AgentCore for speed, then add LangGraph for any sub-workflow where step-by-step auditability or strict ordering is non-negotiable — treating them as complementary rather than exclusive.

Worth noting: LangChain and LangGraph aren't really separate competitors anymore. As of LangChain 1.0 (November 2025), the new create_agent abstraction actually runs on LangGraph's durable runtime under the hood — so "LangChain vs LangGraph" is now more of an internal layering question than a fork in the road.

## Other AWS-adjacent competitors

Beyond Strands, a couple more AWS-associated options come up:

- **Agent Squad** — a separate AWS library focused specifically on multi-agent orchestration/routing to specialist agents with strict context isolation, meant for large ensembles of disparate agents rather than a single agent with tools.
- **Amazon Bedrock Managed Agents, powered by OpenAI** — combines OpenAI's frontier models and agent harness with AWS infrastructure for teams that specifically want to build on OpenAI's stack while staying on Bedrock.

And outside AWS entirely, the broader 2026 field includes Anthropic's Claude Agent SDK (extracted from Claude Code), OpenAI's Agents SDK (evolved from the experimental Swarm project), CrewAI, and AG2 (the community successor to Microsoft's AutoGen) — all of which AgentCore is designed to host regardless of which one you pick, since it's framework-agnostic by design.
