# Chain of Thought for LLMs

**Chain of thought** refers to a prompting technique that encourages large language models to break down complex problems into intermediate reasoning steps before arriving at a final answer, rather than jumping directly to conclusions.

## How It Works

Instead of asking an LLM a question and expecting an immediate answer, chain of thought prompts guide the model to:
1. Show its reasoning process
2. Work through the problem step-by-step
3. Explain each intermediate step
4. Arrive at the final answer based on that reasoning

## Why It's Effective

**Improved accuracy**: By forcing the model to articulate its reasoning, it often catches logical errors and produces more correct answers.

**Better transparency**: You can see *how* the model arrived at its answer, making it easier to verify or debug.

**Better performance on complex tasks**: For math problems, logic puzzles, multi-step reasoning, and complex analysis, chain of thought significantly improves accuracy compared to direct prompting.

## Simple Example

**Without chain of thought:**
> Q: If a train travels 60 mph for 2.5 hours, how far does it go?
> A: 150 miles

**With chain of thought:**
> Q: If a train travels 60 mph for 2.5 hours, how far does it go? Let's think through this step by step.
> A: 
> 1. We know the formula: Distance = Speed × Time
> 2. Speed = 60 mph
> 3. Time = 2.5 hours
> 4. Distance = 60 × 2.5 = 150 miles
> Therefore, the train travels **150 miles**.

## Common Variations

**Self-Consistency**: Run the same prompt multiple times with chain of thought and take the majority answer—further improves accuracy.

**Tree of Thought**: Explore multiple reasoning paths simultaneously, evaluating which seem most promising.

**Least-to-Most Prompting**: Solve simpler subproblems first, then use those solutions to solve harder ones.

Chain of thought has become a fundamental technique in prompt engineering because it leverages a core strength of LLMs—their ability to articulate reasoning—to achieve more reliable results.

---
# Chain of Thought Built-In to Models
---
# Research Findings: Chain of Thought Built Into Modern LLMs

Yes! Recent LLMs have fundamentally transformed how chain of thought works. Rather than requiring users to prompt for it, newer reasoning-focused models now have chain of thought baked directly into their architecture and training. Here's what the research shows:

## Key Models with Built-in Chain of Thought

### **OpenAI's o1 and o3 Models**

The o1 models use "reasoning tokens" that are processed invisibly to users but play a critical role in allowing the model to think through intricate problems. More specifically:

**How it works internally:**

When the o1 model receives an input, the input is broken down into smaller sub-problems. The model evaluates several potential ways to solve these sub-problems in parallel, simulating a variety of "thinking" strategies. These reasoning tokens then feed their processed outcomes into the final completion stage.

The model doesn't immediately produce an answer. It first generates an internal chain of thought—working through the problem step by step, exploring approaches, catching contradictions, backtracking when something doesn't add up—and only then produces a final response.

**Training approach:**

O1 was trained using reinforcement learning with human feedback (RLHF), which means the model received rewards for generating desired reasoning steps. This is different from traditional LLM training—the model was specifically optimized to develop better reasoning processes, not just pattern matching.

### **DeepSeek-R1**

DeepSeek-R1 takes a different but equally sophisticated approach. DeepSeek-R1 uses massive reinforcement learning to unlock emergent reasoning capabilities, including extended chain-of-thought, reflection, verification, and even "aha moments".

**Key innovation:**

DeepSeek-R1 uses Group Relative Policy Optimization (GRPO), which evaluates policy improvements relative to a group of sampled responses rather than requiring a separate reward model. At its foundation, the approach involves asking the model to "think before you answer"—to write out reasoning before writing the solution, but through pure reinforcement learning optimization.

## How This Differs from Prompted Chain of Thought

The research reveals a fascinating insight: Recent studies suggest that in many cases, models form latent representations of answers deep in their middle layers, well before they start writing out their reasoning. The chain you see isn't necessarily the thinking process; it may be a narrative constructed afterward to justify a conclusion the model has already reached in high-dimensional vector space.

With built-in reasoning:
- Instead of immediately predicting an answer, reasoning models generate an internal reasoning trace first. This trace explores the problem space, considers different approaches, and validates conclusions before committing to a final output
- One of the most practical benefits is their role in reducing AI hallucinations—when the model makes a claim, it often checks that claim against its reasoning process

## Research Trade-offs

However, research from 2025 reveals that for many straightforward tasks, short reasoning sketches outperform long verbose chains. Studies show this is especially true for problems where long CoT can introduce "overthinking".

Also, while o1 models don't show reasoning tokens to users, this lack of transparency can make it challenging to understand how the model arrives at its conclusions, reducing trust in critical applications.

## The Bottom Line

Modern reasoning models have moved beyond chain-of-thought-as-a-prompt-trick to architecture-level reasoning built through sophisticated reinforcement learning. The reasoning happens internally during inference, and you only see the final answer—but the process is fundamentally more robust for complex problem-solving than standard LLM inference.
