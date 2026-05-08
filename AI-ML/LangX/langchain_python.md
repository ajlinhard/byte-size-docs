# LangChain Python — Beginner to Advanced

> **Prerequisites:** Python 3.9+, an OpenAI API key (or any supported provider).  
> **Install:** `pip install langchain langchain-openai langchain-community python-dotenv pydantic`

---

## Table of Contents

1. [Core Concepts](#1-core-concepts)
2. [Your First Chain](#2-your-first-chain)
3. [Prompt Templates](#3-prompt-templates)
4. [Output Parsers](#4-output-parsers)
5. [Context & Memory Management](#5-context--memory-management)
6. [Retrieval-Augmented Generation (RAG)](#6-retrieval-augmented-generation-rag)
7. [Tools & Agents](#7-tools--agents)
8. [Advanced Chain Patterns](#8-advanced-chain-patterns)
9. [Callbacks & Observability](#9-callbacks--observability)
10. [Production Patterns](#10-production-patterns)

---

## 1. Core Concepts

LangChain is built around a few primitives that compose together using the **pipe operator (`|`)** from LangChain Expression Language (LCEL).

```
prompt | model | parser  →  a "chain"
```

| Primitive | What it does |
|---|---|
| `ChatPromptTemplate` | Formats your input into a structured prompt |
| `ChatOpenAI` | Calls the LLM and returns a response object |
| `OutputParser` | Converts the raw response into a usable Python type |
| `Runnable` | Anything that implements `.invoke()`, `.stream()`, `.batch()` |

### Environment setup

```python
# .env file
OPENAI_API_KEY=sk-...

# Python
from dotenv import load_dotenv
load_dotenv()
```

---

## 2. Your First Chain

### 2.1 Minimal example

```python
from langchain_openai import ChatOpenAI
from langchain_core.prompts import ChatPromptTemplate
from langchain_core.output_parsers import StrOutputParser

model = ChatOpenAI(model="gpt-4o-mini")

prompt = ChatPromptTemplate.from_messages([
    ("system", "You are a helpful assistant."),
    ("human", "{question}"),
])

chain = prompt | model | StrOutputParser()

response = chain.invoke({"question": "What is the speed of light?"})
print(response)
# "The speed of light in a vacuum is approximately 299,792,458 metres per second..."
```

### 2.2 Invoking in different ways

```python
# Single call
result = chain.invoke({"question": "What is entropy?"})

# Process a list of inputs concurrently
results = chain.batch([
    {"question": "What is entropy?"},
    {"question": "What is enthalpy?"},
    {"question": "What is free energy?"},
])

# Stream tokens as they arrive
for token in chain.stream({"question": "Explain quantum entanglement."}):
    print(token, end="", flush=True)

# Async (inside an async context)
result = await chain.ainvoke({"question": "What is a quasar?"})
```

### 2.3 Direct model calls (no chain)

```python
from langchain_core.messages import HumanMessage, SystemMessage

messages = [
    SystemMessage(content="You are a pirate."),
    HumanMessage(content="Tell me about the ocean."),
]

response = model.invoke(messages)
print(response.content)        # The text response
print(response.response_metadata)  # Token usage, model name, finish reason
```

---

## 3. Prompt Templates

### 3.1 String templates

```python
from langchain_core.prompts import PromptTemplate

# Simple f-string style template
prompt = PromptTemplate.from_template(
    "Summarise the following text in {num_sentences} sentences:\n\n{text}"
)

result = (prompt | model | StrOutputParser()).invoke({
    "num_sentences": 2,
    "text": "The mitochondria is the powerhouse of the cell..."
})
```

### 3.2 Chat prompt templates

```python
from langchain_core.prompts import ChatPromptTemplate, MessagesPlaceholder

prompt = ChatPromptTemplate.from_messages([
    ("system", "You are an expert in {domain}. Respond in {language}."),
    MessagesPlaceholder(variable_name="history"),   # slot for conversation history
    ("human", "{question}"),
])

# Partially fill in some variables upfront
spanish_prompt = prompt.partial(language="Spanish")

chain = spanish_prompt | model | StrOutputParser()
result = chain.invoke({
    "domain": "astronomy",
    "history": [],
    "question": "What is a neutron star?",
})
```

### 3.3 Few-shot prompts

```python
from langchain_core.prompts import FewShotChatMessagePromptTemplate

examples = [
    {"input": "happy",  "output": "sad"},
    {"input": "tall",   "output": "short"},
    {"input": "fast",   "output": "slow"},
]

example_prompt = ChatPromptTemplate.from_messages([
    ("human",  "{input}"),
    ("ai",     "{output}"),
])

few_shot_prompt = FewShotChatMessagePromptTemplate(
    examples=examples,
    example_prompt=example_prompt,
)

final_prompt = ChatPromptTemplate.from_messages([
    ("system", "Give the antonym of every word."),
    few_shot_prompt,
    ("human", "{word}"),
])

chain = final_prompt | model | StrOutputParser()
print(chain.invoke({"word": "bright"}))  # "dim"
```

### 3.4 Dynamic example selection

```python
from langchain_core.example_selectors import SemanticSimilarityExampleSelector
from langchain_openai import OpenAIEmbeddings
from langchain_community.vectorstores import Chroma

# Select the most relevant examples based on the current input
selector = SemanticSimilarityExampleSelector.from_examples(
    examples,
    OpenAIEmbeddings(),
    Chroma,
    k=2,  # select 2 most similar examples
)

dynamic_prompt = FewShotChatMessagePromptTemplate(
    example_selector=selector,
    example_prompt=example_prompt,
)
```

---

## 4. Output Parsers

### 4.1 String parser

```python
from langchain_core.output_parsers import StrOutputParser

chain = prompt | model | StrOutputParser()
# Returns: str
```

### 4.2 JSON parser

```python
from langchain_core.output_parsers import JsonOutputParser

prompt = ChatPromptTemplate.from_messages([
    ("system", "Respond ONLY with valid JSON. No markdown, no extra text."),
    ("human", "Return data about {animal} with keys: name, diet, habitat, endangered (bool)"),
])

chain = prompt | model | JsonOutputParser()
data = chain.invoke({"animal": "amur leopard"})

print(data["endangered"])  # True
print(type(data))          # dict
```

### 4.3 Pydantic parser (strongly typed)

```python
from pydantic import BaseModel, Field, field_validator
from langchain_core.output_parsers import PydanticOutputParser
from typing import Literal

class ProductReview(BaseModel):
    product_name: str = Field(description="Name of the product")
    rating: int = Field(description="Rating from 1-5", ge=1, le=5)
    sentiment: Literal["positive", "neutral", "negative"]
    pros: list[str] = Field(description="List of positive aspects")
    cons: list[str] = Field(description="List of negative aspects")
    recommend: bool = Field(description="Would you recommend this product?")
    summary: str = Field(description="One sentence summary of the review")

    @field_validator("rating")
    def rating_in_range(cls, v):
        if not 1 <= v <= 5:
            raise ValueError("Rating must be between 1 and 5")
        return v

parser = PydanticOutputParser(pydantic_object=ProductReview)

prompt = ChatPromptTemplate.from_messages([
    ("system", "You are a product review analyser.\n{format_instructions}"),
    ("human", "Analyse this review:\n\n{review}"),
]).partial(format_instructions=parser.get_format_instructions())

chain = prompt | model | parser

result = chain.invoke({"review": "The noise-cancelling headphones are incredible! Battery lasts forever. A bit pricey though and the ear cups get warm."})

print(result.rating)      # 4
print(result.sentiment)   # "positive"
print(result.pros)        # ["excellent noise-cancelling", "long battery life"]
print(type(result))       # <class 'ProductReview'>
```

### 4.4 Structured output via model binding (OpenAI function calling)

```python
# Preferred approach for OpenAI models — uses function calling under the hood
# More reliable than prompt-based parsing

class WeatherReport(BaseModel):
    city: str
    temperature_celsius: float
    conditions: str
    humidity_percent: int
    forecast: list[str] = Field(description="3-day forecast as list of strings")

structured_model = model.with_structured_output(WeatherReport)

prompt = ChatPromptTemplate.from_messages([
    ("human", "Give me a realistic mock weather report for {city}"),
])

chain = prompt | structured_model
report = chain.invoke({"city": "Tokyo"})

print(report.city)               # "Tokyo"
print(report.temperature_celsius)  # 22.5
print(type(report))              # <class 'WeatherReport'>
```

### 4.5 List parser

```python
from langchain.output_parsers import CommaSeparatedListOutputParser

parser = CommaSeparatedListOutputParser()

prompt = ChatPromptTemplate.from_messages([
    ("system", parser.get_format_instructions()),
    ("human", "List 5 {topic}"),
])

chain = prompt | model | parser
items = chain.invoke({"topic": "Python web frameworks"})
print(items)  # ['Django', 'FastAPI', 'Flask', 'Tornado', 'Sanic']
```

---

## 5. Context & Memory Management

### 5.1 Manual message history

```python
from langchain_core.messages import HumanMessage, AIMessage, SystemMessage

model = ChatOpenAI(model="gpt-4o-mini")

history = [SystemMessage(content="You are a knowledgeable chef.")]

def chat(user_input: str) -> str:
    history.append(HumanMessage(content=user_input))
    response = model.invoke(history)
    history.append(response)
    return response.content

print(chat("What cuisine should I make for a dinner party?"))
print(chat("Can you suggest a starter for that?"))   # Knows the cuisine from turn 1
print(chat("How long will it take to prepare?"))     # Knows the starter from turn 2
```

### 5.2 RunnableWithMessageHistory (recommended)

```python
from langchain_core.runnables.history import RunnableWithMessageHistory
from langchain_community.chat_message_histories import ChatMessageHistory
from langchain_core.prompts import MessagesPlaceholder

# In-memory store — swap for Redis/DynamoDB in production
store: dict[str, ChatMessageHistory] = {}

def get_session_history(session_id: str) -> ChatMessageHistory:
    if session_id not in store:
        store[session_id] = ChatMessageHistory()
    return store[session_id]

prompt = ChatPromptTemplate.from_messages([
    ("system", "You are a helpful assistant. Be concise."),
    MessagesPlaceholder(variable_name="history"),
    ("human", "{input}"),
])

chain = prompt | model | StrOutputParser()

chain_with_history = RunnableWithMessageHistory(
    chain,
    get_session_history,
    input_messages_key="input",
    history_messages_key="history",
)

# session_id isolates each user's conversation
config_alice = {"configurable": {"session_id": "alice-001"}}
config_bob   = {"configurable": {"session_id": "bob-001"}}

# Alice's conversation
chain_with_history.invoke({"input": "My name is Alice and I love jazz."}, config=config_alice)
reply = chain_with_history.invoke({"input": "What's my name and what do I love?"}, config=config_alice)
print(reply)  # "Your name is Alice and you love jazz."

# Bob starts fresh — no knowledge of Alice
reply = chain_with_history.invoke({"input": "What's my name?"}, config=config_bob)
print(reply)  # "I don't know your name..."
```

### 5.3 Persistent history with Redis

```python
# pip install redis langchain-community
from langchain_community.chat_message_histories import RedisChatMessageHistory

def get_redis_history(session_id: str) -> RedisChatMessageHistory:
    return RedisChatMessageHistory(
        session_id=session_id,
        url="redis://localhost:6379",
        ttl=3600,  # expire after 1 hour
    )

chain_with_history = RunnableWithMessageHistory(
    chain,
    get_redis_history,
    input_messages_key="input",
    history_messages_key="history",
)
```

### 5.4 Trimming long histories

```python
from langchain_core.messages import trim_messages
from langchain_core.runnables import RunnablePassthrough
import operator

trimmer = trim_messages(
    max_tokens=2000,
    strategy="last",         # keep the most recent messages
    token_counter=model,     # uses the model's tokeniser
    include_system=True,     # never drop the system prompt
    allow_partial=False,     # don't cut a message mid-sentence
    start_on="human",        # always start with a user message
)

# Inject trimmer into the chain before the prompt
chain_with_trimming = (
    RunnablePassthrough.assign(history=lambda x: trimmer.invoke(x["history"]))
    | prompt
    | model
    | StrOutputParser()
)
```

### 5.5 Summarising old messages

```python
from langchain_core.messages import HumanMessage, AIMessage, SystemMessage

async def summarise_and_compress(history: list, model, threshold: int = 10) -> list:
    """Summarise old messages when history grows past threshold."""
    if len(history) <= threshold:
        return history

    # Keep system message + last 4 messages
    system = [m for m in history if isinstance(m, SystemMessage)]
    recent = history[-4:]
    to_summarise = history[len(system):-4]

    summary_prompt = f"Summarise this conversation in 3-4 sentences:\n\n"
    for m in to_summarise:
        role = "User" if isinstance(m, HumanMessage) else "Assistant"
        summary_prompt += f"{role}: {m.content}\n"

    summary = await model.ainvoke([HumanMessage(content=summary_prompt)])

    return system + [AIMessage(content=f"[Summary of earlier conversation: {summary.content}]")] + recent
```

### 5.6 Multi-turn context with structured data

```python
from langchain_core.messages import HumanMessage, AIMessage

# Maintain structured context alongside the conversation
class ConversationContext(BaseModel):
    user_name: str | None = None
    preferences: list[str] = []
    session_goal: str | None = None

context = ConversationContext()

def update_context(user_message: str, ai_response: str):
    """Extract and update structured context from conversation turns."""
    # You could use a separate extraction chain here
    if "my name is" in user_message.lower():
        name = user_message.lower().split("my name is")[-1].strip().split()[0]
        context.user_name = name.capitalize()

system_prompt = lambda: f"""You are a helpful assistant.
User name: {context.user_name or 'Unknown'}
Known preferences: {', '.join(context.preferences) or 'None'}
Session goal: {context.session_goal or 'General assistance'}
"""
```

---

## 6. Retrieval-Augmented Generation (RAG)

### 6.1 Basic RAG pipeline

```python
# pip install langchain-chroma pypdf
from langchain_community.document_loaders import PyPDFLoader, WebBaseLoader
from langchain_text_splitters import RecursiveCharacterTextSplitter
from langchain_openai import OpenAIEmbeddings
from langchain_chroma import Chroma
from langchain_core.runnables import RunnablePassthrough

# Step 1: Load documents
loader = WebBaseLoader("https://docs.python.org/3/tutorial/")
docs = loader.load()

# Step 2: Split into chunks
splitter = RecursiveCharacterTextSplitter(
    chunk_size=1000,
    chunk_overlap=200,   # overlap prevents context loss at boundaries
)
chunks = splitter.split_documents(docs)

# Step 3: Embed and store
embeddings = OpenAIEmbeddings(model="text-embedding-3-small")
vectorstore = Chroma.from_documents(chunks, embeddings)
retriever = vectorstore.as_retriever(search_kwargs={"k": 4})

# Step 4: Build RAG chain
rag_prompt = ChatPromptTemplate.from_messages([
    ("system", """Answer the question using ONLY the context below.
If the answer is not in the context, say "I don't have that information."

Context:
{context}"""),
    ("human", "{question}"),
])

def format_docs(docs):
    return "\n\n".join(doc.page_content for doc in docs)

rag_chain = (
    {"context": retriever | format_docs, "question": RunnablePassthrough()}
    | rag_prompt
    | model
    | StrOutputParser()
)

answer = rag_chain.invoke("How do list comprehensions work?")
```

### 6.2 RAG with source citations

```python
from langchain_core.runnables import RunnableParallel

# Return both the answer and the source documents
rag_chain_with_sources = RunnableParallel(
    answer=rag_chain,
    sources=retriever,
)

result = rag_chain_with_sources.invoke("What are Python generators?")
print(result["answer"])
for doc in result["sources"]:
    print(f"  - {doc.metadata.get('source', 'unknown')} p.{doc.metadata.get('page', '?')}")
```

### 6.3 Advanced retrieval strategies

```python
from langchain.retrievers import ContextualCompressionRetriever
from langchain.retrievers.document_compressors import LLMChainExtractor
from langchain.retrievers import MultiQueryRetriever

# Compression: extract only the relevant parts of each retrieved chunk
compressor = LLMChainExtractor.from_llm(model)
compression_retriever = ContextualCompressionRetriever(
    base_compressor=compressor,
    base_retriever=retriever,
)

# Multi-query: generate multiple reformulations to improve recall
multi_query_retriever = MultiQueryRetriever.from_llm(
    retriever=retriever,
    llm=model,
)

# Ensemble: combine results from multiple retrievers
from langchain.retrievers import EnsembleRetriever
from langchain_community.retrievers import BM25Retriever

bm25_retriever = BM25Retriever.from_documents(chunks)
bm25_retriever.k = 4

ensemble_retriever = EnsembleRetriever(
    retrievers=[bm25_retriever, retriever],
    weights=[0.4, 0.6],     # weight semantic search higher
)
```

### 6.4 Conversational RAG

```python
from langchain.chains import create_history_aware_retriever, create_retrieval_chain
from langchain.chains.combine_documents import create_stuff_documents_chain

# Step 1: Rephrase the user's question using conversation history
contextualise_prompt = ChatPromptTemplate.from_messages([
    ("system", """Given a chat history and the latest user question which might 
reference context in the chat history, formulate a standalone question which 
can be understood without the chat history. Do NOT answer — just reformulate 
the question if needed, otherwise return it as-is."""),
    MessagesPlaceholder("history"),
    ("human", "{input}"),
])

history_aware_retriever = create_history_aware_retriever(
    model, retriever, contextualise_prompt
)

# Step 2: Answer using retrieved docs
qa_prompt = ChatPromptTemplate.from_messages([
    ("system", "Answer using the following context:\n\n{context}"),
    MessagesPlaceholder("history"),
    ("human", "{input}"),
])

question_answer_chain = create_stuff_documents_chain(model, qa_prompt)
rag_chain = create_retrieval_chain(history_aware_retriever, question_answer_chain)

# Use with message history
conversational_rag = RunnableWithMessageHistory(
    rag_chain,
    get_session_history,
    input_messages_key="input",
    history_messages_key="history",
    output_messages_key="answer",
)
```

---

## 7. Tools & Agents

### 7.1 Built-in tools

```python
from langchain_community.tools import DuckDuckGoSearchRun, WikipediaQueryRun
from langchain_community.utilities import WikipediaAPIWrapper

search = DuckDuckGoSearchRun()
wiki = WikipediaQueryRun(api_wrapper=WikipediaAPIWrapper())

print(search.invoke("latest Python release"))
print(wiki.invoke("Alan Turing"))
```

### 7.2 Custom tools with @tool decorator

```python
from langchain_core.tools import tool
from typing import Annotated
import math

@tool
def calculate_compound_interest(
    principal: Annotated[float, "Initial investment amount in dollars"],
    rate: Annotated[float, "Annual interest rate as a decimal (e.g. 0.05 for 5%)"],
    years: Annotated[int, "Number of years to invest"],
    compounds_per_year: Annotated[int, "How many times per year interest compounds"] = 12,
) -> dict:
    """Calculate compound interest for an investment."""
    amount = principal * (1 + rate / compounds_per_year) ** (compounds_per_year * years)
    return {
        "final_amount": round(amount, 2),
        "interest_earned": round(amount - principal, 2),
        "total_return_pct": round((amount - principal) / principal * 100, 2),
    }

@tool
def get_stock_price(ticker: str) -> str:
    """Get the current stock price for a given ticker symbol (mock implementation)."""
    mock_prices = {"AAPL": 182.50, "GOOG": 141.80, "MSFT": 378.90}
    price = mock_prices.get(ticker.upper(), "Unknown ticker")
    return f"{ticker.upper()}: ${price}"
```

### 7.3 ReAct agent

```python
from langchain.agents import create_react_agent, AgentExecutor
from langchain import hub

tools = [calculate_compound_interest, get_stock_price]

# Pull a ReAct prompt from LangChain Hub
react_prompt = hub.pull("hwchase17/react")

agent = create_react_agent(model, tools, react_prompt)

agent_executor = AgentExecutor(
    agent=agent,
    tools=tools,
    verbose=True,        # prints thought/action/observation loop
    max_iterations=5,    # prevent infinite loops
    handle_parsing_errors=True,
)

result = agent_executor.invoke({
    "input": "If I invest $10,000 at 7% annual interest compounded monthly for 20 years, what will I have?"
})
print(result["output"])
```

### 7.4 OpenAI tools agent (more reliable than ReAct)

```python
from langchain.agents import create_openai_tools_agent

# Uses OpenAI's function calling — more structured and reliable than ReAct text parsing
agent = create_openai_tools_agent(model, tools, prompt)

agent_executor = AgentExecutor(
    agent=agent,
    tools=tools,
    verbose=True,
    return_intermediate_steps=True,  # see each tool call and result
)

result = agent_executor.invoke({"input": "Compare AAPL and MSFT stock prices"})

# Inspect intermediate steps
for action, observation in result["intermediate_steps"]:
    print(f"Tool: {action.tool}, Input: {action.tool_input}")
    print(f"Result: {observation}\n")
```

### 7.5 Structured tool output

```python
from langchain_core.tools import StructuredTool

class WeatherInput(BaseModel):
    city: str = Field(description="City name")
    units: Literal["celsius", "fahrenheit"] = Field(default="celsius")

def get_weather(city: str, units: str = "celsius") -> dict:
    """Fetch current weather for a city (mock)."""
    return {"city": city, "temp": 22, "units": units, "conditions": "sunny"}

weather_tool = StructuredTool.from_function(
    func=get_weather,
    name="get_weather",
    description="Get current weather for a city",
    args_schema=WeatherInput,
    return_direct=False,   # True = skip LLM response, return tool output directly
)
```

---

## 8. Advanced Chain Patterns

### 8.1 Branching with RunnableBranch

```python
from langchain_core.runnables import RunnableBranch, RunnableLambda

# Route to different chains based on the input
code_chain  = (ChatPromptTemplate.from_template("Answer this coding question: {question}") | model | StrOutputParser())
math_chain  = (ChatPromptTemplate.from_template("Solve this maths problem step by step: {question}") | model | StrOutputParser())
general_chain = (ChatPromptTemplate.from_template("Answer this general question: {question}") | model | StrOutputParser())

def classify(x: dict) -> str:
    q = x["question"].lower()
    if any(w in q for w in ["code", "python", "function", "class", "error", "bug"]):
        return "code"
    elif any(w in q for w in ["calculate", "solve", "equation", "integral", "derivative"]):
        return "math"
    return "general"

router = RunnableBranch(
    (lambda x: classify(x) == "code",  code_chain),
    (lambda x: classify(x) == "math",  math_chain),
    general_chain,  # default
)

print(router.invoke({"question": "Write a Python function to reverse a string"}))
print(router.invoke({"question": "Solve x^2 - 5x + 6 = 0"}))
```

### 8.2 Parallel execution

```python
from langchain_core.runnables import RunnableParallel

# Run two chains simultaneously, merge results
summarise = (
    ChatPromptTemplate.from_template("Summarise this in one sentence: {text}") | model | StrOutputParser()
)
sentiment = (
    ChatPromptTemplate.from_template("What is the sentiment of this text (positive/negative/neutral)? {text}") | model | StrOutputParser()
)
keywords = (
    ChatPromptTemplate.from_template("Extract 5 keywords from this text as a comma-separated list: {text}") | model | StrOutputParser()
)

analyse = RunnableParallel(
    summary=summarise,
    sentiment=sentiment,
    keywords=keywords,
)

results = analyse.invoke({"text": "The new product launch was a massive success. Sales exceeded all expectations and customer feedback has been overwhelmingly positive."})

print(results["summary"])   # One sentence summary
print(results["sentiment"]) # "positive"
print(results["keywords"])  # "product launch, sales, success..."
```

### 8.3 Fallback chains

```python
from langchain_openai import ChatOpenAI

gpt4o     = ChatOpenAI(model="gpt-4o",     temperature=0)
gpt4mini  = ChatOpenAI(model="gpt-4o-mini", temperature=0)

# Try gpt-4o first; fall back to gpt-4o-mini on any error
robust_model = gpt4o.with_fallbacks([gpt4mini])

chain = prompt | robust_model | StrOutputParser()
```

### 8.4 Custom Runnables

```python
from langchain_core.runnables import RunnableLambda
from langchain_core.runnables import chain as runnable_chain

# Wrap any function as a Runnable
def count_words(text: str) -> dict:
    return {"text": text, "word_count": len(text.split())}

word_counter = RunnableLambda(count_words)

# Use @chain decorator for multi-step custom logic with full LCEL support
@runnable_chain
def smart_qa(question: str):
    # Decide approach based on question length
    if len(question.split()) < 5:
        template = "Give a brief answer to: {question}"
    else:
        template = "Give a detailed, structured answer to: {question}"

    prompt_template = ChatPromptTemplate.from_template(template)
    chain = prompt_template | model | StrOutputParser()
    return chain.invoke({"question": question})
```

### 8.5 Retry logic

```python
from langchain_core.runnables import RunnableRetry

# Retry the chain up to 3 times on failure
retrying_chain = chain.with_retry(
    stop_after_attempt=3,
    wait_exponential_jitter=True,
    retry_if_exception_type=(Exception,),
)
```

### 8.6 Rate limiting & concurrency

```python
from langchain_core.rate_limiters import InMemoryRateLimiter

limiter = InMemoryRateLimiter(
    requests_per_second=2,
    check_every_n_seconds=0.1,
    max_bucket_size=10,
)

model_with_limit = ChatOpenAI(
    model="gpt-4o-mini",
    rate_limiter=limiter,
)

# Batch with controlled concurrency
results = chain.batch(
    inputs,
    config={"max_concurrency": 5},  # run at most 5 in parallel
)
```

---

## 9. Callbacks & Observability

### 9.1 Built-in callback handlers

```python
from langchain_core.callbacks import StdOutCallbackHandler
from langchain.callbacks import FileCallbackHandler
from langchain_core.tracers import ConsoleCallbackHandler
import logging

# Log everything to stdout
chain.invoke(
    {"question": "What is a black hole?"},
    config={"callbacks": [StdOutCallbackHandler()]},
)

# Log to a file
handler = FileCallbackHandler("chain_log.txt")
chain.invoke({"question": "..."}, config={"callbacks": [handler]})
```

### 9.2 Custom callback handler

```python
from langchain_core.callbacks.base import BaseCallbackHandler
from langchain_core.outputs import LLMResult
import time

class TimingCallbackHandler(BaseCallbackHandler):
    def __init__(self):
        self.start_time = None
        self.token_count = 0

    def on_llm_start(self, serialized, prompts, **kwargs):
        self.start_time = time.time()
        print(f"LLM started with {len(prompts)} prompt(s)")

    def on_llm_end(self, response: LLMResult, **kwargs):
        elapsed = time.time() - self.start_time
        tokens = response.llm_output.get("token_usage", {})
        print(f"LLM finished in {elapsed:.2f}s | Tokens: {tokens}")

    def on_llm_new_token(self, token: str, **kwargs):
        self.token_count += 1

    def on_chain_error(self, error: Exception, **kwargs):
        print(f"Chain error: {error}")

timing_handler = TimingCallbackHandler()
chain.invoke({"question": "..."}, config={"callbacks": [timing_handler]})
```

---

## 10. Production Patterns

### 10.1 LLM output grading (LLM-as-a-judge)

```python
from langchain.evaluation import load_evaluator

evaluator_llm = ChatOpenAI(model="gpt-4o", temperature=0)

# Criteria evaluator — pass/fail on a named quality
criteria_eval = load_evaluator("criteria", criteria="conciseness", llm=evaluator_llm)
result = criteria_eval.evaluate_strings(
    prediction="The sky is blue due to Rayleigh scattering.",
    input="Why is the sky blue?",
)
print(result["score"])     # 1 = pass
print(result["reasoning"]) # explanation from the judge

# QA evaluator — check correctness against ground truth
qa_eval = load_evaluator("qa", llm=evaluator_llm)
result = qa_eval.evaluate_strings(
    input="What year did WW2 end?",
    prediction="World War 2 ended in 1945.",
    reference="1945",
)
print(result["score"])  # 1 = correct

# Numeric scoring evaluator (1-10)
score_eval = load_evaluator("score_string", criteria="helpfulness", llm=evaluator_llm, normalize_by=10)
result = score_eval.evaluate_strings(
    prediction="Here are 5 ways to approach that problem...",
    input="How do I reverse a list in Python?",
)
print(result["score"])  # 0.0–1.0
```

### 10.2 Custom evaluation rubric

```python
custom_criteria = {
    "uses_examples": "Does the response include at least one concrete code example?",
    "correct_syntax": "Is any code shown syntactically correct Python?",
    "beginner_friendly": "Is the explanation accessible to a Python beginner?",
}

custom_eval = load_evaluator("criteria", criteria=custom_criteria, llm=evaluator_llm)

result = custom_eval.evaluate_strings(
    prediction="You can reverse a list using `my_list.reverse()` or `my_list[::-1]`. For example: nums = [1,2,3]; print(nums[::-1])  # [3,2,1]",
    input="How do I reverse a list in Python?",
)
print(result)
```

### 10.3 Batch evaluation pipeline

```python
test_cases = [
    {"input": "What is a decorator in Python?",        "reference": "A decorator wraps a function to modify its behaviour."},
    {"input": "What is the GIL?",                      "reference": "The GIL is a mutex that allows only one thread to execute Python bytecode at a time."},
    {"input": "What is the difference between list and tuple?", "reference": "Lists are mutable, tuples are immutable."},
]

def evaluate_batch(chain, test_cases, evaluator):
    results = []
    for case in test_cases:
        prediction = chain.invoke({"question": case["input"]})
        score = evaluator.evaluate_strings(
            input=case["input"],
            prediction=prediction,
            reference=case["reference"],
        )
        results.append({
            "input": case["input"],
            "prediction": prediction,
            "score": score["score"],
            "reasoning": score.get("reasoning", ""),
        })
    return results

scores = evaluate_batch(chain, test_cases, qa_eval)
avg = sum(r["score"] for r in scores) / len(scores)
print(f"Average score: {avg:.2f}")
```

### 10.4 Caching

```python
from langchain.globals import set_llm_cache
from langchain_community.cache import InMemoryCache, SQLiteCache

# In-memory cache (lost on restart)
set_llm_cache(InMemoryCache())

# SQLite cache (persists to disk)
set_llm_cache(SQLiteCache(database_path=".langchain_cache.db"))

# Now identical calls return cached results instantly
model.invoke([HumanMessage(content="What is 2+2?")])  # calls API
model.invoke([HumanMessage(content="What is 2+2?")])  # returns from cache
```

### 10.5 Async production server pattern

```python
from fastapi import FastAPI
from pydantic import BaseModel as PydanticModel

app = FastAPI()

class ChatRequest(PydanticModel):
    session_id: str
    message: str

class ChatResponse(PydanticModel):
    reply: str
    session_id: str

@app.post("/chat", response_model=ChatResponse)
async def chat_endpoint(request: ChatRequest):
    reply = await chain_with_history.ainvoke(
        {"input": request.message},
        config={"configurable": {"session_id": request.session_id}},
    )
    return ChatResponse(reply=reply, session_id=request.session_id)

@app.get("/stream")
async def stream_endpoint(session_id: str, message: str):
    from fastapi.responses import StreamingResponse

    async def generate():
        async for chunk in chain_with_history.astream(
            {"input": message},
            config={"configurable": {"session_id": session_id}},
        ):
            yield chunk

    return StreamingResponse(generate(), media_type="text/plain")
```

### 10.6 Configuration & deployment

```python
from langchain_core.runnables import ConfigurableField

# Make model parameters configurable at runtime
configurable_model = ChatOpenAI(model="gpt-4o-mini").configurable_fields(
    temperature=ConfigurableField(
        id="temperature",
        name="LLM Temperature",
        description="Controls randomness. 0 = deterministic, 1 = creative.",
    ),
    model=ConfigurableField(
        id="model_name",
        name="Model name",
        description="The OpenAI model to use.",
    ),
)

chain = prompt | configurable_model | StrOutputParser()

# Override at call time
creative_result = chain.invoke(
    {"question": "Write a poem about space"},
    config={"configurable": {"temperature": 0.9, "model_name": "gpt-4o"}},
)

precise_result = chain.invoke(
    {"question": "What is 2^10?"},
    config={"configurable": {"temperature": 0.0, "model_name": "gpt-4o-mini"}},
)
```

---

*Next steps: see `langgraph_python.md` to build stateful multi-agent workflows, and `langsmith_python.md` for tracing, evaluation, and production monitoring.*
