# Encoder Architectures

## Relationship to Encoding/Decoding Structures

Cross-encoders represent a distinct approach compared to traditional encoder-decoder architectures:

**Versus Dual Encoders**: In dual-encoder systems, each input is processed by separate (often identical) encoders, producing independent embeddings that are later compared using metrics like cosine similarity. Cross-encoders instead process inputs jointly, enabling richer interaction modeling but at higher computational cost.

**Versus Encoder-Decoder**: Traditional encoder-decoder architectures (like in machine translation) encode source information and decode target sequences sequentially. Cross-encoders don't generate sequences but rather compute relationships between existing sequences.

**Encoding Philosophy**: Cross-encoders embody a "late interaction" philosophy where inputs interact deeply within the model rather than being compared post-encoding. This contrasts with "early interaction" (processing inputs together from the start) and "no interaction" (dual encoders) approaches.


## Origins and Historical Context
A cross-encoder is a neural network architecture used in AI embedding systems that processes pairs of inputs simultaneously to compute their similarity or relationship, rather than encoding each input separately. Let me break this down comprehensively.

Cross-encoders emerged from the evolution of transformer architectures and the need for more sophisticated text similarity models. The concept gained prominence around 2019-2020 as researchers sought to improve upon earlier approaches like Siamese networks and dual-encoder architectures. The development was heavily influenced by BERT and other bidirectional transformers, which demonstrated the power of joint attention mechanisms across input sequences.

The key insight was that processing two pieces of text together, rather than separately, allows the model to capture complex interactions and dependencies between them that wouldn't be apparent when encoding them independently.

## Core Concept and Architecture

A cross-encoder takes two inputs (typically text sequences) and processes them jointly through a single neural network, usually a transformer. The architecture typically looks like:

**Input Processing**: Two sequences A and B are concatenated with a separator token (like [SEP] in BERT), creating a single input: `[CLS] sequence_A [SEP] sequence_B [SEP]`

**Joint Encoding**: The concatenated input passes through transformer layers where attention mechanisms can operate across both sequences simultaneously. This allows every token in sequence A to attend to every token in sequence B and vice versa.

**Output**: The model produces a single similarity score or classification output, often using the [CLS] token representation or pooling strategies.

## Key Use Cases

**Information Retrieval**: Cross-encoders excel at re-ranking search results, taking a query and candidate document to produce refined relevance scores. They're often used as a second-stage ranker after initial retrieval by faster dual encoders.

**Semantic Textual Similarity**: Determining how similar two pieces of text are in meaning, going beyond surface-level word matching to capture semantic relationships.

**Natural Language Inference**: Determining logical relationships between premise and hypothesis statements (entailment, contradiction, neutrality).

**Question Answering**: Scoring question-passage pairs to identify the most relevant passages for answer extraction.

**Duplicate Detection**: Identifying whether two documents, queries, or records represent the same entity or concept.

**Paraphrase Detection**: Determining if two sentences express the same meaning despite different wording.

## Advantages and Trade-offs

**Advantages**:
- Higher accuracy due to rich cross-attention mechanisms
- Better capture of subtle semantic relationships
- Superior performance on complex similarity tasks
- Effective for tasks requiring deep understanding of input relationships

**Disadvantages**:
- Computationally expensive - requires processing each pair separately
- Not suitable for large-scale similarity search due to quadratic complexity
- Cannot pre-compute embeddings for efficient storage and retrieval
- Slower inference compared to dual encoders

## Modern Applications and Hybrid Approaches

Contemporary systems often use hybrid architectures that combine both approaches: dual encoders for initial candidate retrieval (leveraging pre-computed embeddings for speed) followed by cross-encoders for precise re-ranking of top candidates. This balances efficiency with accuracy.

Cross-encoders have also influenced the development of more sophisticated architectures like ColBERT, which attempts to capture some cross-encoder benefits while maintaining dual-encoder efficiency through late interaction mechanisms.

The concept continues evolving with transformer variants and remains fundamental to modern information retrieval, semantic search, and text understanding systems where high-quality similarity assessment is crucial.

---
## Code Examples

## 1. Dual-Encoder Architecture
- Uses `sentence-transformers/all-MiniLM-L6-v2` (a lightweight BERT-based model)
- Shows how queries and documents are encoded separately
- Demonstrates cosine similarity computation between embeddings
- Highlights the efficiency advantage for large-scale search

