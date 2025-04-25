# Vector Search Methods in NLP

Vector search methods are fundamental techniques for comparing embeddings in natural language processing. These methods enable us to retrieve and rank text based on semantic meaning rather than just keyword matching. Let me explain the different types of vector search approaches and their applications.

## Similarity Search

Similarity search involves finding vectors (embeddings) that are most similar to a query vector using distance metrics.

### Common Similarity Metrics:

1. **Cosine Similarity**
   - Measures the cosine of the angle between two vectors
   - Value ranges from -1 (opposite direction) to 1 (same direction)
   - Not affected by vector magnitude, only by direction
   - Most widely used for text embeddings

```python
import numpy as np
from sklearn.metrics.pairwise import cosine_similarity

# Example embeddings (simplified)
query_embedding = np.array([[0.2, 0.5, 0.1, 0.8]])
document_embeddings = np.array([
    [0.1, 0.4, 0.2, 0.7],  # Document 1
    [0.8, 0.3, 0.9, 0.2],  # Document 2
    [0.3, 0.6, 0.2, 0.8]   # Document 3
])

# Calculate cosine similarity
similarities = cosine_similarity(query_embedding, document_embeddings)
print("Cosine similarities:", similarities)

# Get indices of documents sorted by similarity (highest first)
ranked_indices = np.argsort(similarities[0])[::-1]
print("Ranked documents:", ranked_indices)
```

2. **Euclidean Distance**
   - Measures the straight-line distance between two points
   - Lower values indicate higher similarity
   - Sensitive to vector magnitude

```python
from sklearn.metrics.pairwise import euclidean_distances

distances = euclidean_distances(query_embedding, document_embeddings)
print("Euclidean distances:", distances)

# Get indices sorted by distance (lowest first)
ranked_indices = np.argsort(distances[0])
print("Ranked documents:", ranked_indices)
```

3. **Dot Product**
   - Simple multiplication of corresponding vector elements
   - Affected by both direction and magnitude
   - Higher values indicate higher similarity

```python
dot_products = np.dot(query_embedding, document_embeddings.T)
print("Dot products:", dot_products)

# Get indices sorted by dot product (highest first)
ranked_indices = np.argsort(dot_products[0])[::-1]
print("Ranked documents:", ranked_indices)
```

4. **Manhattan Distance**
   - Sum of absolute differences between vector elements
   - Less sensitive to outliers than Euclidean distance

```python
from sklearn.metrics.pairwise import manhattan_distances

distances = manhattan_distances(query_embedding, document_embeddings)
print("Manhattan distances:", distances)

# Get indices sorted by distance (lowest first)
ranked_indices = np.argsort(distances[0])
print("Ranked documents:", ranked_indices)
```

## Semantic Search

Semantic search goes a step further by focusing specifically on understanding the meaning and intent behind a query, rather than just matching based on surface-level similarities. Semantic search leverages natural language processing and understanding to capture the contextual meaning of words and phrases.
Semantic search leverages embedding models to understand the meaning behind queries rather than just matching keywords. It matches documents based on semantic similarity rather than lexical similarity.

```python
from sentence_transformers import SentenceTransformer
import numpy as np

# Load pre-trained sentence transformer model
model = SentenceTransformer('all-MiniLM-L6-v2')

# Sample corpus
documents = [
    "The cat sits on the mat",
    "Machine learning algorithms require significant computational resources",
    "Neural networks have transformed natural language processing",
    "Deep learning models can understand semantic relationships"
]

# Create embeddings for all documents
document_embeddings = model.encode(documents)

# Query
query = "How do AI models understand language?"
query_embedding = model.encode([query])[0]

# Calculate cosine similarity
from sklearn.metrics.pairwise import cosine_similarity
similarities = cosine_similarity([query_embedding], document_embeddings)[0]

# Rank documents
ranked_indices = np.argsort(similarities)[::-1]
for i in ranked_indices:
    print(f"Score: {similarities[i]:.4f}, Document: {documents[i]}")
```

