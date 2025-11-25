# AI/ML Overview:

Helpful Overview Videos:
- [All ML Algorithms in 17 min](https://www.youtube.com/watch?v=E0Hmnixke2g)


## AI Terms
These are **sampling parameters** that control how language models generate text by affecting randomness and diversity in the output:

## **Temperature**
**Definition:** Controls the randomness of predictions by scaling the logits (raw prediction scores) before applying softmax. Higher temperature = more random, lower = more deterministic.

**How it works:** Divides logits by the temperature value. Temperature of 1.0 = unchanged probabilities. Lower values make high-probability tokens even more likely; higher values flatten the distribution.

**Typical values:**
- 0.0-0.3: Very focused, deterministic (factual tasks, code)
- 0.7-0.9: Balanced creativity (general conversation)
- 1.0+: More creative/random (brainstorming, fiction)

**Use cases:** Lower for accuracy-critical tasks like math or data extraction; higher for creative writing or generating diverse options.

## **Top-k**
**Definition:** Limits sampling to the k most likely next tokens, setting all others to zero probability.

**How it works:** At each step, only the top k tokens by probability are considered. If k=40, only the 40 most likely tokens can be selected.

**Typical values:**
- 0 or off: No limit (not recommended alone)
- 20-50: Good balance
- 1: Greedy decoding (always picks most likely)

**Use cases:** Prevents the model from selecting very unlikely tokens. Often combined with temperature or top-p.

## **Top-p (Nucleus Sampling)**
**Definition:** Samples from the smallest set of tokens whose cumulative probability exceeds p. Dynamically adjusts how many tokens are considered.

**How it works:** Tokens are sorted by probability, then selected until their cumulative sum reaches p. If p=0.9, enough tokens are included to cover 90% of the probability mass.

**Typical values:**
- 0.9-0.95: Standard (flexible, good results)
- 0.5-0.8: More focused
- 1.0: No filtering

**Use cases:** Generally preferred over top-k because it adapts to the confidence of predictions. When the model is confident, fewer tokens are considered; when uncertain, more options remain.

**Common combinations:** Temperature + top-p together, or temperature + top-k. Temperature=0.7 with top-p=0.9 is a popular balanced setting for general use.



Routing Model

Attention

## Machine Learning:

Supervised

Basic Linear Regression

Unsupervised Learning
Clustering
K-means
