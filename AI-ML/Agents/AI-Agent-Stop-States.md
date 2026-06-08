## Stopping AI Agents at a Specific End State

The core challenge is defining *when* an agent is "done." Here are the main patterns:

---

### 1. Explicit Terminal State Check

The simplest approach: define a function that inspects the current state and returns `True` when done.

```python
def is_terminal(state: dict) -> bool:
    return (
        state["goal_reached"] == True or
        state["steps"] >= state["max_steps"] or
        state["error"] is not None
    )

while not is_terminal(state):
    state = agent.step(state)
```

This works well when you can enumerate all exit conditions clearly.

---

### 2. Sentinel / Special Action

The agent itself emits a special action (like `STOP` or `FINISH`) when it believes it's done. The loop watches for it.

```python
def run_agent(agent, state):
    while True:
        action = agent.decide(state)

        if action.type == "FINISH":
            return action.result   # agent declares it's done

        state = env.apply(state, action)
```

This is common in **ReAct-style agents** where the LLM outputs `Final Answer:` or similar.

---

### 3. Goal Condition Evaluator

Separate the *goal* from the *agent*. An independent evaluator checks whether the goal is satisfied — useful when success is fuzzy or hard to code explicitly.

```python
def goal_satisfied(state, goal) -> bool:
    # Could be a rule, a classifier, or even another LLM call
    return similarity(state["output"], goal["target"]) > 0.95

while not goal_satisfied(state, goal):
    action = agent.step(state)
    state = env.apply(state, action)
```

---

### 4. Safety Budget (Step / Token / Time Limit)

Always wrap agent loops in a budget to prevent infinite loops. This is a **hard stop** that runs alongside any other condition.

```python
MAX_STEPS = 50

for step in range(MAX_STEPS):
    if is_terminal(state):
        break
    state = agent.step(state)
else:
    raise AgentTimeoutError(f"Agent did not finish in {MAX_STEPS} steps")
```

---

### 5. Hierarchical / Supervisor Stop

A parent agent or orchestrator decides when a child agent should stop. Good for multi-agent systems.

```python
def supervisor_loop(supervisor, worker, state):
    while True:
        worker_output = worker.step(state)

        verdict = supervisor.evaluate(state, worker_output)

        if verdict == "ACCEPT":
            return worker_output       # supervisor approves → stop
        elif verdict == "REJECT":
            raise ValueError("Goal unachievable")
        else:
            state = worker_output      # supervisor says keep going
```

---

### Putting It All Together

In practice, combine multiple mechanisms for robustness:

```python
def run_agent(agent, initial_state, goal, max_steps=50):
    state = initial_state

    for step in range(max_steps):
        # 1. Check terminal state
        if is_terminal(state):
            return {"status": "terminal_state", "state": state}

        # 2. Check goal satisfaction
        if goal_satisfied(state, goal):
            return {"status": "success", "state": state}

        # 3. Agent picks an action (may include FINISH sentinel)
        action = agent.decide(state, goal)
        if action.type == "FINISH":
            return {"status": "agent_finish", "result": action.result}

        state = env.apply(state, action)

    # 4. Budget exhausted — hard stop
    return {"status": "timeout", "state": state}
```

---

### Choosing the Right Pattern

| Pattern | Best for |
|---|---|
| **Explicit terminal state** | Well-defined, enumerable end conditions |
| **Sentinel action** | LLM agents that reason about completion |
| **Goal evaluator** | Fuzzy success criteria, QA tasks |
| **Safety budget** | Always — use as a fallback on everything |
| **Supervisor** | Multi-agent systems, quality gates |

The key insight: **never rely on a single stopping mechanism.** A well-designed agent loop has both an agent-driven stop (sentinel or goal check) *and* an external hard limit (budget), so you're protected even if the agent's judgment fails.
