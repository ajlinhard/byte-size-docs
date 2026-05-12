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

---
# Examples of Chunking
Here are several chunking strategies as a Python file, covering approaches suited for different embedding models and use cases:The file covers 8 strategies, each suited to different model families:

**Strategy → Best model family**

| Strategy | When to use |
|---|---|
| **Fixed char** | Any model, guaranteed size cap |
| **Token-based** (tiktoken) | OpenAI `text-embedding-3-*` — billing is per token |
| **Sentence-aware** | SBERT family (MiniLM, mpnet) — trained on sentences |
| **Paragraph** | BGE, E5 — good balance of context vs size |
| **Recursive** | Long-context models (Nomic, Jina, `text-embedding-3-large`) |
| **Semantic** | Any model where topic coherence matters most — breaks at actual topic shifts rather than arbitrary sizes |
| **Markdown/heading** | Structured docs, READMEs, wikis |
| **Streaming generator** | Very large files — yields one chunk at a time to avoid RAM pressure |

**Key design decisions in the file:**
- Every strategy returns a `Chunk` dataclass with `text`, `index`, `char_start`, `char_end`, and optional `metadata` — so they're drop-in compatible with each other
- Overlap is supported in all size-based strategies to avoid losing context at boundaries
- The semantic chunker uses a sliding window average over embeddings so a single noisy sentence doesn't trigger a false break