## Approximate Nearest Neighbor (ANN) Search

For large-scale embedding collections, exact nearest neighbor search becomes computationally expensive. ANN algorithms provide faster search with minimal accuracy loss.
ANN (Approximate Nearest Neighbor) search is closely related to both similarity search and semantic search, serving as an efficient implementation technique for them.

When dealing with large datasets, performing exact similarity search can be computationally expensive. ANN search addresses this challenge by sacrificing some precision for significant speed improvements. Rather than finding the exact nearest neighbors, ANN algorithms find approximate nearest neighbors that are "close enough" for practical purposes.

The relationship between these concepts can be understood as:

1. Similarity search is the general concept of finding similar items based on distance metrics.
2. ANN search is an efficiency-focused implementation approach for similarity search that trades perfect accuracy for speed.
3. Semantic search often leverages ANN search algorithms when working with vector embeddings that represent semantic meaning.

Common ANN algorithms include:
- Locality-Sensitive Hashing (LSH)
- Hierarchical Navigable Small World graphs (HNSW)
- Product Quantization
- Tree-based methods like k-d trees and ball trees

In practical applications like vector databases (Pinecone, Weaviate, etc.), ANN search is what makes it feasible to perform semantic search across millions or billions of embeddings with reasonable response times.

Would you like me to explain any of these ANN algorithms in more detail or discuss how they're specifically applied in semantic search systems?
### Popular ANN Algorithms:

1. **Locality-Sensitive Hashing (LSH)**
   - Uses hash functions to map similar items to the same buckets
   - Efficient for high-dimensional data

```python
from datasketch import MinHashLSH
import numpy as np

# Convert embeddings to binary format for LSH
def embedding_to_binary(embedding, threshold=0.5):
    return [1 if x > threshold else 0 for x in embedding]

# Example embeddings converted to binary
binary_embeddings = [
    embedding_to_binary(doc) for doc in document_embeddings
]

# Initialize LSH index
lsh = MinHashLSH(threshold=0.7, num_perm=128)

# Index documents
for i, binary_doc in enumerate(binary_embeddings):
    lsh.insert(f"doc_{i}", binary_doc)

# Query
binary_query = embedding_to_binary(query_embedding[0])
results = lsh.query(binary_query)
print("LSH results:", results)
```

2. **FAISS (Facebook AI Similarity Search)**
   - Efficient library for similarity search and clustering
   - Supports various indexing methods

```python
import faiss
import numpy as np

# Convert to float32 (required by FAISS)
document_embeddings_f32 = np.array(document_embeddings).astype('float32')
query_embedding_f32 = np.array(query_embedding).astype('float32')

# Get embedding dimension
dimension = document_embeddings_f32.shape[1]

# Create index
index = faiss.IndexFlatL2(dimension)  # L2 distance
index.add(document_embeddings_f32)    # Add vectors to index

# Search
k = 2  # number of nearest neighbors
distances, indices = index.search(query_embedding_f32, k)
print(f"Top {k} nearest neighbors: {indices}")
print(f"With distances: {distances}")
```

3. **Hierarchical Navigable Small World (HNSW)**
   - Graph-based approach for efficient search
   - Available in libraries like Annoy, FAISS, and Hnswlib

```python
import hnswlib
import numpy as np

# Initialize HNSW index
dimension = document_embeddings.shape[1]
num_elements = len(document_embeddings)

# Create index
index = hnswlib.Index(space='cosine', dim=dimension)
index.init_index(max_elements=num_elements, ef_construction=200, M=16)

# Add items
index.add_items(document_embeddings)

# Query
k = 3  # number of nearest neighbors
indices, distances = index.knn_query(query_embedding, k=k)
print(f"Top {k} nearest neighbors: {indices}")
print(f"With distances: {distances}")
```

## Hybrid Search

Hybrid search combines traditional keyword-based search with semantic search for improved results.

