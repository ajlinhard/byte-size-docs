## Text Embedding Models

Embedding models convert text into dense numerical vectors (embeddings) that capture semantic meaning. Here are the main ones organized by scale:

**Sentence-level models**
- **Sentence-BERT (SBERT)** – The classic. Fine-tunes BERT with siamese networks so that semantically similar sentences cluster together in vector space.
- **all-MiniLM-L6-v2** – A distilled, fast SBERT variant. Great balance of speed and quality; very popular for RAG pipelines.
- **paraphrase-multilingual-mpnet-base-v2** – Handles 50+ languages.

**Page/document-level models**
- **OpenAI `text-embedding-3-large` / `ada-002`** – Strong general-purpose embeddings via API.
- **Cohere Embed v3** – Excels at long documents; supports up to 512 tokens with compression options.
- **BGE (BAAI General Embedding)** – A strong open-source family (bge-large-en, bge-m3) that handles longer passages well.
- **E5 (Microsoft)** – Instruction-tuned embeddings; prepending "query:" or "passage:" improves retrieval accuracy.

**Specialized / newer**
- **Nomic Embed** – Open, 8192-token context window, great for long pages.
- **GTE (Alibaba DAMO)** – Strong on benchmarks like MTEB; multilingual variants available.
- **Jina Embeddings v3** – Up to 8192 tokens, task-specific adapters.

**How similarity is measured** — Almost universally via **cosine similarity**: the cosine of the angle between two embedding vectors. Score of 1.0 = identical meaning, 0.0 = orthogonal, -1.0 = opposite.

---

Below is an interactive tool that runs a real `all-MiniLM-L6-v2` model **in your browser** via Transformers.js to compare two blocks of text:The tool runs the real `all-MiniLM-L6-v2` model directly in your browser — no API key or server needed. It downloads the model weights from Hugging Face on first load (~23MB), then computes 384-dimensional embeddings for each section and returns the cosine similarity.

**How to read the score:**
- **0.9 – 1.0** → near-duplicate in meaning
- **0.75 – 0.9** → strongly related
- **0.55 – 0.75** → moderately related
- **0.35 – 0.55** → loosely connected
- **< 0.35** → semantically different

A few things worth knowing about embedding similarity in practice: sentence-level models like MiniLM are optimized for shorter passages (a few sentences to a paragraph). For whole pages or long documents, you'd typically split into chunks, embed each chunk, and aggregate — either by averaging the chunk vectors or by taking the max similarity across chunk pairs. Models like BGE-M3 and Nomic Embed are better suited natively to longer contexts.
