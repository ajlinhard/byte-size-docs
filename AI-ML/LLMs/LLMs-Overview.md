# LLMs Overview
This topic has explode since the release of ChatGPT-3 in late 2023. The topic and use can be covered to all kinds of depths: from the high-level API calls and prompt engineering, to different model optimizations/fine tuning, down to the intense math and transformer strucutures.

![image](https://github.com/user-attachments/assets/bd783fd7-ddc4-40a6-a954-b5c63829c715)

## Key Vocabulary:

---
## Transformers
A Transformer is an architecture for tokenizing, scoring, and processing data in parallel in the deep learning space. It was a break through which has many nuanced sub-components, but most importantly allowed for processing of tokens to no longer need happen sequencially.

**Intro Video:** https://www.youtube.com/watch?v=wjZofJX0v4M&t
**Nueral Networks Intro Series:** https://www.youtube.com/watch?v=aircAruvnKk&list=PLZHQObOWTQDNU6R1_67000Dx_ZCJB-3pi&index=1

## Why Transformers Were Invented
Prior to transformers, sequence modeling primarily relied on recurrent neural networks (RNNs) like LSTMs and GRUs, which had several limitations:

1. **Sequential Processing**: RNNs processed tokens one after another, making them difficult to parallelize and slow to train on long sequences.
2. **Information Bottleneck**: Information from earlier parts of a sequence could be lost or diluted when processing later parts (the "vanishing gradient problem").
3. **Limited Context Window**: RNNs struggled to maintain context over very long sequences.

The transformer architecture was designed specifically to overcome these limitations, allowing for better parallelization during training and more effective modeling of long-range dependencies.

## How Transformers Work in LLMs
### The Transformer Block
A typical transformer block consists of:
1. Multi-head self-attention
2. Layer normalization
3. Feed-forward neural network (aka Multilayer Perceptron)
4. Another layer normalization
5. Residual connections around each sub-layer

### Core Components

1. **Self-Attention Mechanism**
   - The heart of the transformer is the self-attention mechanism that allows each position in a sequence to "attend" to all positions, determining their relevance.
   - Each token's representation is updated based on a weighted combination of all other tokens, with weights determined by compatibility scores.

2. **Multi-Head Attention**
   - Rather than using a single attention mechanism, transformers use multiple "heads" that each focus on different aspects of the relationships between tokens.
   - This allows the model to jointly attend to information from different representation subspaces.

3. **Positional Encoding**
   - Since transformers process all tokens simultaneously, they need a way to understand token order.
   - Positional encodings are added to token embeddings to provide information about position in the sequence.

4. **Feed-Forward Networks**
   - After attention layers, each token's representation is processed independently through feed-forward neural networks.
   - These typically consist of two linear transformations with a ReLU activation in between.

5. **Layer Normalization and Residual Connections**
   - These techniques help stabilize training and allow for building very deep models.

### How LLMs Use Transformers

Modern Large Language Models like GPT (Generative Pre-trained Transformer) are built by stacking many transformer decoder blocks on top of each other:

1. **Tokenization**: Text is converted into tokens (subword units).
2. **Embedding**: Tokens are converted to vector representations.
3. **Processing**: These vectors pass through multiple transformer blocks, each refining the contextual understanding of each token.
4. **Next Token Prediction**: In generative LLMs, the model predicts the next token based on all previous tokens.
5. **Auto-regressive Generation**: To generate text, LLMs repeatedly:
   - Process the existing sequence
   - Predict the next token
   - Add that token to the sequence
   - Repeat

### Key Innovations in Modern LLMs

1. **Scale**: Modern LLMs use vastly more parameters, data, and compute than the original transformer.
2. **Decoder-Only Architecture**: Many LLMs use only the decoder portion of the original transformer design.
3. **Pre-training and Fine-tuning**: Models are pre-trained on large text corpora and then fine-tuned for specific tasks.
4. **Attention Masking**: In decoder-only models, tokens can only attend to previous tokens (causal/autoregressive attention).

The transformer architecture's ability to model long-range dependencies and parallelize computation has been crucial to the remarkable capabilities of modern LLMs, enabling them to generate coherent, contextually relevant text across an enormous range of topics and tasks.

---
## Vectors and Vector Databases
The meaning of a token in a LLM is completely stored and represented by a high-dimensional array or vector. A full sentence, document, or context is represented by a series of these Vectors, which can be efficiently stored and referenced within a Vector database.

---
## Training and Fine Tuning

---
## RAG
