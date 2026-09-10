# Monte Carlo Simulations
A Monte Carlo simulation is a technique for understanding uncertainty by running a model thousands (or millions) of times with randomly sampled inputs, then looking at the distribution of outcomes rather than a single "answer."

**The core idea**

Instead of solving a problem analytically (which may be impossible or intractable), you simulate it repeatedly:

1. Identify the uncertain inputs to your system and their probability distributions (e.g., demand ~ normal(1000, 200), failure rate ~ uniform(0.01, 0.05))
2. Randomly sample one value from each input's distribution
3. Run your model/calculation with those sampled values, record the output
4. Repeat thousands of times
5. Analyze the resulting distribution of outputs — mean, percentiles, probability of exceeding a threshold, etc.

The name comes from the randomness resembling casino games (Monte Carlo, the casino district in Monaco) — it was coined by physicists at Los Alamos in the 1940s working on nuclear chain reactions.

**A simple example**

Estimating π: randomly throw points into a square containing a circle, and the ratio of points landing inside the circle vs. the square converges to π/4 as your sample size grows. No formula, just repeated random sampling converging on an answer.

**Where it's actually used**

- **Finance**: simulating portfolio returns under thousands of random market scenarios to estimate risk (Value at Risk)
- **Project management**: estimating project completion dates when task durations are uncertain
- **Physics/engineering**: particle transport, reliability testing
- **ML/statistics**: Bayesian inference (MCMC — Markov Chain Monte Carlo), bootstrapping, hyperparameter search

**Why it matters for you specifically**

Given your pipeline/ETL background, the place this tends to show up is in **capacity planning and load estimation** — e.g., "if request volume follows this distribution and processing time follows that distribution, what's the 95th-percentile queue depth in my Step Functions pipeline?" Rather than doing the queueing-theory math by hand, you simulate thousands of runs with randomized inputs and read the percentiles off the output distribution. It's also common in **cost estimation** for variable cloud workloads (e.g., Bedrock invocation costs where token counts vary).

The main trade-off: it's computationally heavier than a closed-form solution, but it doesn't require you to derive one — you just need a model and the ability to sample and repeat, which is very much in an engineer's wheelhouse.
