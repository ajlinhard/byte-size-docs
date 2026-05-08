# LangX Overview
There are three comprehensive markdown files — one each for LangChain, LangGraph, and LangSmith — going from beginner to advanced. Let me write them all out fully.Three comprehensive markdown files, each progressing from beginner to advanced:

**`langchain_python.md`** — 10 sections covering:
- Core LCEL concepts and first chains
- Prompt templates (basic, few-shot, dynamic selection)
- All output parsers (string, JSON, Pydantic, structured binding, list)
- Context & memory (manual, `RunnableWithMessageHistory`, Redis, trimming, summarisation)
- RAG pipelines (basic, citations, advanced retrieval, conversational RAG)
- Tools & agents (built-in, custom `@tool`, ReAct, OpenAI tools agent)
- Advanced patterns (branching, parallel, fallbacks, retry, rate limiting)
- Callbacks and LLM-as-a-judge output grading

**`langgraph_python.md`** — 10 sections covering:
- Graph primitives (nodes, edges, state, START/END)
- State management (reducers, `MessagesState`, custom reducers, private I/O schemas)
- Conditional edges & routing (basic routing, ReAct loops, retry loops)
- Human-in-the-loop (interrupts, dynamic breakpoints, mid-run state edits)
- Multi-agent patterns (supervisor, parallel fan-out with `Send`, handoff)
- Persistence (in-memory, SQLite, Postgres, state replay, long-term Store)
- Streaming (events, token-level, multiple modes, async)
- Subgraphs, composition, and FastAPI integration

**`langsmith_python.md`** — 10 sections covering:
- Auto-tracing setup (zero code changes)
- Manual `@traceable` and context managers
- Dataset creation (manual, from traces, from CSV)
- Evaluations (built-in, custom, LLM-as-judge, RAG-specific, A/B comparison)
- Prompt Hub (push, pull, versioning, A/B variants)
- Production monitoring (sampling, cost tracking, alerting)
- Human feedback & annotation queues
- CI/CD with GitHub Actions and pass/fail thresholds
- Advanced: online eval, conversation eval, prompt optimisation loops