```python
import numpy as np
from sklearn.feature_extraction.text import TfidfVectorizer
from sklearn.metrics.pairwise import cosine_similarity
from sentence_transformers import SentenceTransformer

# Sample corpus
documents = [
    "The cat sits on the mat",
    "Machine learning algorithms require significant computational resources",
    "Neural networks have transformed natural language processing",
    "Deep learning models can understand semantic relationships"
]

# TF-IDF (keyword-based) search
tfidf_vectorizer = TfidfVectorizer()
tfidf_matrix = tfidf_vectorizer.fit_transform(documents)

# Semantic search
model = SentenceTransformer('all-MiniLM-L6-v2')
semantic_embeddings = model.encode(documents)

# Query
query = "How do AI models understand language?"

# Get TF-IDF score
query_tfidf = tfidf_vectorizer.transform([query])
tfidf_scores = cosine_similarity(query_tfidf, tfidf_matrix)[0]

# Get semantic score
query_semantic = model.encode([query])[0]
semantic_scores = cosine_similarity([query_semantic], semantic_embeddings)[0]

# Hybrid scoring (weighted combination)
alpha = 0.3  # weight for TF-IDF score
hybrid_scores = alpha * tfidf_scores + (1 - alpha) * semantic_scores

# Rank documents
ranked_indices = np.argsort(hybrid_scores)[::-1]
for i in ranked_indices:
    print(f"Score: {hybrid_scores[i]:.4f}, Document: {documents[i]}")
```

## Dense Retrieval

Dense retrieval uses neural networks to encode queries and documents into the same embedding space, then retrieves relevant documents using similarity search.

```python
from sentence_transformers import SentenceTransformer, util
import torch

# Load model
model = SentenceTransformer('msmarco-distilbert-base-v4')

# Example corpus
documents = [
    "The cat sits on the mat",
    "Machine learning algorithms require significant computational resources",
    "Neural networks have transformed natural language processing",
    "Deep learning models can understand semantic relationships"
]

# Create document embeddings
document_embeddings = model.encode(documents, convert_to_tensor=True)

# Query
query = "How do AI models understand language?"
query_embedding = model.encode(query, convert_to_tensor=True)

# Calculate similarity scores
scores = util.pytorch_cos_sim(query_embedding, document_embeddings)[0]

# Rank documents
ranked_results = torch.argsort(scores, descending=True)
for idx in ranked_results:
    print(f"Score: {scores[idx].item():.4f}, Document: {documents[idx]}")
```

## Cross-Encoder Reranking

Cross-encoders take query-document pairs as input and produce relevance scores, often used to rerank initial retrieval results.

```python
from sentence_transformers import CrossEncoder
import numpy as np

# Sample corpus
documents = [
    "The cat sits on the mat",
    "Machine learning algorithms require significant computational resources",
    "Neural networks have transformed natural language processing",
    "Deep learning models can understand semantic relationships"
]

# Query
query = "How do AI models understand language?"

# Create query-document pairs
pairs = [[query, doc] for doc in documents]

# Cross-encoder scoring
cross_encoder = CrossEncoder('cross-encoder/ms-marco-MiniLM-L-6-v2')
scores = cross_encoder.predict(pairs)

# Rank documents
ranked_indices = np.argsort(scores)[::-1]
for i in ranked_indices:
    print(f"Score: {scores[i]:.4f}, Document: {documents[i]}")
```

## Relationship Between Tokenization and Vector Search

Tokenization directly impacts vector search because:

1. Tokenization determines what units are embedded (words, subwords, etc.)
2. The quality of tokenization affects the quality of embeddings
3. Different tokenization approaches can result in different vector representations
4. Token-level search vs. sequence-level search depends on tokenization strategy

The choice of tokenization method influences how well embeddings capture semantic meaning, which ultimately affects search quality. Modern embedding models like BERT, RoBERTa, and Sentence-BERT use subword tokenization to create more effective embeddings for vector search.
