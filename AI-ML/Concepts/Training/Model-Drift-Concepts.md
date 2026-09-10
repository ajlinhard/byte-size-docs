# Model Drift Concepts

### **Model Drift**

This is the degradation of a model's predictive performance over time because the real-world data it sees no longer matches the data it was trained on. It comes in two main flavors:

- **Data drift (covariate shift)**: the distribution of input features changes, even if the underlying relationship between inputs and outputs stays the same. Example: a fraud model trained on pre-pandemic spending patterns suddenly seeing very different transaction behavior.
- **Concept drift**: the actual relationship between inputs and the target variable changes — P(Y|X) shifts. Example: what counts as "spam" evolves as spammers change tactics, so the same email features now predict a different outcome.

Drift is usually detected by monitoring live performance metrics against a baseline, or using statistical tests (e.g., Population Stability Index, Kolmogorov-Smirnov test) to compare incoming data distributions to training data distributions.

### **Residual Models**

A residual model is a model trained specifically to predict the *residuals* — the errors, or the gap between a base model's predictions and the actual values — rather than the target itself. The idea is that if your primary model has systematic, learnable patterns in its mistakes, a second model can capture what the first one missed.

Common places this shows up:
- **Gradient boosting**: each new tree in the ensemble is fit to the residuals of the current ensemble's predictions, progressively reducing error.
- **Time series**: after removing trend and seasonality, you model the leftover residual component (often to check it's just noise, or to squeeze out any remaining signal).
- **Bias correction / stacking**: a secondary model learns to correct systematic bias in a base model's outputs, then the two are combined.

### **Model Adjustments**

This is the broader umbrella term for anything done to keep a model performing well over time — often the response to detected drift. It can range from light-touch to heavy-touch:

- **Recalibration**: adjusting output probabilities or decision thresholds without touching the underlying model (e.g., Platt scaling).
- **Partial/incremental retraining**: updating the model with recent data rather than starting over.
- **Full retraining**: rebuilding the model from scratch on a fresh dataset.
- **Residual correction**: layering a residual model on top of the existing one (tying back to the point above) instead of touching the original.
- **Feature or architecture updates**: adding new features, removing stale ones, or changing model structure if the old assumptions no longer hold.

**Is residual modeling just one type of Model Adjustment?**

Yes, essentially. To be precise about the relationship:

Model adjustment is the umbrella goal — "keep this model accurate as things change" — and it splits into two broad strategies:

1. **Modify the model directly**: recalibration, incremental retraining, full retraining, changing features/architecture.
2. **Leave the model alone and correct its output**: this is where residual modeling lives — you keep the original model as-is and bolt on a second model that predicts (and corrects for) its errors.

So residual modeling isn't just "one item in a flat list" — it represents a whole *category* of adjustment (correction-based, rather than modification-based). But within that category, it's still just one technique; other correction-based approaches exist too, like simple bias-offset corrections or ensemble reweighting. So: residual modeling is one type of model adjustment, and specifically it's the technique of choice when you want to correct a model's mistakes without disturbing the model itself.

### **How they fit together**: 
Model drift is the *problem* (performance eroding as the world changes), and model adjustments are the general *category of responses* to that problem. Residual modeling is one specific *technique* within that response — instead of discarding or fully retraining the original model, you patch it by learning a second model on its errors.
