# LangSmith Python — Beginner to Advanced

> **Prerequisites:** LangChain and/or LangGraph setup complete.  
> **Install:** `pip install langsmith langchain langchain-openai`  
> **Sign up:** https://smith.langchain.com — get your API key from Settings.

---

## Table of Contents

1. [What is LangSmith?](#1-what-is-langsmith)
2. [Setup & Auto-Tracing](#2-setup--auto-tracing)
3. [Manual Tracing with @traceable](#3-manual-tracing-with-traceable)
4. [Datasets & Test Cases](#4-datasets--test-cases)
5. [Evaluations](#5-evaluations)
6. [Prompt Management](#6-prompt-management)
7. [Monitoring in Production](#7-monitoring-in-production)
8. [Feedback & Human Review](#8-feedback--human-review)
9. [CI/CD Integration](#9-cicd-integration)
10. [Advanced Patterns](#10-advanced-patterns)

---

## 1. What is LangSmith?

LangSmith is an observability, evaluation, and experimentation platform for LLM applications. It works alongside LangChain and LangGraph but can also be used independently.

### Core capabilities

| Feature | What it gives you |
|---|---|
| **Tracing** | Full visibility into every LLM call, tool use, and chain step |
| **Datasets** | Versioned test cases and golden examples |
| **Evaluations** | Automated scoring of your app's outputs |
| **Experiments** | Compare model/prompt changes side-by-side |
| **Prompt Hub** | Version-controlled prompt management |
| **Monitoring** | Production dashboards, error tracking, feedback collection |
| **Annotation queues** | Route outputs for human review |

### The LangSmith data model

```
Project
  └── Runs (one per invocation)
        ├── Inputs + Outputs
        ├── Start/End time
        ├── Token counts + costs
        ├── Tags + metadata
        ├── Feedback scores
        └── Child runs (nested LLM calls, tool calls)
```

---

## 2. Setup & Auto-Tracing

### 2.1 Environment configuration

```python
# .env file
LANGCHAIN_TRACING_V2=true
LANGCHAIN_API_KEY=ls__...
LANGCHAIN_PROJECT=my-project-name     # optional: default project if not set
OPENAI_API_KEY=sk-...

# Python
from dotenv import load_dotenv
load_dotenv()
```

That's it. With `LANGCHAIN_TRACING_V2=true` set, **every LangChain and LangGraph call is automatically traced** — no code changes needed.

### 2.2 Programmatic configuration

```python
import os
from langsmith import Client

os.environ["LANGCHAIN_TRACING_V2"] = "true"
os.environ["LANGCHAIN_API_KEY"] = "ls__..."
os.environ["LANGCHAIN_PROJECT"] = "production-chatbot"

client = Client()  # connects to https://api.smith.langchain.com
```

### 2.3 What gets traced automatically

When tracing is enabled, every invocation creates a run tree:

```
chain.invoke({"question": "..."})
  └── RunnableSequence               ← the chain
        ├── ChatPromptTemplate        ← prompt formatting
        ├── ChatOpenAI                ← LLM call (with token counts)
        │     ├── input messages
        │     ├── output message
        │     ├── model: gpt-4o-mini
        │     ├── tokens: 342 prompt, 89 completion
        │     └── latency: 1.23s
        └── StrOutputParser           ← output parsing
```

### 2.4 Per-invocation project and metadata

```python
# Override project on a per-call basis
result = chain.invoke(
    {"question": "What is a quasar?"},
    config={
        "run_name": "astronomy-qa",          # friendly name in the UI
        "tags": ["astronomy", "v2"],          # filterable tags
        "metadata": {
            "user_id": "user-123",
            "session_id": "sess-abc",
            "environment": "production",
        },
        "project_name": "astronomy-bot",     # override project
    },
)
```

---

## 3. Manual Tracing with @traceable

### 3.1 Basic @traceable

```python
from langsmith import traceable

@traceable(name="fetch-user-profile")
def get_user_profile(user_id: str) -> dict:
    """Any function decorated with @traceable is automatically traced."""
    # Simulate a DB call
    return {"id": user_id, "name": "Alice", "tier": "premium"}

@traceable(name="personalised-response")
def personalised_qa(user_id: str, question: str) -> str:
    profile = get_user_profile(user_id)     # nested call — shows as child run
    context = f"User: {profile['name']}, Tier: {profile['tier']}"
    result = chain.invoke({"question": f"{context}\n\nQuestion: {question}"})
    return result

# Both calls appear in LangSmith with parent-child relationship
answer = personalised_qa("user-123", "What features do I have access to?")
```

### 3.2 @traceable with metadata and tags

```python
@traceable(
    name="document-qa",
    run_type="chain",          # chain | llm | tool | retriever | embedding
    tags=["rag", "v3"],
    metadata={"pipeline_version": "3.1"},
)
def document_qa(question: str, doc_ids: list[str]) -> str:
    docs = retrieve_docs(doc_ids)
    context = "\n\n".join(d.page_content for d in docs)
    return chain.invoke({"question": question, "context": context})
```

### 3.3 Trace context manager

```python
from langsmith import trace

def process_batch(items: list[str]) -> list[str]:
    results = []
    for i, item in enumerate(items):
        # Manual trace with context manager
        with trace(
            name=f"process-item-{i}",
            run_type="chain",
            inputs={"item": item},
            tags=["batch"],
        ) as run:
            result = chain.invoke({"question": item})
            run.end(outputs={"result": result})
            results.append(result)
    return results
```

### 3.4 Tracing non-LangChain code

```python
from langsmith import traceable
import anthropic
import openai

# Wrap any LLM SDK with @traceable
@traceable(run_type="llm", name="openai-direct-call")
def call_openai_directly(prompt: str) -> str:
    client = openai.OpenAI()
    response = client.chat.completions.create(
        model="gpt-4o-mini",
        messages=[{"role": "user", "content": prompt}],
    )
    return response.choices[0].message.content

@traceable(run_type="retriever", name="custom-retriever")
def my_custom_retriever(query: str) -> list[dict]:
    """Trace a custom retriever that doesn't use LangChain."""
    # Your custom retrieval logic here
    return [{"content": "result 1"}, {"content": "result 2"}]
```

### 3.5 Adding feedback programmatically

```python
from langsmith import Client, traceable
from langsmith.run_helpers import get_current_run_tree

client = Client()

@traceable(name="answer-question")
def answer_with_feedback(question: str, expected: str) -> str:
    run_tree = get_current_run_tree()
    answer = chain.invoke({"question": question})

    # Add automated feedback on the current run
    if run_tree:
        is_correct = expected.lower() in answer.lower()
        client.create_feedback(
            run_id=run_tree.id,
            key="correctness",
            score=1.0 if is_correct else 0.0,
            comment=f"Expected '{expected}' in response",
        )

    return answer
```

---

## 4. Datasets & Test Cases

### 4.1 Create a dataset

```python
from langsmith import Client

client = Client()

# Create a dataset
dataset = client.create_dataset(
    dataset_name="qa-golden-set",
    description="Golden Q&A pairs for regression testing",
)

# Add examples one by one
client.create_example(
    inputs={"question": "What is the capital of France?"},
    outputs={"answer": "Paris"},
    dataset_id=dataset.id,
)

# Add multiple examples at once
examples = [
    {
        "inputs":  {"question": "What is photosynthesis?"},
        "outputs": {"answer": "The process by which plants convert sunlight to glucose"},
    },
    {
        "inputs":  {"question": "Who invented the telephone?"},
        "outputs": {"answer": "Alexander Graham Bell"},
    },
    {
        "inputs":  {"question": "What is the speed of light?"},
        "outputs": {"answer": "approximately 299,792,458 metres per second"},
    },
]

client.create_examples(
    inputs=[e["inputs"] for e in examples],
    outputs=[e["outputs"] for e in examples],
    dataset_id=dataset.id,
)

print(f"Dataset ID: {dataset.id}")
print(f"Dataset URL: {dataset.url}")
```

### 4.2 Create dataset from existing traces

```python
# Filter runs from a project and add the good ones to a dataset
runs = client.list_runs(
    project_name="production-chatbot",
    filter='and(eq(feedback_key, "correctness"), eq(feedback_score, 1))',
    limit=100,
)

dataset = client.create_dataset("production-golden-set")
client.create_examples(
    inputs=[r.inputs for r in runs],
    outputs=[r.outputs for r in runs],
    dataset_id=dataset.id,
)
```

### 4.3 Create dataset from CSV

```python
import csv
from io import StringIO

csv_content = """question,answer
What is the GIL in Python?,A mutex that allows only one thread to execute Python bytecode at a time
What is a decorator?,A function that wraps another function to modify its behaviour
What is list comprehension?,"A concise way to create lists: [x*2 for x in range(10)]"
"""

dataset = client.create_dataset("python-concepts")
reader = csv.DictReader(StringIO(csv_content))

for row in reader:
    client.create_example(
        inputs={"question": row["question"]},
        outputs={"answer": row["answer"]},
        dataset_id=dataset.id,
    )
```

### 4.4 Retrieve and update datasets

```python
# List all datasets
for dataset in client.list_datasets():
    print(f"{dataset.name}: {dataset.example_count} examples")

# Get a specific dataset
dataset = client.read_dataset(dataset_name="qa-golden-set")

# List examples in a dataset
for example in client.list_examples(dataset_id=dataset.id):
    print(f"Input: {example.inputs}")
    print(f"Output: {example.outputs}")

# Update an example
client.update_example(
    example_id=example.id,
    inputs={"question": "Updated question text"},
    outputs={"answer": "Updated expected answer"},
)

# Delete an example
client.delete_example(example_id=example.id)
```

---

## 5. Evaluations

### 5.1 Run an evaluation with built-in evaluators

```python
from langsmith.evaluation import evaluate, LangChainStringEvaluator

def target(inputs: dict) -> dict:
    """The function being evaluated — must accept inputs dict, return outputs dict."""
    answer = chain.invoke({"question": inputs["question"]})
    return {"answer": answer}

# Built-in evaluators
results = evaluate(
    target,
    data="qa-golden-set",                    # dataset name or ID
    evaluators=[
        LangChainStringEvaluator("qa"),       # correctness vs reference
        LangChainStringEvaluator("criteria", config={"criteria": "conciseness"}),
        LangChainStringEvaluator("criteria", config={"criteria": "relevance"}),
    ],
    experiment_prefix="baseline-gpt4o-mini",
    max_concurrency=4,
)

print(results.to_pandas())
```

### 5.2 Custom evaluator functions

```python
from langsmith.schemas import Run, Example

def exact_match_evaluator(run: Run, example: Example) -> dict:
    """Check if the answer contains the expected text."""
    prediction = run.outputs.get("answer", "").lower()
    reference  = example.outputs.get("answer", "").lower()
    passed = reference in prediction
    return {
        "key": "exact_match",
        "score": 1.0 if passed else 0.0,
        "comment": f"Expected '{reference}' in response",
    }

def length_evaluator(run: Run, example: Example) -> dict:
    """Penalise responses that are too long."""
    words = len(run.outputs.get("answer", "").split())
    score = 1.0 if words <= 100 else max(0, 1 - (words - 100) / 200)
    return {
        "key": "response_length",
        "score": round(score, 2),
        "comment": f"Response had {words} words",
    }

results = evaluate(
    target,
    data="qa-golden-set",
    evaluators=[exact_match_evaluator, length_evaluator],
    experiment_prefix="custom-eval-v1",
)
```

### 5.3 LLM-as-a-judge evaluator

```python
from langsmith.evaluation import LangChainStringEvaluator
from langchain_openai import ChatOpenAI

judge_llm = ChatOpenAI(model="gpt-4o", temperature=0)  # use a strong model to judge

# Custom rubric evaluator
rubric_evaluator = LangChainStringEvaluator(
    "labeled_score_string",
    config={
        "criteria": {
            "accuracy": "Is the answer factually correct?",
            "completeness": "Does the answer fully address all parts of the question?",
            "clarity": "Is the answer written clearly and understandably?",
        },
        "normalize_by": 10,
    },
    prepare_data=lambda run, example: {
        "prediction": run.outputs.get("answer", ""),
        "reference":  example.outputs.get("answer", ""),
        "input":      example.inputs.get("question", ""),
    },
)

results = evaluate(
    target,
    data="qa-golden-set",
    evaluators=[rubric_evaluator],
    experiment_prefix="rubric-judge-v1",
)
```

### 5.4 RAG-specific evaluators

```python
def context_relevance_evaluator(run: Run, example: Example) -> dict:
    """Check if retrieved context is relevant to the question."""
    question = example.inputs.get("question", "")
    context  = run.outputs.get("context", "")

    prompt = f"""Rate from 0-10 how relevant this context is to answering the question.
Question: {question}
Context: {context}
Output ONLY a number."""

    score_str = judge_llm.invoke([HumanMessage(content=prompt)]).content
    try:
        score = float(score_str.strip()) / 10
    except:
        score = 0.5

    return {"key": "context_relevance", "score": score}

def faithfulness_evaluator(run: Run, example: Example) -> dict:
    """Check if the answer is grounded in the retrieved context."""
    answer  = run.outputs.get("answer", "")
    context = run.outputs.get("context", "")

    prompt = f"""Does the following answer contain ONLY information that can be found in the context?
Context: {context}
Answer: {answer}
Reply with: yes or no"""

    verdict = judge_llm.invoke([HumanMessage(content=prompt)]).content.strip().lower()
    return {"key": "faithfulness", "score": 1.0 if "yes" in verdict else 0.0}
```

### 5.5 Comparing experiments

```python
# Run two different chain configurations
def target_gpt4o(inputs: dict) -> dict:
    model = ChatOpenAI(model="gpt-4o")
    chain = prompt | model | StrOutputParser()
    return {"answer": chain.invoke({"question": inputs["question"]})}

def target_gpt4o_mini(inputs: dict) -> dict:
    model = ChatOpenAI(model="gpt-4o-mini")
    chain = prompt | model | StrOutputParser()
    return {"answer": chain.invoke({"question": inputs["question"]})}

evaluators = [exact_match_evaluator, length_evaluator]

results_gpt4o = evaluate(
    target_gpt4o,
    data="qa-golden-set",
    evaluators=evaluators,
    experiment_prefix="gpt4o-comparison",
)

results_mini = evaluate(
    target_gpt4o_mini,
    data="qa-golden-set",
    evaluators=evaluators,
    experiment_prefix="gpt4o-mini-comparison",
)

# Compare in LangSmith UI: go to Datasets → your dataset → Experiments tab
# Or compare programmatically:
gpt4o_scores = results_gpt4o.to_pandas()["feedback.exact_match"].mean()
mini_scores  = results_mini.to_pandas()["feedback.exact_match"].mean()
print(f"GPT-4o: {gpt4o_scores:.2f}")
print(f"GPT-4o-mini: {mini_scores:.2f}")
```

### 5.6 Async evaluation

```python
from langsmith.evaluation import aevaluate

async def async_target(inputs: dict) -> dict:
    answer = await chain.ainvoke({"question": inputs["question"]})
    return {"answer": answer}

results = await aevaluate(
    async_target,
    data="qa-golden-set",
    evaluators=[exact_match_evaluator],
    max_concurrency=10,
)
```

---

## 6. Prompt Management

### 6.1 Push a prompt to LangSmith Hub

```python
from langchain_core.prompts import ChatPromptTemplate
from langsmith import Client

client = Client()

# Define your prompt
qa_prompt = ChatPromptTemplate.from_messages([
    ("system", "You are a helpful assistant. Answer concisely and accurately."),
    ("human", "{question}"),
])

# Push to hub — creates a versioned prompt
client.push_prompt(
    "my-org/qa-assistant",
    object=qa_prompt,
    description="Standard Q&A prompt for the assistant",
    tags=["production", "v2"],
)

print("Prompt pushed to: https://smith.langchain.com/hub/my-org/qa-assistant")
```

### 6.2 Pull a prompt from Hub

```python
from langsmith import Client
from langchain import hub

# Pull latest version
prompt = hub.pull("my-org/qa-assistant")

# Pull a specific commit (for reproducibility)
prompt = hub.pull("my-org/qa-assistant:abc123def")

# Pull with authenticated client
prompt = hub.pull("my-org/qa-assistant", api_key="ls__...")

# Use it in a chain
chain = prompt | model | StrOutputParser()
```

### 6.3 Prompt versioning workflow

```python
# Version your prompts for reproducible experiments
versions = {
    "v1": "abc111",
    "v2": "def222",
    "v3_latest": None,  # None = latest
}

def run_experiment_with_prompt_version(version_hash: str | None, dataset_name: str):
    if version_hash:
        prompt = hub.pull(f"my-org/qa-assistant:{version_hash}")
    else:
        prompt = hub.pull("my-org/qa-assistant")

    chain = prompt | model | StrOutputParser()
    target = lambda inputs: {"answer": chain.invoke({"question": inputs["question"]})}

    return evaluate(
        target,
        data=dataset_name,
        evaluators=[exact_match_evaluator],
        experiment_prefix=f"prompt-{version_hash or 'latest'}",
    )
```

### 6.4 Managing prompt variants

```python
# A/B test two prompt variants
prompt_a = ChatPromptTemplate.from_messages([
    ("system", "Answer concisely."),
    ("human", "{question}"),
])

prompt_b = ChatPromptTemplate.from_messages([
    ("system", "You are an expert assistant. Think step-by-step before answering."),
    ("human", "{question}"),
])

client.push_prompt("my-org/qa-assistant-a", object=prompt_a, tags=["experiment", "concise"])
client.push_prompt("my-org/qa-assistant-b", object=prompt_b, tags=["experiment", "cot"])
```

---

## 7. Monitoring in Production

### 7.1 Production tracing best practices

```python
import os

# Set these in your production environment
os.environ["LANGCHAIN_TRACING_V2"] = "true"
os.environ["LANGCHAIN_PROJECT"] = "production-v2"

# Tag runs with deployment metadata
def get_run_config(user_id: str, session_id: str) -> dict:
    return {
        "tags": ["production", f"version-{os.environ.get('APP_VERSION', 'unknown')}"],
        "metadata": {
            "user_id": user_id,
            "session_id": session_id,
            "region": os.environ.get("AWS_REGION", "us-east-1"),
            "build": os.environ.get("GIT_SHA", "unknown"),
        },
    }

# Use in every call
result = chain.invoke(
    {"question": question},
    config=get_run_config(user_id="u123", session_id="s456"),
)
```

### 7.2 Sampling — trace a percentage of traffic

```python
import random

def should_trace(sample_rate: float = 0.1) -> bool:
    """Only trace sample_rate fraction of requests."""
    return random.random() < sample_rate

def invoke_with_sampling(inputs: dict, sample_rate: float = 0.1) -> str:
    if should_trace(sample_rate):
        # Full tracing enabled
        return chain.invoke(inputs, config={"run_name": "sampled-run"})
    else:
        # Disable tracing for this call
        with tracing_v2_enabled(project_name="production", enabled=False):
            return chain.invoke(inputs)
```

### 7.3 Custom dashboards via the API

```python
from datetime import datetime, timedelta, timezone

client = Client()

# Query runs for the last 24 hours
end_time   = datetime.now(timezone.utc)
start_time = end_time - timedelta(hours=24)

runs = list(client.list_runs(
    project_name="production-v2",
    start_time=start_time,
    end_time=end_time,
    run_type="llm",       # filter to LLM calls only
    limit=1000,
))

# Compute metrics
latencies   = [r.end_time - r.start_time for r in runs if r.end_time and r.start_time]
avg_latency = sum(l.total_seconds() for l in latencies) / len(latencies)

errors  = [r for r in runs if r.error is not None]
error_rate = len(errors) / len(runs) if runs else 0

total_tokens = sum(
    (r.total_tokens or 0) for r in runs
)

print(f"Runs (24h):     {len(runs)}")
print(f"Avg latency:    {avg_latency:.2f}s")
print(f"Error rate:     {error_rate:.1%}")
print(f"Total tokens:   {total_tokens:,}")
```

### 7.4 Alerts and anomaly detection

```python
import smtplib
from email.mime.text import MIMEText

def check_production_health(project_name: str, window_minutes: int = 60):
    end   = datetime.now(timezone.utc)
    start = end - timedelta(minutes=window_minutes)

    runs = list(client.list_runs(
        project_name=project_name,
        start_time=start,
        end_time=end,
    ))

    if not runs:
        return

    errors = [r for r in runs if r.error]
    error_rate = len(errors) / len(runs)

    latencies = [
        (r.end_time - r.start_time).total_seconds()
        for r in runs if r.end_time and r.start_time
    ]
    avg_latency = sum(latencies) / len(latencies) if latencies else 0

    alerts = []
    if error_rate > 0.05:    # > 5% error rate
        alerts.append(f"High error rate: {error_rate:.1%} ({len(errors)}/{len(runs)} runs)")
    if avg_latency > 10:     # > 10s average latency
        alerts.append(f"High latency: {avg_latency:.1f}s average")

    if alerts:
        print(f"🚨 ALERT for {project_name}:")
        for alert in alerts:
            print(f"  - {alert}")
        # send_alert_email(alerts)  # hook up to your alerting system

# Run on a schedule (cron / Celery beat / etc.)
check_production_health("production-v2")
```

### 7.5 Cost tracking

```python
# Token costs per 1M tokens (update as pricing changes)
COSTS = {
    "gpt-4o":        {"input": 2.50,  "output": 10.00},
    "gpt-4o-mini":   {"input": 0.15,  "output": 0.60},
    "gpt-3.5-turbo": {"input": 0.50,  "output": 1.50},
}

def calculate_cost(runs: list) -> float:
    total_cost = 0.0
    for run in runs:
        model = run.extra.get("invocation_params", {}).get("model_name", "")
        if model in COSTS and run.prompt_tokens and run.completion_tokens:
            cost = (
                run.prompt_tokens     / 1_000_000 * COSTS[model]["input"] +
                run.completion_tokens / 1_000_000 * COSTS[model]["output"]
            )
            total_cost += cost
    return total_cost

runs = list(client.list_runs(project_name="production-v2", limit=10_000))
daily_cost = calculate_cost(runs)
print(f"Estimated cost (last 10k runs): ${daily_cost:.4f}")
```

---

## 8. Feedback & Human Review

### 8.1 Collect user feedback

```python
from langsmith import Client
from langchain_core.runnables import RunnableConfig
from langchain_core.tracers.langchain import wait_for_all_tracers

client = Client()

@traceable(name="chatbot-response")
def get_response(question: str, config: RunnableConfig | None = None) -> tuple[str, str]:
    """Returns (answer, run_id) so caller can attach feedback."""
    run_tree = get_current_run_tree()
    answer = chain.invoke({"question": question})
    run_id = str(run_tree.id) if run_tree else None
    return answer, run_id

# In your API endpoint:
answer, run_id = get_response("What is machine learning?")
wait_for_all_tracers()  # ensure run is persisted before attaching feedback

# When user gives a thumbs up/down:
def record_thumbs_feedback(run_id: str, thumbs_up: bool, comment: str = ""):
    client.create_feedback(
        run_id=run_id,
        key="user_feedback",
        score=1.0 if thumbs_up else 0.0,
        value="thumbs_up" if thumbs_up else "thumbs_down",
        comment=comment,
    )

record_thumbs_feedback(run_id, thumbs_up=True, comment="Very helpful!")
```

### 8.2 Annotation queues

```python
# Create an annotation queue for human review
queue = client.create_annotation_queue(
    name="low-confidence-responses",
    description="Responses where the model expressed uncertainty",
)

# Add runs to the queue
def check_and_queue_for_review(run_id: str, answer: str):
    uncertainty_phrases = ["I'm not sure", "I don't know", "I cannot", "I'm uncertain"]
    needs_review = any(phrase.lower() in answer.lower() for phrase in uncertainty_phrases)

    if needs_review:
        client.add_runs_to_annotation_queue(
            queue_id=queue.id,
            run_ids=[run_id],
        )
        print(f"Run {run_id} queued for human review")

# Human reviewers access the queue in the LangSmith UI
# and can label each run as correct/incorrect/needs-improvement
```

### 8.3 Structured feedback schemas

```python
# Define what feedback you want to collect
feedback_configs = [
    {
        "key": "factual_accuracy",
        "min": 1, "max": 5,
        "label": "Factual accuracy (1-5)",
    },
    {
        "key": "tone",
        "options": ["too formal", "appropriate", "too casual"],
        "label": "Tone",
    },
    {
        "key": "is_hallucination",
        "options": [True, False],
        "label": "Contains hallucination?",
    },
]

def submit_structured_feedback(run_id: str, feedback: dict):
    for key, value in feedback.items():
        score = value if isinstance(value, (int, float)) else None
        str_value = str(value) if not isinstance(value, (int, float)) else None
        client.create_feedback(
            run_id=run_id,
            key=key,
            score=score,
            value=str_value,
        )

submit_structured_feedback(run_id, {
    "factual_accuracy": 4,
    "tone": "appropriate",
    "is_hallucination": False,
})
```

---

## 9. CI/CD Integration

### 9.1 Evaluation in GitHub Actions

```yaml
# .github/workflows/eval.yml
name: LLM Evaluation

on:
  pull_request:
    branches: [main]
  push:
    branches: [main]

jobs:
  evaluate:
    runs-on: ubuntu-latest
    steps:
      - uses: actions/checkout@v3
      - uses: actions/setup-python@v4
        with:
          python-version: "3.11"
      - name: Install dependencies
        run: pip install -r requirements.txt
      - name: Run evaluation
        env:
          LANGCHAIN_API_KEY: ${{ secrets.LANGCHAIN_API_KEY }}
          OPENAI_API_KEY: ${{ secrets.OPENAI_API_KEY }}
          LANGCHAIN_TRACING_V2: "true"
          LANGCHAIN_PROJECT: "ci-eval-${{ github.sha }}"
        run: python scripts/run_evals.py --fail-threshold 0.8
```

### 9.2 Evaluation script with pass/fail threshold

```python
# scripts/run_evals.py
import argparse
import sys
from langsmith.evaluation import evaluate

def run_ci_evaluation(fail_threshold: float = 0.8):
    results = evaluate(
        target,
        data="qa-golden-set",
        evaluators=[exact_match_evaluator, length_evaluator],
        experiment_prefix=f"ci-{os.environ.get('GITHUB_SHA', 'local')[:8]}",
        max_concurrency=5,
    )

    df = results.to_pandas()

    # Compute scores
    exact_match_score = df["feedback.exact_match"].mean()
    length_score      = df["feedback.response_length"].mean()
    overall_score     = (exact_match_score + length_score) / 2

    print(f"Exact match:  {exact_match_score:.2%}")
    print(f"Length score: {length_score:.2%}")
    print(f"Overall:      {overall_score:.2%}")
    print(f"Threshold:    {fail_threshold:.2%}")

    if overall_score < fail_threshold:
        print(f"❌ FAIL — score {overall_score:.2%} is below threshold {fail_threshold:.2%}")
        sys.exit(1)
    else:
        print(f"✅ PASS — score {overall_score:.2%} meets threshold {fail_threshold:.2%}")
        sys.exit(0)

if __name__ == "__main__":
    parser = argparse.ArgumentParser()
    parser.add_argument("--fail-threshold", type=float, default=0.8)
    args = parser.parse_args()
    run_ci_evaluation(args.fail_threshold)
```

### 9.3 Regression testing

```python
def regression_test(current_experiment: str, baseline_experiment: str, metric_key: str) -> bool:
    """Check that the current model isn't worse than the baseline on key metrics."""
    current_runs  = list(client.list_runs(project_name=current_experiment))
    baseline_runs = list(client.list_runs(project_name=baseline_experiment))

    def get_avg_score(runs, key):
        scores = []
        for run in runs:
            feedback = client.list_feedback(run_ids=[str(run.id)], feedback_key=key)
            scores.extend(f.score for f in feedback if f.score is not None)
        return sum(scores) / len(scores) if scores else 0

    current_score  = get_avg_score(current_runs, metric_key)
    baseline_score = get_avg_score(baseline_runs, metric_key)

    regression = current_score < baseline_score * 0.95  # allow 5% regression
    print(f"Current: {current_score:.2f}, Baseline: {baseline_score:.2f}, Regression: {regression}")
    return not regression
```

---

## 10. Advanced Patterns

### 10.1 Online evaluation (evaluate in production)

```python
from langsmith import traceable, Client
from langsmith.run_helpers import get_current_run_tree

client = Client()

@traceable(name="production-answer")
async def answer_with_online_eval(question: str, reference: str | None = None) -> str:
    answer = await chain.ainvoke({"question": question})
    run_tree = get_current_run_tree()

    if run_tree and reference:
        # Evaluate immediately and attach feedback to the trace
        eval_result = qa_eval.evaluate_strings(
            input=question,
            prediction=answer,
            reference=reference,
        )
        await asyncio.to_thread(
            client.create_feedback,
            run_id=run_tree.id,
            key="online_correctness",
            score=eval_result["score"],
        )

    return answer
```

### 10.2 Multi-turn conversation evaluation

```python
def evaluate_conversation(conversation: list[dict], evaluator_llm) -> dict:
    """Evaluate an entire multi-turn conversation."""
    conversation_text = "\n".join(
        f"{turn['role'].upper()}: {turn['content']}"
        for turn in conversation
    )

    coherence_prompt = f"""Rate the coherence of this conversation from 0-10.
Does the assistant maintain context across turns?
Does the conversation flow naturally?

Conversation:
{conversation_text}

Output ONLY a number."""

    score_str = evaluator_llm.invoke([HumanMessage(content=coherence_prompt)]).content
    coherence = float(score_str.strip()) / 10

    return {
        "coherence": coherence,
        "turn_count": len([t for t in conversation if t["role"] == "user"]),
    }
```

### 10.3 Tracing LangGraph with LangSmith

```python
# LangGraph traces automatically when LANGCHAIN_TRACING_V2=true
# Each node appears as a child run in the trace

# Add node-level metadata
def my_node(state: AgentState) -> dict:
    response = model.invoke(state["messages"])

    # Tag the specific model call within this node
    return {
        "messages": [response],
        "__run_metadata": {                 # LangGraph-specific metadata key
            "node_name": "my_node",
            "custom_metric": 42,
        },
    }

# Per-graph trace configuration
result = graph.invoke(
    initial_state,
    config={
        "run_name": "multi-agent-workflow",
        "tags": ["production", "v3"],
        "metadata": {"workflow_id": "wf-123"},
    },
)
```

### 10.4 Custom run metadata for debugging

```python
from langsmith import RunTree

def debug_chain_run(question: str, debug: bool = False) -> str:
    """Run chain with rich debugging metadata captured in LangSmith."""
    run = RunTree(
        name="debug-chain",
        run_type="chain",
        inputs={"question": question},
        extra={"metadata": {"debug_mode": debug}},
    )

    try:
        # Pre-processing
        preprocessed = question.strip().lower()
        run.add_metadata({"preprocessed_length": len(preprocessed)})

        # Main chain call
        answer = chain.invoke({"question": preprocessed})

        # Post-processing metrics
        run.add_metadata({
            "answer_word_count": len(answer.split()),
            "answer_sentence_count": answer.count("."),
        })

        run.end(outputs={"answer": answer})
        run.post()
        return answer

    except Exception as e:
        run.end(error=str(e))
        run.post()
        raise
```

### 10.5 Bulk export and analysis

```python
import pandas as pd

def export_runs_to_dataframe(
    project_name: str,
    start_time: datetime,
    end_time: datetime,
    include_feedback: bool = True,
) -> pd.DataFrame:
    runs = list(client.list_runs(
        project_name=project_name,
        start_time=start_time,
        end_time=end_time,
        run_type="chain",
    ))

    records = []
    for run in runs:
        record = {
            "run_id":    str(run.id),
            "name":      run.name,
            "start":     run.start_time,
            "latency_s": (run.end_time - run.start_time).total_seconds() if run.end_time else None,
            "tokens":    run.total_tokens,
            "error":     run.error,
            "input":     str(run.inputs),
            "output":    str(run.outputs),
        }

        if include_feedback:
            feedback = list(client.list_feedback(run_ids=[str(run.id)]))
            for f in feedback:
                record[f"feedback_{f.key}"] = f.score

        records.append(record)

    df = pd.DataFrame(records)
    df["start"] = pd.to_datetime(df["start"], utc=True)
    return df

# Export last week's runs
df = export_runs_to_dataframe(
    "production-v2",
    start_time=datetime.now(timezone.utc) - timedelta(days=7),
    end_time=datetime.now(timezone.utc),
)

print(df.describe())
df.to_csv("weekly_run_export.csv", index=False)
```

### 10.6 Prompt optimisation loop

```python
async def optimise_prompt(
    dataset_name: str,
    base_prompt: ChatPromptTemplate,
    optimiser_llm,
    iterations: int = 3,
) -> ChatPromptTemplate:
    """Iteratively improve a prompt based on evaluation results."""
    current_prompt = base_prompt
    best_score = 0.0

    for i in range(iterations):
        # Evaluate current prompt
        chain = current_prompt | model | StrOutputParser()
        target = lambda inputs: {"answer": chain.invoke({"question": inputs["question"]})}
        results = await aevaluate(
            target,
            data=dataset_name,
            evaluators=[exact_match_evaluator],
            experiment_prefix=f"optimise-iter-{i}",
        )

        df = results.to_pandas()
        score = df["feedback.exact_match"].mean()
        print(f"Iteration {i}: score = {score:.2f}")

        if score > best_score:
            best_score = score
            best_prompt = current_prompt

        if score >= 0.95:
            print("Target score reached. Stopping.")
            break

        # Ask LLM to improve the prompt based on failures
        failures = df[df["feedback.exact_match"] == 0]
        failure_examples = "\n".join(
            f"Q: {row['inputs.question']}\nA: {row['outputs.answer']}"
            for _, row in failures.head(5).iterrows()
        )

        improvement_request = f"""The current system prompt is:
{current_prompt.messages[0].prompt.template}

It failed on these examples:
{failure_examples}

Suggest an improved system prompt that would handle these cases better.
Reply with ONLY the new system prompt text."""

        new_system = optimiser_llm.invoke([HumanMessage(content=improvement_request)]).content
        current_prompt = ChatPromptTemplate.from_messages([
            ("system", new_system),
            ("human", "{question}"),
        ])

    return best_prompt
```

---

*You now have the full triad: build with **LangChain** (`langchain_python.md`), orchestrate with **LangGraph** (`langgraph_python.md`), and observe and improve with **LangSmith** (this file).*
