# Medical AI Models

Yes, there are medical-specific rerankers on Hugging Face! Here are the most notable ones:

---

### 🏥 Purpose-Built Medical Rerankers

**1. `ncbi/MedCPT-Cross-Encoder`** *(Most notable)*
This is a cross-encoder from the NCBI (NIH) designed specifically for biomedical information retrieval. It's part of the MedCPT project — *Contrastive Pre-trained Transformers with large-scale PubMed search logs* — built for zero-shot biomedical IR. You feed it query-article pairs and it outputs relevance logits, where higher scores indicate higher relevance. This is arguably the most purpose-built medical reranker on the Hub.

**2. `BSC-NLP4BIA/Medprocner-CE-Reranker`**
A cross-encoder model trained using the sentence-transformers library, specifically for re-ranking in the context of **medical procedure entity linking**. It scores pairs of texts for reranking and semantic search in the biomedical NER/entity-linking pipeline.

---

### 🔬 General Rerankers with Strong Medical Performance

**3. `zeroentropy/zerank-1-reranker`**
This general-purpose reranker is benchmarked across a wide variety of domains and explicitly claims to outperform proprietary rerankers across **medical**, finance, legal, code, STEM, and conversational data.

---

### 🛠️ Fine-tuning Option

If none of these fit your exact use case, a common approach is to take a general reranker like `BAAI/bge-reranker-base` and fine-tune it on a medical dataset (e.g., PubMed pairs, BioASQ, MedMCQA). The `sentence-transformers` library makes this relatively straightforward.

---

**Best bet for biomedical RAG:** `ncbi/MedCPT-Cross-Encoder` — it's directly trained on PubMed search behavior and is freely available. Would you like example code for using it?
