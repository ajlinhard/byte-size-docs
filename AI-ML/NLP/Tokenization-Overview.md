# Tokenization in NLP/AI

Tokenization is the process of breaking down text into smaller units called tokens. It's a fundamental preprocessing step in natural language processing (NLP) and serves as the foundation for how AI models understand and process text.

### Documentation
- [Anthropic Embeddings](https://docs.anthropic.com/en/docs/build-with-claude/embeddings)
- [Crash Course for RAG](https://www.dailydoseofds.com/tag/rag-crash-course/)

## What are Tokens?

Tokens can be:
- Characters
- Subwords
- Words
- Phrases
- Sentences

The choice depends on the specific NLP task and model architecture.

## Common Tokenization Approaches

### 1. Word Tokenization

The simplest approach is splitting text by whitespace and removing punctuation:

```python
def simple_word_tokenize(text):
    # Remove punctuation and split by whitespace
    import re
    text = re.sub(r'[^\w\s]', '', text)
    tokens = text.split()
    return tokens

text = "Hello, world! How are you doing today?"
tokens = simple_word_tokenize(text)
print(tokens)  # ['Hello', 'world', 'How', 'are', 'you', 'doing', 'today']
```

Using NLTK's tokenizer:

```python
import nltk
nltk.download('punkt')
from nltk.tokenize import word_tokenize

text = "Hello, world! How are you doing today?"
tokens = word_tokenize(text)
print(tokens)  # ['Hello', ',', 'world', '!', 'How', 'are', 'you', 'doing', 'today', '?']
```

### 2. Subword Tokenization

Subword tokenization breaks words into meaningful subunits, helping with rare words and morphologically rich languages:

#### Byte-Pair Encoding (BPE)

```python
from transformers import AutoTokenizer

# Load a BPE tokenizer (GPT-2 uses BPE)
tokenizer = AutoTokenizer.from_pretrained("gpt2")

text = "Tokenization is fundamental to NLP"
tokens = tokenizer.tokenize(text)
print(tokens)  # ['Token', 'ization', 'is', 'fundamental', 'to', 'NLP']

# Get token IDs
token_ids = tokenizer.encode(text)
print(token_ids)
```

#### WordPiece (used by BERT)

```python
from transformers import BertTokenizer

tokenizer = BertTokenizer.from_pretrained("bert-base-uncased")

text = "Tokenization is fundamental to NLP"
tokens = tokenizer.tokenize(text)
print(tokens)  # ['token', '##ization', 'is', 'fundamental', 'to', 'nlp']
```

#### SentencePiece

```python
import sentencepiece as spm

# Training a model (simplified example)
with open('corpus.txt', 'w') as f:
    f.write("Tokenization is fundamental to NLP")

spm.SentencePieceTrainer.train('--input=corpus.txt --model_prefix=m --vocab_size=100')

# Loading and using the model
sp = spm.SentencePieceProcessor()
sp.load('m.model')
tokens = sp.encode_as_pieces("Tokenization is fundamental to NLP")
print(tokens)
```

### 3. Character-Level Tokenization

```python
def char_tokenize(text):
    return list(text)

text = "Hello!"
tokens = char_tokenize(text)
print(tokens)  # ['H', 'e', 'l', 'l', 'o', '!']
```

## Tokenization in Modern NLP Systems

Modern NLP systems often use hybrid approaches:

1. **Normalization**: Converting text to lowercase, removing accents
2. **Pre-tokenization**: Splitting text into words using rules
3. **Subword tokenization**: Further splitting words into subword units
4. **Special token addition**: Adding model-specific tokens like [CLS], [SEP]

## Challenges in Tokenization

- **Language-specific issues**: Different languages require different approaches
- **Out-of-vocabulary (OOV) words**: Words not seen during training
- **Multiword expressions**: Phrases that should be treated as single units
- **Ambiguities**: Words with multiple meanings based on context

## Tokenization and Embeddings: The Connection

Tokenization directly relates to embeddings in several crucial ways:

1. **Input Transformation**: Embeddings can only be created after text is tokenized. The tokenizer converts raw text into tokens, which are then mapped to their corresponding embedding vectors.

2. **Vocabulary Size**: The tokenizer determines the vocabulary size of the embedding space. Each unique token in the vocabulary gets its own embedding vector.

3. **Semantic Granularity**: The tokenization method affects the semantic granularity of embeddings:
   - Word-level tokenization: Each word has its own embedding
   - Subword tokenization: Embeddings can capture morphological structure
   - Character-level tokenization: Embeddings represent individual characters

4. **Handling Rare Words**: Subword tokenization helps embedding models handle rare or unseen words by breaking them into familiar subword units that already have embeddings.

```python
# Example showing the pipeline from text to embeddings
from transformers import AutoTokenizer, AutoModel
import torch

# Load pre-trained model and tokenizer
tokenizer = AutoTokenizer.from_pretrained("bert-base-uncased")
model = AutoModel.from_pretrained("bert-base-uncased")

# Input text
text = "Understanding tokenization improves NLP models"

# 1. Tokenize the text
tokens = tokenizer.tokenize(text)
print("Tokens:", tokens)

# 2. Convert tokens to IDs
token_ids = tokenizer.encode(text, return_tensors="pt")
print("Token IDs:", token_ids)

# 3. Get embeddings from the model
with torch.no_grad():
    outputs = model(token_ids)
    embeddings = outputs.last_hidden_state
    
print("Embedding shape:", embeddings.shape)
# Shape will be [1, sequence_length, embedding_dimension]
# Where sequence_length is the number of tokens including special tokens
```

In this example, we see the complete pipeline: raw text → tokens → token IDs → embedding vectors. Each token gets mapped to a high-dimensional vector that captures its semantic and syntactic properties in the context of the sentence.

The quality and characteristics of embeddings are heavily influenced by the tokenization strategy used during model training. This is why modern language models put significant effort into developing sophisticated tokenization schemes that balance vocabulary size, representation power, and computational efficiency.

---
# Embedding Models vs. Large Language Models (LLMs)

Embedding models and Large Language Models (LLMs) are two different types of AI models that serve distinct purposes:

## Embedding Models
- Create numerical representations (vectors) of text, images, or other data
- Usually much smaller and more specialized than LLMs
- Convert words, phrases, or entire documents into fixed-length vectors in a high-dimensional space
- The vectors capture semantic relationships, allowing similar items to be close to each other in the vector space
- Primarily used for similarity comparisons, clustering, search, and retrieval
- Examples include Word2Vec, GloVe, BERT embeddings, and OpenAI's text-embedding models

## Large Language Models (LLMs)
- Generate and process natural language text
- Typically much larger and more complex than embedding models
- Can understand context, generate coherent text, answer questions, and perform various language tasks
- Trained to predict the next token in a sequence given previous tokens
- Used for text generation, summarization, translation, question answering, and other language tasks
- Examples include GPT models, Claude (that's me!), LLaMA, and PaLM

## Key Differences
1. **Purpose**: Embeddings represent text as vectors for comparison; LLMs generate and process text
2. **Size**: Embedding models are generally smaller than full LLMs
3. **Output**: Embeddings produce fixed-length vectors; LLMs produce natural language text
4. **Applications**: Embeddings are often used as components within larger systems (like search engines), while LLMs can be used as standalone applications

LLMs sometimes use embedding layers internally as part of their architecture, but the complete LLM has many additional components beyond just the embedding functionality.
