# NLP Concepts High-Level
This document will go through high-level concepts in the field of NLP. This are the quick blurbs. More in-depth study and knowledge can be done on each topic.


## Natural Language Inference (NLI)
NLI stands for **Natural Language Inference**, also called textual entailment. It's a fundamental task in natural language processing where an AI system determines the logical relationship between two pieces of text.

Specifically, given a premise (a statement) and a hypothesis (another statement), the system must classify their relationship as one of three categories:

1. **Entailment** - The hypothesis logically follows from the premise
   - Premise: "All birds can fly"
   - Hypothesis: "Robins can fly" 
   - Relationship: Entailment

2. **Contradiction** - The hypothesis contradicts the premise
   - Premise: "John is in Paris"
   - Hypothesis: "John is in London"
   - Relationship: Contradiction

3. **Neutral** - The hypothesis is neither entailed by nor contradicts the premise
   - Premise: "The cat is sleeping"
   - Hypothesis: "The cat is black"
   - Relationship: Neutral

NLI is crucial for AI systems because it tests their ability to understand logical relationships, handle reasoning, and comprehend nuanced language meaning. It's used as a benchmark task for evaluating language models and appears in applications like fact-checking, question answering, and reading comprehension systems.

The task requires understanding context, semantics, world knowledge, and logical reasoning - making it a challenging but important capability for language AI systems.