## 2. Cross-Encoder Architecture  
- Uses `cross-encoder/ms-marco-MiniLM-L-6-v2` (trained on MS MARCO dataset)
- Shows how query-document pairs are processed jointly
- Demonstrates the higher computational cost but better accuracy
- Illustrates the input format: `[CLS] query [SEP] document [SEP]`

## 3. Encoder-Decoder Architecture
- Uses `Helsinki-NLP/opus-mt-en-fr` (MarianMT for English-French translation)
- Shows the complete encode-then-decode process
- Demonstrates beam search for better generation quality
- Illustrates sequence-to-sequence transformation

## Key Features of the Code:
- **Detailed comments** explaining each step and architectural choice
- **Performance timing** to show speed differences
- **Sample data** with realistic queries, documents, and sentences
- **Error handling** and shape information for debugging
- **Comparison table** summarizing the trade-offs between approaches

## Running the Code:
You'll need to install the required packages:
```bash
pip install sentence-transformers transformers torch scikit-learn numpy
```

The code will download the pre-trained models automatically on first run. Each architecture section can be run independently if you only want to test specific approaches.

This example provides a practical foundation for understanding how these different encoder architectures work in practice and when to use each one.

```python
"""
Three Encoder Architectures: Dual-Encoder, Cross-Encoder, and Encoder-Decoder
============================================================================

This script demonstrates three different encoder architectures commonly used in NLP:
1. Dual-Encoder: For efficient similarity computation with pre-computed embeddings
2. Cross-Encoder: For high-accuracy similarity scoring with joint processing
3. Encoder-Decoder: For sequence-to-sequence tasks like translation

Models used:
- Dual-Encoder: sentence-transformers/all-MiniLM-L6-v2 (lightweight BERT-based)
- Cross-Encoder: cross-encoder/ms-marco-MiniLM-L-6-v2 (BERT-based cross-encoder)
- Encoder-Decoder: Helsinki-NLP/opus-mt-en-fr (MarianMT for English to French)

Requirements:
pip install sentence-transformers transformers torch scikit-learn numpy
"""

import numpy as np
import torch
from sentence_transformers import SentenceTransformer, CrossEncoder
from transformers import MarianMTModel, MarianTokenizer
from sklearn.metrics.pairwise import cosine_similarity
import time

# Sample data for demonstrations
SAMPLE_QUERIES = [
    "What is machine learning?",
    "How does artificial intelligence work?",
    "Explain deep learning concepts"
]

SAMPLE_DOCUMENTS = [
    "Machine learning is a subset of artificial intelligence that enables computers to learn and improve from experience without being explicitly programmed.",
    "Artificial intelligence refers to computer systems that can perform tasks typically requiring human intelligence, such as visual perception and decision-making.",
    "Deep learning uses artificial neural networks with multiple layers to model and understand complex patterns in data.",
    "Python is a high-level programming language known for its simplicity and readability in software development.",
    "Database management systems store, organize, and retrieve large amounts of structured data efficiently."
]

SAMPLE_ENGLISH_SENTENCES = [
    "Hello, how are you today?",
    "The weather is beautiful outside.",
    "I love learning about artificial intelligence."
]

print("="*80)
print("ENCODER ARCHITECTURES DEMONSTRATION")
print("="*80)

# =============================================================================
# 1. DUAL-ENCODER ARCHITECTURE
# =============================================================================
print("\n1. DUAL-ENCODER ARCHITECTURE")
print("-" * 40)
print("Model: sentence-transformers/all-MiniLM-L6-v2")
print("Purpose: Efficient similarity computation using pre-computed embeddings")
print("Architecture: Two separate (identical) encoders process inputs independently")

# Load pre-trained dual-encoder model
dual_encoder = SentenceTransformer('sentence-transformers/all-MiniLM-L6-v2')

def dual_encoder_similarity(queries, documents, model):
    """
    Dual-encoder approach: Encode queries and documents separately,
    then compute similarity using vector operations (cosine similarity).
    
    Advantages:
    - Fast inference after initial encoding
    - Embeddings can be pre-computed and cached
    - Efficient for large-scale similarity search
    
    Disadvantages:
    - No interaction between query and document during encoding
    - May miss subtle semantic relationships
    """
    
    start_time = time.time()
    
    # Step 1: Encode all queries independently
    # Each query becomes a dense vector representation
    print(f"\nEncoding {len(queries)} queries...")
    query_embeddings = model.encode(queries, show_progress_bar=False)
    print(f"Query embeddings shape: {query_embeddings.shape}")
    
    # Step 2: Encode all documents independently  
    # Each document becomes a dense vector representation
    print(f"Encoding {len(documents)} documents...")
    doc_embeddings = model.encode(documents, show_progress_bar=False)
    print(f"Document embeddings shape: {doc_embeddings.shape}")
    
    # Step 3: Compute similarity matrix using cosine similarity
    # This is where the "dual" aspect comes in - comparing embeddings from two encoders
    similarity_matrix = cosine_similarity(query_embeddings, doc_embeddings)
    
    encoding_time = time.time() - start_time
    print(f"Total encoding time: {encoding_time:.3f} seconds")
    
    return similarity_matrix, query_embeddings, doc_embeddings

# Demonstrate dual-encoder
print("\nRunning dual-encoder similarity computation...")
dual_sim_matrix, q_embeddings, d_embeddings = dual_encoder_similarity(
    SAMPLE_QUERIES, SAMPLE_DOCUMENTS, dual_encoder
)

print(f"\nSimilarity Matrix Shape: {dual_sim_matrix.shape}")
print("Top matches for each query:")
for i, query in enumerate(SAMPLE_QUERIES):
    # Find most similar document for this query
    best_doc_idx = np.argmax(dual_sim_matrix[i])
    similarity_score = dual_sim_matrix[i][best_doc_idx]
    print(f"Query: '{query}'")
    print(f"Best match: '{SAMPLE_DOCUMENTS[best_doc_idx]}'")
    print(f"Similarity: {similarity_score:.4f}\n")

# =============================================================================
# 2. CROSS-ENCODER ARCHITECTURE  
# =============================================================================
print("\n" + "="*80)
print("2. CROSS-ENCODER ARCHITECTURE")
print("-" * 40)
print("Model: cross-encoder/ms-marco-MiniLM-L-6-v2")
print("Purpose: High-accuracy similarity scoring through joint processing")
print("Architecture: Single encoder processes concatenated input pairs")

# Load pre-trained cross-encoder model
cross_encoder = CrossEncoder('cross-encoder/ms-marco-MiniLM-L-6-v2')

def cross_encoder_similarity(queries, documents, model):
    """
    Cross-encoder approach: Process query-document pairs jointly through
    a single transformer that can model interactions between inputs.
    
    Advantages:
    - Higher accuracy due to cross-attention between inputs
    - Better capture of semantic relationships
    - Superior performance on complex similarity tasks
    
    Disadvantages:  
    - Computationally expensive (O(n²) comparisons)
    - Cannot pre-compute embeddings
    - Slower inference for large collections
    """
    
    start_time = time.time()
    
    # Step 1: Create all query-document pairs
    # Each pair will be processed jointly: [CLS] query [SEP] document [SEP]
    pairs = []
    pair_info = []
    
    for i, query in enumerate(queries):
        for j, document in enumerate(documents):
            pairs.append([query, document])
            pair_info.append((i, j))
    
    print(f"\nProcessing {len(pairs)} query-document pairs...")
    print(f"Example pair format: {pairs[0]}")
    
    # Step 2: Process all pairs through the cross-encoder
    # The model internally concatenates and processes each pair jointly
    similarity_scores = model.predict(pairs, show_progress_bar=False)
    
    # Step 3: Reshape scores back into matrix format
    similarity_matrix = np.zeros((len(queries), len(documents)))
    for idx, (i, j) in enumerate(pair_info):
        similarity_matrix[i, j] = similarity_scores[idx]
    
    processing_time = time.time() - start_time
    print(f"Total processing time: {processing_time:.3f} seconds")
    
    return similarity_matrix, similarity_scores

# Demonstrate cross-encoder
print("\nRunning cross-encoder similarity computation...")
cross_sim_matrix, cross_scores = cross_encoder_similarity(
    SAMPLE_QUERIES, SAMPLE_DOCUMENTS, cross_encoder
)

print(f"\nSimilarity Matrix Shape: {cross_sim_matrix.shape}")
print("Top matches for each query:")
for i, query in enumerate(SAMPLE_QUERIES):
    # Find most similar document for this query
    best_doc_idx = np.argmax(cross_sim_matrix[i])
    similarity_score = cross_sim_matrix[i][best_doc_idx]
    print(f"Query: '{query}'")
    print(f"Best match: '{SAMPLE_DOCUMENTS[best_doc_idx]}'")
    print(f"Similarity: {similarity_score:.4f}\n")

# =============================================================================
# 3. ENCODER-DECODER ARCHITECTURE
# =============================================================================
print("\n" + "="*80)
print("3. ENCODER-DECODER ARCHITECTURE")
print("-" * 40)
print("Model: Helsinki-NLP/opus-mt-en-fr (MarianMT)")
print("Purpose: Sequence-to-sequence generation (e.g., translation)")
print("Architecture: Encoder processes input, decoder generates output sequence")

# Load pre-trained encoder-decoder model for translation
model_name = "Helsinki-NLP/opus-mt-en-fr"
tokenizer = MarianTokenizer.from_pretrained(model_name)
enc_dec_model = MarianMTModel.from_pretrained(model_name)

def encoder_decoder_translation(sentences, tokenizer, model):
    """
    Encoder-Decoder approach: Encode source sequence into context representation,
    then decode target sequence token by token using encoder context.
    
    Architecture Flow:
    1. Encoder: Processes input sequence, creates context representation
    2. Decoder: Generates output sequence using encoder context + previous tokens
    
    Advantages:
    - Excellent for sequence-to-sequence tasks
    - Can handle variable-length input/output
    - Captures complex mappings between sequence domains
    
    Disadvantages:
    - More complex than similarity-based approaches
    - Requires paired training data
    - Sequential generation can be slow
    """
    
    start_time = time.time()
    
    print(f"\nTranslating {len(sentences)} sentences from English to French...")
    
    # Step 1: Tokenize input sentences for the encoder
    # Convert text to token IDs that the model can process
    encoded = tokenizer(sentences, return_tensors="pt", padding=True, truncation=True)
    print(f"Encoded input shape: {encoded['input_ids'].shape}")
    print(f"Example tokens: {encoded['input_ids'][0][:10].tolist()}")
    
    # Step 2: Generate translations using encoder-decoder architecture
    # The model internally:
    # - Encodes English text into contextual representations
    # - Decodes French text token by token using encoder context
    with torch.no_grad():
        generated_tokens = model.generate(
            encoded['input_ids'], 
            attention_mask=encoded['attention_mask'],
            max_length=128,
            num_beams=4,  # Beam search for better quality
            early_stopping=True
        )
    
    # Step 3: Decode generated tokens back to text
    translations = tokenizer.batch_decode(generated_tokens, skip_special_tokens=True)
    
    translation_time = time.time() - start_time
    print(f"Total translation time: {translation_time:.3f} seconds")
    
    return translations, encoded, generated_tokens

# Demonstrate encoder-decoder
print("\nRunning encoder-decoder translation...")
translations, encoded_input, generated_output = encoder_decoder_translation(
    SAMPLE_ENGLISH_SENTENCES, tokenizer, enc_dec_model
)

print(f"\nTranslation Results:")
print("-" * 30)
for i, (english, french) in enumerate(zip(SAMPLE_ENGLISH_SENTENCES, translations)):
    print(f"English:  '{english}'")
    print(f"French:   '{french}'\n")

# =============================================================================
# COMPARISON SUMMARY
# =============================================================================
print("="*80)
print("ARCHITECTURE COMPARISON SUMMARY")
print("="*80)

comparison_data = [
    ["Architecture", "Dual-Encoder", "Cross-Encoder", "Encoder-Decoder"],
    ["Processing", "Independent encoding", "Joint processing", "Sequential generation"],
    ["Interaction", "Post-encoding similarity", "Cross-attention", "Encoder→Decoder context"],
    ["Speed", "Fast (pre-computed)", "Slow (pairwise)", "Medium (sequential)"],
    ["Accuracy", "Good", "Excellent", "Task-dependent"],
    ["Scalability", "Excellent", "Poor", "Good"],
    ["Use Cases", "Similarity search", "Re-ranking", "Translation, Summarization"],
    ["Memory", "Low (cached embeddings)", "High (all pairs)", "Medium"],
]

# Print comparison table
for row in comparison_data:
    print(f"{row[0]:<15} | {row[1]:<20} | {row[2]:<20} | {row[3]:<20}")
    if row[0] == "Architecture":
        print("-" * 80)

print("\n" + "="*80)
print("KEY TAKEAWAYS:")
print("="*80)
print("• Dual-Encoders: Best for large-scale similarity search with pre-computed embeddings")
print("• Cross-Encoders: Best for high-accuracy similarity when computational cost is acceptable") 
print("• Encoder-Decoders: Best for generative tasks requiring sequence transformation")
print("• Hybrid approaches often combine dual + cross encoders for optimal speed/accuracy balance")
```



