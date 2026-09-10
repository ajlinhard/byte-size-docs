# ML Ops Overview
MLOps is essentially applying your ETL/pipeline discipline to models instead of just data, with a few new wrinkles. Here's the high-level lifecycle:

## The Shift for a Data Engineer
The two biggest mental shifts are probably: 
- **(a)** the artifact you're versioning and deploying is a *model*, not just data or code, and it decays silently in ways a broken pipeline doesn't
-  **(b)** the feature store is the thing standing between your existing feature-mining skills and eliminating train/serve inconsistency — that's likely your fastest on-ramp into this space.

To go deeper on any one stage — like how a feature store actually plugs into an existing batch pipeline, or how drift detection works in practice will take time and practice.

## High-Level Steps
**1. Problem framing**
Translate a business question into an ML problem: what's being predicted, what's the target variable, what does "good enough" look like (accuracy, latency, cost). This step doesn't exist in classic ETL — get it wrong and everything downstream is wasted effort.

**2. Data collection & versioning**
Same territory as your ETL work, but with an added twist: you need to version datasets (not just schemas), track lineage, and often handle labeling/annotation pipelines. Tools: DVC, lakeFS, Delta Lake.

**3. Feature engineering → Feature store**
This is your feature mining experience, productionized. The key new concept is the **feature store** (Feast, Tecton, Databricks Feature Store) — a central place that serves the *same* feature computation logic to both training (batch) and inference (often real-time). The reason this matters: mismatched logic between training and serving ("training-serving skew") is one of the top causes of silent model failure.

**4. Experimentation & training**
Iterative model training with experiment tracking (MLflow, Weights & Biases, Neptune) — logging hyperparameters, metrics, and artifacts so runs are reproducible and comparable. Think of it like version control for experiments, not just code.

**5. Model validation**
Offline evaluation against held-out data, plus checks your ETL background wouldn't typically need: bias/fairness testing, robustness checks, sometimes shadow deployment (running the new model silently alongside production to compare outputs before cutover).

**6. Model registry**
A model equivalent of an artifact repository — versioned models with metadata, staged as "staging" → "production" → "archived." This is the handoff point between data science and deployment.

**7. Deployment / serving**
Batch scoring (like a nightly pipeline job — very ETL-like) or online serving (a low-latency API endpoint). Deployment patterns include canary releases and blue-green, similar to standard software deploys but with a model artifact instead of a code binary.

**8. Monitoring & observability**
This is where MLOps really diverges from ETL monitoring. Beyond pipeline health (did the job run, did data land), you need to watch for:
- **Data drift** — input distributions shifting over time
- **Concept drift** — the relationship between inputs and target changing
- **Performance decay** — accuracy/precision degrading in production, often invisible until ground truth arrives later

**9. Retraining loop (continuous training)**
Automated or triggered retraining pipelines that kick off when drift is detected or on a schedule, then flow back through validation → registry → deployment. This closed loop is the "ops" part of MLOps — it's what turns steps 2–8 into a system instead of a one-off project.

**10. Governance**
Model cards, audit trails, explainability requirements — increasingly non-optional in regulated industries.

---

