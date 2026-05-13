
Topics to cover:
1. Zero, One, Few Shot learning
2. Tagging
3. Semantic/Similarity Search
4. temp, top-p, top-k
5. Function calling


---
## Minimizing Token Usage
In order to keep cost down for both input and generation we want to use techniques which communicate needs and achieve desired results in minimal vtoekns/characters. There are many micro strategies to do this, but here is a shot list.
- TOON Format (Alternative to JSON - TOON Format)[https://www.kdnuggets.com/stop-wasting-tokens-a-smarter-alternative-to-json-for-llm-pipelines]
- Context Management
- Use LLMs to make more concise prompts.
- Summarize Input Supporting Text (this can decrease accuracy depending on needs)
