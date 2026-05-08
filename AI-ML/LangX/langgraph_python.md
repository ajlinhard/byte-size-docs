# LangGraph Python — Beginner to Advanced

> **Prerequisites:** Completed `langchain_python.md` or equivalent LangChain familiarity.  
> **Install:** `pip install langgraph langchain-openai langchain-core`

---

## Table of Contents

1. [What is LangGraph?](#1-what-is-langgraph)
2. [Your First Graph](#2-your-first-graph)
3. [State Management](#3-state-management)
4. [Conditional Edges & Routing](#4-conditional-edges--routing)
5. [Human-in-the-Loop](#5-human-in-the-loop)
6. [Multi-Agent Systems](#6-multi-agent-systems)
7. [Persistence & Checkpointing](#7-persistence--checkpointing)
8. [Streaming & Real-Time Output](#8-streaming--real-time-output)
9. [Subgraphs & Composition](#9-subgraphs--composition)
10. [Production Patterns](#10-production-patterns)

---

## 1. What is LangGraph?

LangGraph extends LangChain to build **stateful, multi-step workflows** modelled as directed graphs. Where LangChain chains are linear (`A → B → C`), LangGraph supports cycles, branching, and long-running processes with memory.

### When to use LangGraph over plain LangChain

| Use case | LangChain chains | LangGraph |
|---|---|---|
| One-shot Q&A | ✅ | overkill |
| Linear multi-step pipeline | ✅ | fine |
| Conditional routing | partial | ✅ |
| Loops until done | ❌ | ✅ |
| Human approval step | ❌ | ✅ |
| Multiple cooperating agents | ❌ | ✅ |
| Persistent, resumable workflows | ❌ | ✅ |

### Core vocabulary

| Term | Meaning |
|---|---|
| **State** | A typed dict shared across all nodes in a graph |
| **Node** | A Python function that reads state and returns updates |
| **Edge** | A connection from one node to the next |
| **Conditional edge** | An edge whose destination depends on the current state |
| **START / END** | Built-in sentinels marking graph entry and exit |
| **Checkpointer** | Saves state snapshots for persistence and replay |

---

## 2. Your First Graph

### 2.1 Minimal graph

```python
from langgraph.graph import StateGraph, END
from langchain_openai import ChatOpenAI
from langchain_core.messages import HumanMessage
from typing import TypedDict

model = ChatOpenAI(model="gpt-4o-mini")

# Step 1: Define your state schema
class SimpleState(TypedDict):
    question: str
    answer: str

# Step 2: Define nodes (functions that transform state)
def answer_node(state: SimpleState) -> SimpleState:
    """Call the LLM and store its response."""
    response = model.invoke([HumanMessage(content=state["question"])])
    return {"answer": response.content}

# Step 3: Build the graph
graph_builder = StateGraph(SimpleState)
graph_builder.add_node("answer", answer_node)

# Step 4: Define entry point and edges
graph_builder.set_entry_point("answer")
graph_builder.add_edge("answer", END)

# Step 5: Compile
graph = graph_builder.compile()

# Step 6: Run
result = graph.invoke({"question": "What is the capital of France?", "answer": ""})
print(result["answer"])  # "The capital of France is Paris."
```

### 2.2 Visualise the graph

```python
# Print ASCII representation
print(graph.get_graph().draw_ascii())

# Export to Mermaid diagram (paste into mermaid.live)
print(graph.get_graph().draw_mermaid())

# Save as PNG (requires graphviz)
# pip install pygraphviz
graph.get_graph().draw_png("my_graph.png")
```

### 2.3 Multi-node pipeline

```python
from typing import TypedDict, Annotated
import operator

class PipelineState(TypedDict):
    text: str
    summary: str
    keywords: list[str]
    sentiment: str

def summarise_node(state: PipelineState) -> dict:
    prompt = f"Summarise this in one sentence:\n\n{state['text']}"
    result = model.invoke([HumanMessage(content=prompt)])
    return {"summary": result.content}

def extract_keywords_node(state: PipelineState) -> dict:
    prompt = f"Extract 5 keywords as a comma-separated list from:\n\n{state['text']}"
    result = model.invoke([HumanMessage(content=prompt)])
    return {"keywords": [k.strip() for k in result.content.split(",")]}

def analyse_sentiment_node(state: PipelineState) -> dict:
    prompt = f"Classify the sentiment as positive/neutral/negative:\n\n{state['text']}"
    result = model.invoke([HumanMessage(content=prompt)])
    return {"sentiment": result.content.strip().lower()}

builder = StateGraph(PipelineState)
builder.add_node("summarise",         summarise_node)
builder.add_node("extract_keywords",  extract_keywords_node)
builder.add_node("analyse_sentiment", analyse_sentiment_node)

builder.set_entry_point("summarise")
builder.add_edge("summarise",         "extract_keywords")
builder.add_edge("extract_keywords",  "analyse_sentiment")
builder.add_edge("analyse_sentiment", END)

pipeline = builder.compile()

result = pipeline.invoke({
    "text": "The product launch exceeded all expectations. Customer feedback has been overwhelmingly positive and sales are up 40%.",
    "summary": "", "keywords": [], "sentiment": "",
})
print(result)
```

---

## 3. State Management

### 3.1 Reducers — merging state updates

By default, each node's return value **replaces** the corresponding state key. Use `Annotated` with a reducer to change this behaviour.

```python
from typing import Annotated
import operator

class AccumulatingState(TypedDict):
    messages: Annotated[list, operator.add]   # appends each update to the list
    step_count: int                            # replaced on each update
    errors: Annotated[list, operator.add]     # appends errors

def step_one(state: AccumulatingState) -> dict:
    return {
        "messages": ["step one complete"],     # appended, not replaced
        "step_count": state["step_count"] + 1,
    }

def step_two(state: AccumulatingState) -> dict:
    return {
        "messages": ["step two complete"],     # appended again
        "step_count": state["step_count"] + 1,
    }
```

### 3.2 MessagesState — built-in for chat

```python
from langgraph.graph import MessagesState  # pre-built state with message accumulation
from langchain_core.messages import AIMessage, HumanMessage, SystemMessage

# MessagesState has a single key: messages: Annotated[list[BaseMessage], add_messages]
# add_messages is smarter than operator.add — it deduplicates by message ID

class ChatState(MessagesState):
    # Extend with your own fields
    user_name: str
    turn_count: int

def chat_node(state: ChatState) -> dict:
    messages = state["messages"]
    response = model.invoke(messages)
    return {
        "messages": [response],             # AIMessage appended to history
        "turn_count": state["turn_count"] + 1,
    }
```

### 3.3 Custom reducer functions

```python
from langgraph.graph.message import add_messages

def merge_unique(existing: list, new: list) -> list:
    """Custom reducer: merge lists, deduplicate by value."""
    return list(set(existing + new))

def take_latest(existing: any, new: any) -> any:
    """Custom reducer: always take the most recent value (same as default)."""
    return new

class CustomState(TypedDict):
    tags: Annotated[list[str], merge_unique]      # unique tags across all nodes
    messages: Annotated[list, add_messages]        # smart message dedup
    last_result: Annotated[str, take_latest]       # always latest value
```

### 3.4 Private state (input/output schemas)

```python
from typing import TypedDict

class PublicInput(TypedDict):
    """What callers pass in."""
    question: str
    user_id: str

class PublicOutput(TypedDict):
    """What callers receive back."""
    answer: str
    confidence: float

class InternalState(TypedDict):
    """Full state used internally — includes scratch space."""
    question: str
    user_id: str
    answer: str
    confidence: float
    _retrieved_docs: list        # internal only
    _reasoning_steps: list       # internal only

# Build the graph with the full internal state but expose only public I/O
builder = StateGraph(InternalState, input=PublicInput, output=PublicOutput)
```

---

## 4. Conditional Edges & Routing

### 4.1 Basic conditional edge

```python
from langgraph.graph import END

class RouterState(TypedDict):
    question: str
    answer: str
    needs_web_search: bool

def classify_node(state: RouterState) -> dict:
    """Decide if we need to search the web."""
    prompt = f"""Does this question require current information from the web? 
Question: {state['question']}
Reply with only: yes or no"""
    result = model.invoke([HumanMessage(content=prompt)])
    return {"needs_web_search": "yes" in result.content.lower()}

def web_search_node(state: RouterState) -> dict:
    # Simulate web search
    return {"answer": f"[Web search result for: {state['question']}]"}

def llm_answer_node(state: RouterState) -> dict:
    result = model.invoke([HumanMessage(content=state["question"])])
    return {"answer": result.content}

def route(state: RouterState) -> str:
    """Return the name of the next node."""
    return "web_search" if state["needs_web_search"] else "llm_answer"

builder = StateGraph(RouterState)
builder.add_node("classify",   classify_node)
builder.add_node("web_search", web_search_node)
builder.add_node("llm_answer", llm_answer_node)

builder.set_entry_point("classify")

# Conditional edge: call `route` to decide which node to go to
builder.add_conditional_edges(
    "classify",
    route,
    {
        "web_search": "web_search",
        "llm_answer": "llm_answer",
    },
)

builder.add_edge("web_search", END)
builder.add_edge("llm_answer", END)

graph = builder.compile()
```

### 4.2 ReAct agent loop (the classic pattern)

```python
from langchain_core.tools import tool
from langchain_openai import ChatOpenAI
from langgraph.prebuilt import ToolNode

@tool
def add(a: float, b: float) -> float:
    """Add two numbers."""
    return a + b

@tool
def multiply(a: float, b: float) -> float:
    """Multiply two numbers."""
    return a * b

tools = [add, multiply]
model_with_tools = ChatOpenAI(model="gpt-4o-mini").bind_tools(tools)

class AgentState(MessagesState):
    pass

def agent_node(state: AgentState) -> dict:
    """The LLM decides whether to call a tool or give a final answer."""
    response = model_with_tools.invoke(state["messages"])
    return {"messages": [response]}

def should_continue(state: AgentState) -> str:
    """If the last message has tool_calls, go to tools; otherwise end."""
    last = state["messages"][-1]
    if hasattr(last, "tool_calls") and last.tool_calls:
        return "tools"
    return END

tool_node = ToolNode(tools)  # built-in node that executes tool calls

builder = StateGraph(AgentState)
builder.add_node("agent", agent_node)
builder.add_node("tools", tool_node)

builder.set_entry_point("agent")
builder.add_conditional_edges("agent", should_continue)
builder.add_edge("tools", "agent")   # after tool execution, go back to agent

agent_graph = builder.compile()

result = agent_graph.invoke({
    "messages": [HumanMessage(content="What is (3 + 4) * 5?")]
})
print(result["messages"][-1].content)  # "35"
```

### 4.3 Multi-step retry loop

```python
class RetryState(TypedDict):
    task: str
    result: str
    attempts: int
    quality_score: float
    max_attempts: int

def generate_node(state: RetryState) -> dict:
    result = model.invoke([HumanMessage(content=state["task"])])
    return {"result": result.content, "attempts": state["attempts"] + 1}

def grade_node(state: RetryState) -> dict:
    """Score the result on a 0-1 scale."""
    prompt = f"""Rate the quality of this response from 0.0 to 1.0:
Task: {state['task']}
Response: {state['result']}
Output ONLY a number between 0.0 and 1.0."""
    score_str = model.invoke([HumanMessage(content=prompt)]).content
    try:
        score = float(score_str.strip())
    except ValueError:
        score = 0.5
    return {"quality_score": score}

def retry_or_end(state: RetryState) -> str:
    if state["quality_score"] >= 0.8:
        return END
    if state["attempts"] >= state["max_attempts"]:
        return END
    return "generate"

builder = StateGraph(RetryState)
builder.add_node("generate", generate_node)
builder.add_node("grade",    grade_node)

builder.set_entry_point("generate")
builder.add_edge("generate", "grade")
builder.add_conditional_edges("grade", retry_or_end)

retry_graph = builder.compile()

result = retry_graph.invoke({
    "task": "Write a haiku about programming",
    "result": "", "attempts": 0, "quality_score": 0.0, "max_attempts": 3,
})
print(f"Final result (after {result['attempts']} attempts): {result['result']}")
```

---

## 5. Human-in-the-Loop

### 5.1 Interrupt before a node

```python
from langgraph.checkpoint.memory import MemorySaver
from langgraph.types import interrupt

checkpointer = MemorySaver()

class ApprovalState(TypedDict):
    task: str
    plan: str
    approved: bool
    result: str

def plan_node(state: ApprovalState) -> dict:
    result = model.invoke([HumanMessage(content=f"Create a step-by-step plan to: {state['task']}")])
    return {"plan": result.content}

def approval_node(state: ApprovalState) -> dict:
    """Interrupt here — wait for human to approve/reject."""
    human_input = interrupt({
        "message": "Please review the plan and respond with 'approve' or 'reject':",
        "plan": state["plan"],
    })
    return {"approved": human_input.lower().strip() == "approve"}

def execute_node(state: ApprovalState) -> dict:
    if not state["approved"]:
        return {"result": "Task cancelled by human reviewer."}
    result = model.invoke([HumanMessage(content=f"Execute this plan:\n{state['plan']}")])
    return {"result": result.content}

builder = StateGraph(ApprovalState)
builder.add_node("plan",     plan_node)
builder.add_node("approval", approval_node)
builder.add_node("execute",  execute_node)

builder.set_entry_point("plan")
builder.add_edge("plan",     "approval")
builder.add_edge("approval", "execute")
builder.add_edge("execute",  END)

# Checkpointer is REQUIRED for human-in-the-loop
graph = builder.compile(checkpointer=checkpointer)

config = {"configurable": {"thread_id": "task-001"}}

# First run — pauses at approval_node
state = graph.invoke(
    {"task": "Set up a CI/CD pipeline", "plan": "", "approved": False, "result": ""},
    config=config,
)
print("Interrupted. Current plan:", state["plan"])
```

```python
# Resume after human reviews
# Pass the human's response via Command
from langgraph.types import Command

final_state = graph.invoke(
    Command(resume="approve"),
    config=config,
)
print(final_state["result"])
```

### 5.2 Interrupt with dynamic breakpoints

```python
# Compile with always-on breakpoints at specific nodes
graph = builder.compile(
    checkpointer=checkpointer,
    interrupt_before=["execute"],       # always pause before execute
    interrupt_after=["plan"],           # always pause after plan
)

# Or set breakpoints per-invocation
graph.invoke(
    initial_state,
    config={**config, "interrupt_before": ["execute"]},
)
```

### 5.3 Edit state mid-run

```python
# After an interrupt, inspect and edit the state before resuming
current_state = graph.get_state(config)
print(current_state.values["plan"])

# Update a state value before resuming
graph.update_state(
    config,
    {"plan": "Revised plan: Step 1 → Step 2 → Step 3"},
    as_node="plan",   # as if this update came from the plan node
)

# Now resume
final = graph.invoke(None, config=config)
```

---

## 6. Multi-Agent Systems

### 6.1 Supervisor pattern

```python
from langchain_core.prompts import ChatPromptTemplate
from langgraph.graph import END

class SupervisorState(TypedDict):
    messages: Annotated[list, add_messages]
    next_agent: str
    task_complete: bool

# --- Worker agents ---

def researcher_node(state: SupervisorState) -> dict:
    """Specialises in finding facts."""
    system = "You are a research specialist. Find relevant facts and data."
    messages = [SystemMessage(content=system)] + state["messages"]
    result = model.invoke(messages)
    return {"messages": [AIMessage(content=f"[Researcher]: {result.content}")]}

def writer_node(state: SupervisorState) -> dict:
    """Specialises in writing clear prose."""
    system = "You are a professional writer. Turn research notes into clear, engaging prose."
    messages = [SystemMessage(content=system)] + state["messages"]
    result = model.invoke(messages)
    return {"messages": [AIMessage(content=f"[Writer]: {result.content}")]}

def reviewer_node(state: SupervisorState) -> dict:
    """Reviews and provides feedback."""
    system = "You are a critical editor. Review the draft and provide specific improvement suggestions."
    messages = [SystemMessage(content=system)] + state["messages"]
    result = model.invoke(messages)
    return {"messages": [AIMessage(content=f"[Reviewer]: {result.content}")]}

# --- Supervisor ---

members = ["researcher", "writer", "reviewer"]

supervisor_prompt = ChatPromptTemplate.from_messages([
    ("system", f"""You are a team supervisor managing: {members}.
Given the conversation, decide who should act next.
Reply ONLY with one of: {', '.join(members)}, or FINISH if the task is complete."""),
    ("human", "Current messages:\n{messages}\n\nWho should act next?"),
])

def supervisor_node(state: SupervisorState) -> dict:
    formatted = "\n".join(
        f"{m.type}: {m.content}" for m in state["messages"][-6:]  # last 6 messages
    )
    chain = supervisor_prompt | model | StrOutputParser()
    next_agent = chain.invoke({"messages": formatted}).strip().lower()
    task_complete = "finish" in next_agent
    return {"next_agent": next_agent, "task_complete": task_complete}

def route_to_agent(state: SupervisorState) -> str:
    if state["task_complete"]:
        return END
    return state["next_agent"]

builder = StateGraph(SupervisorState)
builder.add_node("supervisor", supervisor_node)
builder.add_node("researcher", researcher_node)
builder.add_node("writer",     writer_node)
builder.add_node("reviewer",   reviewer_node)

builder.set_entry_point("supervisor")
builder.add_conditional_edges("supervisor", route_to_agent)

for member in members:
    builder.add_edge(member, "supervisor")   # all workers report back to supervisor

team_graph = builder.compile()

result = team_graph.invoke({
    "messages": [HumanMessage(content="Write a short article about the James Webb Space Telescope")],
    "next_agent": "",
    "task_complete": False,
})
```

### 6.2 Parallel agent execution

```python
from langgraph.constants import Send

class ParallelState(TypedDict):
    topic: str
    perspectives: Annotated[list[str], operator.add]   # accumulates results from all parallel agents
    final_synthesis: str

def generate_perspective(state: dict) -> dict:
    """Worker that generates one perspective on a topic."""
    role = state["role"]
    topic = state["topic"]
    prompt = f"As a {role}, give your perspective on: {topic}. Be concise (2-3 sentences)."
    result = model.invoke([HumanMessage(content=prompt)])
    return {"perspectives": [f"[{role}]: {result.content}"]}

def synthesise_node(state: ParallelState) -> dict:
    """Combine all perspectives into a synthesis."""
    perspectives_text = "\n\n".join(state["perspectives"])
    prompt = f"Synthesise these perspectives on '{state['topic']}':\n\n{perspectives_text}"
    result = model.invoke([HumanMessage(content=prompt)])
    return {"final_synthesis": result.content}

def fan_out(state: ParallelState) -> list[Send]:
    """Launch one worker per perspective in parallel."""
    roles = ["economist", "environmentalist", "technologist", "sociologist"]
    return [
        Send("get_perspective", {"role": role, "topic": state["topic"]})
        for role in roles
    ]

builder = StateGraph(ParallelState)
builder.add_node("get_perspective", generate_perspective)
builder.add_node("synthesise",      synthesise_node)

builder.set_entry_point("fan_out_node")
builder.add_node("fan_out_node", lambda s: {})   # no-op entry node
builder.add_conditional_edges("fan_out_node", fan_out)   # fan out
builder.add_edge("get_perspective", "synthesise")        # fan in
builder.add_edge("synthesise", END)
```

### 6.3 Handoff pattern (agent-to-agent)

```python
from langgraph.prebuilt import InjectedState
from langchain_core.tools import tool

# An agent can transfer control to another agent via a "handoff" tool
@tool
def transfer_to_billing(state: Annotated[dict, InjectedState]) -> str:
    """Transfer the user to the billing specialist agent."""
    # In a real system this would update a routing field in state
    return "Transferring you to billing..."

@tool
def transfer_to_technical_support(state: Annotated[dict, InjectedState]) -> str:
    """Transfer the user to the technical support agent."""
    return "Transferring you to technical support..."

# Each agent has access to handoff tools in addition to their domain tools
triage_tools = [transfer_to_billing, transfer_to_technical_support]
billing_tools = [transfer_to_technical_support]   # billing can escalate to tech
```

---

## 7. Persistence & Checkpointing

### 7.1 In-memory checkpointer

```python
from langgraph.checkpoint.memory import MemorySaver

checkpointer = MemorySaver()
graph = builder.compile(checkpointer=checkpointer)

config = {"configurable": {"thread_id": "conversation-123"}}

# Each invoke with the same thread_id continues from where it left off
graph.invoke({"messages": [HumanMessage(content="Hello, I'm Bob")]}, config=config)
result = graph.invoke({"messages": [HumanMessage(content="What's my name?")]}, config=config)
print(result["messages"][-1].content)  # "Your name is Bob."
```

### 7.2 SQLite checkpointer (persists across restarts)

```python
from langgraph.checkpoint.sqlite import SqliteSaver

# Persists to a local SQLite database
with SqliteSaver.from_conn_string("checkpoints.db") as checkpointer:
    graph = builder.compile(checkpointer=checkpointer)
    config = {"configurable": {"thread_id": "session-abc"}}

    # Even if you restart the process, this thread continues
    result = graph.invoke({"messages": [HumanMessage(content="Remember: my PIN is 4242")]}, config=config)
```

### 7.3 PostgreSQL checkpointer (production)

```python
# pip install langgraph-checkpoint-postgres psycopg
from langgraph.checkpoint.postgres import PostgresSaver

DB_URI = "postgresql://user:password@localhost:5432/langgraph"

with PostgresSaver.from_conn_string(DB_URI) as checkpointer:
    checkpointer.setup()   # creates tables on first run
    graph = builder.compile(checkpointer=checkpointer)
```

### 7.4 Inspecting and replaying state

```python
# Get current state
state = graph.get_state(config)
print(state.values)          # dict of current state
print(state.next)            # which nodes run next
print(state.metadata)        # step count, timestamps, etc.
print(state.config)          # the config used
print(state.created_at)      # when this state was created

# Get full history (all checkpoints for this thread)
for checkpoint in graph.get_state_history(config):
    print(f"Step {checkpoint.metadata['step']}: {checkpoint.values}")

# Replay from a specific point in history
old_checkpoint = list(graph.get_state_history(config))[3]
result = graph.invoke(None, config=old_checkpoint.config)  # replay from step 3
```

### 7.5 Long-term memory with Store

```python
from langgraph.store.memory import InMemoryStore
from langgraph.store.base import BaseStore
from langgraph.prebuilt import InjectedStore
from typing import Annotated

store = InMemoryStore()

def memory_node(
    state: AgentState,
    store: Annotated[BaseStore, InjectedStore()],
) -> dict:
    user_id = state.get("user_id", "default")

    # Retrieve memories for this user
    memories = store.search(("memories", user_id), query=state["messages"][-1].content)
    memory_context = "\n".join(m.value["content"] for m in memories)

    # Get answer using memories
    prompt = f"User memories:\n{memory_context}\n\nQuestion: {state['messages'][-1].content}"
    response = model.invoke([HumanMessage(content=prompt)])

    # Save the new interaction as a memory
    store.put(
        ("memories", user_id),
        key=f"mem-{len(memories)}",
        value={"content": f"User said: {state['messages'][-1].content}"},
    )

    return {"messages": [response]}

# Compile with the store
graph = builder.compile(store=store, checkpointer=checkpointer)
```

---

## 8. Streaming & Real-Time Output

### 8.1 Stream graph events

```python
# Stream all events as they happen
for event in graph.stream({"messages": [HumanMessage(content="Plan a trip to Kyoto")]}, config=config):
    for node_name, node_output in event.items():
        print(f"=== {node_name} ===")
        print(node_output)
```

### 8.2 Stream tokens (LLM tokens in real time)

```python
# stream_mode="messages" streams individual tokens
for msg, metadata in graph.stream(
    {"messages": [HumanMessage(content="Write a short story")]},
    config=config,
    stream_mode="messages",
):
    if isinstance(msg, AIMessageChunk):
        print(msg.content, end="", flush=True)
```

### 8.3 Multiple stream modes simultaneously

```python
# stream_mode can be a list — get multiple event types at once
for event in graph.stream(
    input_state,
    config=config,
    stream_mode=["updates", "messages", "values"],
):
    mode, data = event
    if mode == "updates":
        print(f"Node updated: {list(data.keys())}")
    elif mode == "messages":
        msg, meta = data
        if hasattr(msg, "content"):
            print(msg.content, end="")
    elif mode == "values":
        print(f"Full state: {data}")
```

### 8.4 Async streaming

```python
import asyncio

async def stream_agent_response(question: str):
    config = {"configurable": {"thread_id": "async-001"}}
    async for event in graph.astream(
        {"messages": [HumanMessage(content=question)]},
        config=config,
        stream_mode="messages",
    ):
        msg, metadata = event
        if hasattr(msg, "content") and msg.content:
            print(msg.content, end="", flush=True)
    print()

asyncio.run(stream_agent_response("Explain how neural networks learn"))
```

---

## 9. Subgraphs & Composition

### 9.1 Nesting graphs

```python
# A subgraph is just a compiled graph used as a node in a parent graph
class ResearchState(TypedDict):
    query: str
    sources: list[str]
    summary: str

# Build and compile the subgraph
research_builder = StateGraph(ResearchState)
research_builder.add_node("fetch", fetch_sources_node)
research_builder.add_node("summarise", summarise_sources_node)
research_builder.set_entry_point("fetch")
research_builder.add_edge("fetch", "summarise")
research_builder.add_edge("summarise", END)
research_subgraph = research_builder.compile()

# Use it as a node in the parent graph
class MainState(TypedDict):
    user_request: str
    research_query: str
    research_summary: str
    final_answer: str

def prepare_research(state: MainState) -> dict:
    return {"research_query": f"facts about {state['user_request']}"}

def use_research_results(state: MainState) -> dict:
    answer = model.invoke([HumanMessage(content=f"Based on: {state['research_summary']}\n\nAnswer: {state['user_request']}")])
    return {"final_answer": answer.content}

main_builder = StateGraph(MainState)
main_builder.add_node("prepare",     prepare_research)
main_builder.add_node("research",    research_subgraph)  # subgraph as a node
main_builder.add_node("finalise",    use_research_results)

main_builder.set_entry_point("prepare")
main_builder.add_edge("prepare",  "research")
main_builder.add_edge("research", "finalise")
main_builder.add_edge("finalise", END)
```

### 9.2 Composing reusable node factories

```python
def make_llm_node(system_prompt: str, output_key: str):
    """Factory that creates a node with a given system prompt."""
    def node(state: dict) -> dict:
        messages = [SystemMessage(content=system_prompt)] + state.get("messages", [])
        response = model.invoke(messages)
        return {output_key: response.content, "messages": [response]}
    return node

# Create specialised nodes from the factory
researcher = make_llm_node("You are a research specialist.", "research_notes")
copywriter = make_llm_node("You are a professional copywriter.", "draft_copy")
editor     = make_llm_node("You are a critical editor.", "feedback")
```

---

## 10. Production Patterns

### 10.1 Error handling & graceful degradation

```python
from langgraph.errors import GraphInterrupt, NodeInterrupt

def safe_llm_node(state: AgentState) -> dict:
    """Node with comprehensive error handling."""
    try:
        response = model.invoke(state["messages"])
        return {"messages": [response]}
    except Exception as e:
        # Log the error and add a graceful error message
        print(f"LLM error: {e}")
        return {
            "messages": [AIMessage(content="I encountered an issue. Please try again.")],
            "error": str(e),
        }

def validation_node(state: AgentState) -> dict:
    """Interrupt if something critical is wrong."""
    if not state.get("user_id"):
        raise NodeInterrupt("user_id is required but not provided")
    return {}
```

### 10.2 Timeout and resource limits

```python
import asyncio
from contextlib import asynccontextmanager

@asynccontextmanager
async def timeout_context(seconds: float):
    try:
        async with asyncio.timeout(seconds):
            yield
    except asyncio.TimeoutError:
        raise Exception(f"Graph execution timed out after {seconds}s")

async def run_with_timeout(graph, input_state, config, timeout=30.0):
    async with timeout_context(timeout):
        return await graph.ainvoke(input_state, config=config)
```

### 10.3 LangGraph Platform deployment

```python
# langgraph.json (project root)
{
  "dependencies": ["."],
  "graphs": {
    "agent": "./my_agent/graph.py:graph",
    "research_team": "./my_agent/research.py:team_graph"
  },
  "env": ".env"
}

# Deploy locally for testing:
# langgraph dev

# Deploy to LangGraph Cloud:
# langgraph deploy --config langgraph.json
```

### 10.4 FastAPI integration

```python
from fastapi import FastAPI
from pydantic import BaseModel
from langgraph.checkpoint.sqlite import SqliteSaver
from fastapi.responses import StreamingResponse
import json

app = FastAPI()

with SqliteSaver.from_conn_string("prod.db") as checkpointer:
    compiled_graph = builder.compile(checkpointer=checkpointer)

class InvokeRequest(BaseModel):
    thread_id: str
    message: str

@app.post("/invoke")
async def invoke(request: InvokeRequest):
    config = {"configurable": {"thread_id": request.thread_id}}
    result = await compiled_graph.ainvoke(
        {"messages": [HumanMessage(content=request.message)]},
        config=config,
    )
    return {"reply": result["messages"][-1].content, "thread_id": request.thread_id}

@app.get("/stream")
async def stream(thread_id: str, message: str):
    config = {"configurable": {"thread_id": thread_id}}

    async def event_generator():
        async for msg, metadata in compiled_graph.astream(
            {"messages": [HumanMessage(content=message)]},
            config=config,
            stream_mode="messages",
        ):
            if hasattr(msg, "content") and msg.content:
                yield f"data: {json.dumps({'token': msg.content})}\n\n"
        yield "data: [DONE]\n\n"

    return StreamingResponse(event_generator(), media_type="text/event-stream")

@app.get("/history/{thread_id}")
async def get_history(thread_id: str):
    config = {"configurable": {"thread_id": thread_id}}
    history = []
    for state in compiled_graph.get_state_history(config):
        history.append({
            "step": state.metadata.get("step"),
            "created_at": str(state.created_at),
            "messages": [{"role": m.type, "content": m.content} for m in state.values.get("messages", [])],
        })
    return {"thread_id": thread_id, "history": history}
```

### 10.5 Testing graphs

```python
import pytest

@pytest.fixture
def test_graph():
    """Fresh in-memory graph for each test."""
    checkpointer = MemorySaver()
    return builder.compile(checkpointer=checkpointer)

def test_agent_answers_question(test_graph):
    config = {"configurable": {"thread_id": "test-001"}}
    result = test_graph.invoke(
        {"messages": [HumanMessage(content="What is 2 + 2?")]},
        config=config,
    )
    assert "4" in result["messages"][-1].content

def test_agent_maintains_context(test_graph):
    config = {"configurable": {"thread_id": "test-002"}}
    test_graph.invoke({"messages": [HumanMessage(content="My name is Alice")]}, config=config)
    result = test_graph.invoke({"messages": [HumanMessage(content="What is my name?")]}, config=config)
    assert "alice" in result["messages"][-1].content.lower()

def test_state_after_execution(test_graph):
    config = {"configurable": {"thread_id": "test-003"}}
    test_graph.invoke({"messages": [HumanMessage(content="Hello")]}, config=config)
    state = test_graph.get_state(config)
    assert len(state.values["messages"]) > 0
    assert state.next == ()  # graph has finished
```

---

*Next steps: see `langsmith_python.md` to trace, debug, evaluate, and monitor these graphs in production.*
