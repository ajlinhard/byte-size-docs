# Embedding Overviews
In the simplest statement embeddings are vecter representations(series of numbers) of a set of text. The set of test can be different sizes (tokens) often and represent a larger text. Splitting a larger text is often referred to a toeknizing.

## Documentation
Many of the ideas and concepts are covered very well in these documents and links:
- [Anthropic Embeddings](https://docs.anthropic.com/en/docs/build-with-claude/embeddings)
- [Open AI Embeddings](https://platform.openai.com/docs/guides/embeddings/limitations-risks#what-are-embeddings)


## Basic Useful Embedding Models:
- [BERT Family](https://huggingface.co/docs/transformers/en/model_doc/bert)
- [Voyage AI (recommended by Anthropic)](https://www.voyageai.com/)
- [Open AI Embedding Models](https://platform.openai.com/docs/guides/embeddings/limitations-risks#embedding-models)
- [Examples of Useful Models](https://www.perplexity.ai/search/create-a-list-of-different-emb-QfSxuUnKQIe.npvcv57FXg)

# Embedding Models for Different Text Sizes

## Short Text Embeddings (Phrases, Sentences)

- **OpenAI's text-embedding-ada-002**
  - Use case: Ideal for short text like search queries, product descriptions, or chat messages
  - Performance advantages: Optimized for semantic similarity matching in dense vector spaces, with good performance for retrieval tasks while maintaining reasonable computational requirements

- **GTE (General Text Embeddings)**
  - Use case: Excellent for sentence-level semantic search and retrieval
  - Performance advantages: Achieves high performance on the MTEB (Massive Text Embedding Benchmark) for short text while having relatively small parameter counts

## Medium Text Embeddings (Paragraphs, Short Documents)

- **BERT-based models (e.g., all-MiniLM-L6-v2)**
  - Use case: Good for paragraph-level semantic understanding and similarity matching
  - Performance advantages: Balances computation cost and accuracy well for medium-length texts, with lower latency than larger models

- **E5 models (e.g., E5-large)**
  - Use case: Excellent for retrieval augmented generation and knowledge-intensive tasks
  - Performance advantages: Strong performance on information retrieval benchmarks with medium-length texts while maintaining reasonable inference speed

## Long Text Embeddings (Documents, Articles)

- **LongFormer and BigBird**
  - Use case: Processing long documents with thousands of tokens
  - Performance advantages: Uses sparse attention mechanisms to efficiently handle long sequences with linear scaling rather than quadratic scaling of computational complexity

- **MPNet**
  - Use case: Document classification and clustering of longer texts
  - Performance advantages: Combines the advantages of BERT's masked language modeling and XLNet's permuted language modeling for better long-context understanding

## Domain-Specific Embeddings

- **BGE (BAAI General Embeddings)**
  - Use case: Specialized for multilingual retrieval and dense passage retrieval
  - Performance advantages: Optimized for cross-lingual search and information retrieval with strong performance across languages

- **SciBERT**
  - Use case: Scientific and biomedical text processing
  - Performance advantages: Pre-trained on scientific corpus for better domain-specific semantic understanding in research contexts

## Embedding Models with Customizable Context Windows

- **Cohere Embed models**
  - Use case: Flexible across different text lengths with adjustable truncation strategies
  - Performance advantages: Offers truncation_config parameter to control how text is processed, allowing optimization for different text lengths within the same model

Would you like me to elaborate on any specific model or discuss other considerations for embedding model selection?
