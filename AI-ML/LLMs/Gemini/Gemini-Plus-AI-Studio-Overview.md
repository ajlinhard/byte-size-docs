# Gemini Models and AI Studio Overview
Google is obviously well invested in the AI arms race. They are creating a suite of tools, models, and papers geared towards advancing their models. Below is information gathered on the offerings at Google.

## Documentation/Tutorials
- [Google Official API Docs](https://ai.google.dev/gemini-api/docs)
- [Google Github AI Cookbooks](https://github.com/google-gemini/cookbook/blob/main/examples/)
- [Google Models](https://ai.google.dev/gemini-api/docs/models)

## AI Studio
The AI Studio tool/IDE is the place where Google aims to have developers engage with the Gemini models. Ideally from basic prompt engineering ideas like zero to multi-shot or chain-of-thought, all the way to intermediate/advance techniques like fine tuning.

[Link to AI Studio Home](https://aistudio.google.com/app/)

Additionally, you can interact with the models via your own API key which you can find in AI Studio as well.
[Link to API key Creation](https://aistudio.google.com/app/apikey)

```python
from google import genai
from google.genai import types
# import your secret manger here (example)
from kaggle_secrets import UserSecretsClient

client = genai.Client(api_key=UserSecretsClient().get_secret("GOOGLE_API_KEY"))
```