```python
"""
text_chunking.py
================
Chunking strategies for feeding text into embedding models.

Model           | Max tokens | Best chunking approach
----------------|------------|------------------------------
all-MiniLM-L6   | 256        | Fixed-size + sentence-aware
all-mpnet-base  | 384        | Sentence / paragraph
BGE-large-en    | 512        | Sentence / paragraph
text-embed-3    | 8191       | Recursive / semantic
Nomic-embed     | 8192       | Semantic / document-level
Jina v3         | 8192       | Semantic / document-level
"""

import re
import textwrap
from dataclasses import dataclass, field
from typing import Iterator


# ── 0. Shared data class ────────────────────────────────────────────────────

@dataclass
class Chunk:
    text: str
    index: int
    char_start: int
    char_end: int
    metadata: dict = field(default_factory=dict)

    def __repr__(self):
        preview = self.text[:60].replace("\n", " ")
        return f"Chunk({self.index}, chars={self.char_start}-{self.char_end}, '{preview}…')"


# ── 1. Fixed-size character chunking ────────────────────────────────────────
# Good for: any model when you need a hard size cap.
# Overlap prevents losing context at boundaries.

def fixed_char_chunks(
    text: str,
    chunk_size: int = 500,
    overlap: int = 50,
) -> list[Chunk]:
    """
    Split text every `chunk_size` characters, with `overlap` chars
    carried over into the next chunk.
    """
    chunks = []
    start = 0
    idx = 0

    while start < len(text):
        end = min(start + chunk_size, len(text))
        chunks.append(Chunk(
            text=text[start:end],
            index=idx,
            char_start=start,
            char_end=end,
        ))
        start += chunk_size - overlap
        idx += 1

    return chunks


# ── 2. Fixed-size token chunking (tiktoken) ─────────────────────────────────
# Good for: OpenAI text-embedding-3-* where billing + limits are in tokens.
# Requires:  pip install tiktoken

def fixed_token_chunks(
    text: str,
    model: str = "text-embedding-3-small",
    max_tokens: int = 512,
    overlap_tokens: int = 64,
) -> list[Chunk]:
    """
    Split text so each chunk contains at most `max_tokens` tokens.
    Uses tiktoken to count accurately for OpenAI models.
    """
    try:
        import tiktoken
    except ImportError:
        raise ImportError("pip install tiktoken")

    enc = tiktoken.encoding_for_model(model)
    token_ids = enc.encode(text)

    chunks = []
    start = 0
    idx = 0

    while start < len(token_ids):
        end = min(start + max_tokens, len(token_ids))
        chunk_tokens = token_ids[start:end]
        chunk_text = enc.decode(chunk_tokens)

        # Map back to char offsets (approximate)
        char_start = len(enc.decode(token_ids[:start]))
        char_end = char_start + len(chunk_text)

        chunks.append(Chunk(
            text=chunk_text,
            index=idx,
            char_start=char_start,
            char_end=char_end,
            metadata={"token_count": len(chunk_tokens)},
        ))
        start += max_tokens - overlap_tokens
        idx += 1

    return chunks


# ── 3. Sentence-aware chunking ───────────────────────────────────────────────
# Good for: SBERT family (MiniLM, mpnet, BGE) — models trained on sentences.
# Preserves sentence boundaries so embeddings stay semantically clean.

def sentence_chunks(
    text: str,
    max_sentences: int = 5,
    overlap_sentences: int = 1,
) -> list[Chunk]:
    """
    Split into groups of `max_sentences` sentences.
    Overlap carries the last `overlap_sentences` sentences into the next chunk.
    """
    # Simple regex sentence splitter — replace with spacy for better accuracy
    sentence_endings = re.compile(r'(?<=[.!?])\s+(?=[A-Z])')
    sentences = sentence_endings.split(text.strip())

    chunks = []
    start = 0
    idx = 0

    while start < len(sentences):
        end = min(start + max_sentences, len(sentences))
        chunk_sents = sentences[start:end]
        chunk_text = " ".join(chunk_sents)

        # Approximate char offsets
        char_start = text.find(sentences[start])
        char_end = char_start + len(chunk_text)

        chunks.append(Chunk(
            text=chunk_text,
            index=idx,
            char_start=max(char_start, 0),
            char_end=char_end,
            metadata={"sentence_count": len(chunk_sents)},
        ))
        start += max_sentences - overlap_sentences
        idx += 1

    return chunks


# ── 4. Paragraph chunking ───────────────────────────────────────────────────
# Good for: medium-context models (BGE, E5, mpnet).
# Paragraphs are natural semantic units — great for article/blog text.

def paragraph_chunks(
    text: str,
    max_chars: int = 1000,
    overlap_chars: int = 100,
) -> list[Chunk]:
    """
    Group blank-line-delimited paragraphs into chunks up to `max_chars`.
    Spills into a new chunk when adding the next paragraph would exceed the limit.
    """
    raw_paragraphs = [p.strip() for p in re.split(r'\n{2,}', text) if p.strip()]

    chunks = []
    buffer = []
    buffer_len = 0
    idx = 0
    char_cursor = 0

    def flush(buf: list[str], start: int) -> Chunk:
        joined = "\n\n".join(buf)
        return Chunk(
            text=joined,
            index=idx,
            char_start=start,
            char_end=start + len(joined),
            metadata={"paragraph_count": len(buf)},
        )

    buffer_start = 0
    for para in raw_paragraphs:
        if buffer and buffer_len + len(para) > max_chars:
            chunks.append(flush(buffer, buffer_start))
            idx += 1

            # Carry overlap: take last paragraph(s) up to overlap_chars
            overlap_buf = []
            for p in reversed(buffer):
                if sum(len(x) for x in overlap_buf) + len(p) <= overlap_chars:
                    overlap_buf.insert(0, p)
                else:
                    break
            buffer = overlap_buf
            buffer_len = sum(len(p) for p in buffer)
            buffer_start = char_cursor

        buffer.append(para)
        buffer_len += len(para)
        char_cursor += len(para) + 2  # +2 for \n\n

    if buffer:
        chunks.append(flush(buffer, buffer_start))

    return chunks


# ── 5. Recursive / hierarchical chunking ───────────────────────────────────
# Good for: long-context models (Nomic, Jina, text-embedding-3-large).
# Mirrors LangChain's RecursiveCharacterTextSplitter logic.
# Tries to split on natural boundaries first; falls back to hard cuts.

def recursive_chunks(
    text: str,
    chunk_size: int = 2000,
    overlap: int = 200,
    separators: list[str] | None = None,
) -> list[Chunk]:
    """
    Recursively split using a priority list of separators.
    Falls back to the next separator when a piece is still too large.
    """
    if separators is None:
        separators = ["\n\n", "\n", ". ", " ", ""]

    def _split(t: str, seps: list[str]) -> list[str]:
        if len(t) <= chunk_size:
            return [t]

        sep = seps[0]
        next_seps = seps[1:]

        parts = t.split(sep) if sep else list(t)
        pieces: list[str] = []
        current = ""

        for part in parts:
            candidate = (current + sep + part) if current else part
            if len(candidate) <= chunk_size:
                current = candidate
            else:
                if current:
                    pieces.append(current)
                    # Start next chunk with overlap
                    overlap_text = current[-overlap:] if overlap else ""
                    current = overlap_text + (sep if overlap_text else "") + part
                else:
                    # Single part is too large — recurse with next separator
                    if next_seps:
                        pieces.extend(_split(part, next_seps))
                    else:
                        # Hard cut as last resort
                        for i in range(0, len(part), chunk_size - overlap):
                            pieces.append(part[i:i + chunk_size])
                    current = ""

        if current:
            pieces.append(current)

        return pieces

    raw_pieces = _split(text, separators)

    chunks = []
    char_cursor = 0
    for idx, piece in enumerate(raw_pieces):
        char_start = text.find(piece, max(char_cursor - overlap - 10, 0))
        char_end = char_start + len(piece)
        chunks.append(Chunk(
            text=piece,
            index=idx,
            char_start=max(char_start, 0),
            char_end=char_end,
        ))
        char_cursor = char_end

    return chunks


# ── 6. Semantic / embedding-based chunking ──────────────────────────────────
# Good for: any model when topic-coherence matters more than size.
# Groups sentences by embedding similarity — chunks break at topic shifts.
# Requires: pip install sentence-transformers numpy

def semantic_chunks(
    text: str,
    model_name: str = "all-MiniLM-L6-v2",
    breakpoint_threshold: float = 0.3,
    window_size: int = 2,
) -> list[Chunk]:
    """
    Embed each sentence, then split where cosine similarity between adjacent
    windows drops below `breakpoint_threshold`. Topic shifts become boundaries.

    Lower threshold  → fewer, larger chunks (more lenient about breaks)
    Higher threshold → more, smaller chunks (stricter coherence per chunk)
    """
    try:
        from sentence_transformers import SentenceTransformer
        import numpy as np
    except ImportError:
        raise ImportError("pip install sentence-transformers numpy")

    sentence_endings = re.compile(r'(?<=[.!?])\s+(?=[A-Z])')
    sentences = sentence_endings.split(text.strip())
    if len(sentences) < 2:
        return [Chunk(text=text, index=0, char_start=0, char_end=len(text))]

    model = SentenceTransformer(model_name)
    embeddings = model.encode(sentences, normalize_embeddings=True)

    def window_embed(idx: int):
        lo = max(0, idx - window_size)
        hi = min(len(embeddings), idx + window_size + 1)
        return embeddings[lo:hi].mean(axis=0)

    # Cosine similarity between adjacent windows (already normalized)
    similarities = [
        float(np.dot(window_embed(i), window_embed(i + 1)))
        for i in range(len(sentences) - 1)
    ]

    # Split wherever similarity dips below threshold
    breakpoints = {i + 1 for i, s in enumerate(similarities) if s < breakpoint_threshold}

    chunks = []
    group_start = 0
    char_cursor = 0

    for i, sent in enumerate(sentences):
        if i in breakpoints and i > group_start:
            group = sentences[group_start:i]
            chunk_text = " ".join(group)
            char_start = text.find(sentences[group_start], max(char_cursor - 20, 0))
            chunks.append(Chunk(
                text=chunk_text,
                index=len(chunks),
                char_start=max(char_start, 0),
                char_end=max(char_start, 0) + len(chunk_text),
                metadata={
                    "sentence_count": len(group),
                    "avg_similarity": round(
                        sum(similarities[group_start:i]) / max(len(group) - 1, 1), 3
                    ),
                },
            ))
            char_cursor = max(char_start, 0) + len(chunk_text)
            group_start = i

    # Final group
    final_group = sentences[group_start:]
    if final_group:
        chunk_text = " ".join(final_group)
        char_start = text.find(sentences[group_start], max(char_cursor - 20, 0))
        chunks.append(Chunk(
            text=chunk_text,
            index=len(chunks),
            char_start=max(char_start, 0),
            char_end=max(char_start, 0) + len(chunk_text),
            metadata={"sentence_count": len(final_group)},
        ))

    return chunks


# ── 7. Markdown / structured-document chunking ─────────────────────────────
# Good for: docs, READMEs, wikis — split on heading hierarchy.
# Each heading section becomes its own chunk (with optional overflow splitting).

def markdown_chunks(
    text: str,
    max_chars: int = 1500,
) -> list[Chunk]:
    """
    Split markdown on H1/H2/H3 headings. If a section exceeds `max_chars`,
    fall back to recursive splitting within it.
    """
    heading_re = re.compile(r'^(#{1,3})\s+(.+)$', re.MULTILINE)
    matches = list(heading_re.finditer(text))

    if not matches:
        return recursive_chunks(text, chunk_size=max_chars)

    sections = []
    for i, match in enumerate(matches):
        start = match.start()
        end = matches[i + 1].start() if i + 1 < len(matches) else len(text)
        sections.append((match.group(0), text[start:end], start))

    chunks = []
    idx = 0

    for heading, body, char_start in sections:
        if len(body) <= max_chars:
            chunks.append(Chunk(
                text=body.strip(),
                index=idx,
                char_start=char_start,
                char_end=char_start + len(body),
                metadata={"heading": heading.strip()},
            ))
            idx += 1
        else:
            # Section too long — split recursively, keep heading as prefix
            sub_chunks = recursive_chunks(body, chunk_size=max_chars)
            for sc in sub_chunks:
                sc.index = idx
                sc.char_start += char_start
                sc.char_end += char_start
                sc.metadata["heading"] = heading.strip()
                chunks.append(sc)
                idx += 1

    return chunks


# ── 8. Streaming / generator variant ───────────────────────────────────────
# Good for: very large files where loading all chunks into memory is costly.

def stream_sentence_chunks(
    text: str,
    max_sentences: int = 5,
) -> Iterator[Chunk]:
    """
    Generator version of sentence chunking — yields one chunk at a time.
    Use with large documents to avoid holding all chunks in RAM.
    """
    sentence_endings = re.compile(r'(?<=[.!?])\s+(?=[A-Z])')
    sentences = sentence_endings.split(text.strip())
    buffer: list[str] = []
    idx = 0
    char_cursor = 0

    for sent in sentences:
        buffer.append(sent)
        if len(buffer) >= max_sentences:
            chunk_text = " ".join(buffer)
            yield Chunk(
                text=chunk_text,
                index=idx,
                char_start=char_cursor,
                char_end=char_cursor + len(chunk_text),
            )
            char_cursor += len(chunk_text) + 1
            idx += 1
            buffer = []

    if buffer:
        chunk_text = " ".join(buffer)
        yield Chunk(
            text=chunk_text,
            index=idx,
            char_start=char_cursor,
            char_end=char_cursor + len(chunk_text),
        )


# ── Demo ────────────────────────────────────────────────────────────────────

SAMPLE = textwrap.dedent("""
    Artificial intelligence has transformed the way we interact with technology.
    From voice assistants to recommendation engines, machine learning models now
    power countless aspects of daily life. These systems learn from vast datasets,
    identifying patterns that would be impossible for humans to detect manually.

    Natural language processing is one of the most visible branches of AI research.
    It enables machines to understand, generate, and reason about human language.
    Recent advances in transformer architectures have driven dramatic improvements
    in tasks like translation, summarization, and question answering.

    Retrieval-augmented generation (RAG) combines search with language models.
    A retriever first fetches relevant document chunks from a vector database.
    Those chunks are then injected into the model's context window as grounding.
    This approach reduces hallucinations and enables knowledge to be updated cheaply.

    Embedding models sit at the heart of modern RAG pipelines. They convert text
    into dense numerical vectors that capture semantic meaning. Similar passages
    end up close together in vector space, making similarity search efficient.
    Choosing the right chunking strategy directly affects retrieval quality.
""").strip()


if __name__ == "__main__":
    strategies = {
        "1. Fixed char (500, overlap=50)":    lambda: fixed_char_chunks(SAMPLE, 500, 50),
        "2. Sentence (5 sentences, overlap=1)": lambda: sentence_chunks(SAMPLE, 5, 1),
        "3. Paragraph (max 1000 chars)":       lambda: paragraph_chunks(SAMPLE, 1000, 100),
        "4. Recursive (2000 chars)":           lambda: recursive_chunks(SAMPLE, 2000, 200),
        "5. Markdown headings":                lambda: markdown_chunks(SAMPLE, 1500),
        "6. Streaming sentences":              lambda: list(stream_sentence_chunks(SAMPLE, 4)),
    }

    for name, fn in strategies.items():
        chunks = fn()
        print(f"\n{'─'*60}")
        print(f"  {name}")
        print(f"  → {len(chunks)} chunk(s)")
        for c in chunks:
            preview = c.text[:80].replace('\n', ' ')
            print(f"    [{c.index}] ({c.char_start}–{c.char_end})  '{preview}…'")

    # Semantic chunking (requires sentence-transformers)
    print(f"\n{'─'*60}")
    print("  7. Semantic (topic-shift breakpoints) — requires sentence-transformers")
    print("     Run:  pip install sentence-transformers numpy")
    print("     Then: chunks = semantic_chunks(your_text, breakpoint_threshold=0.3)")

    # Token chunking (requires tiktoken)
    print(f"\n{'─'*60}")
    print("  8. Token-based (tiktoken) — requires tiktoken")
    print("     Run:  pip install tiktoken")
    print("     Then: chunks = fixed_token_chunks(your_text, max_tokens=512)")
```
