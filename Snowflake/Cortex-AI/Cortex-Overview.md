# Snowflake Cortex AI: Comprehensive Overview for LLM Data Operations
Cortex is the AI offering from Snowflake, to speed-up the use and interactions of AI.

### Documentation:
- [Snowflake Cortex Product Page](https://www.snowflake.com/en/product/features/cortex/)
- [Snowflake Cortex Documentation](https://docs.snowflake.com/en/user-guide/snowflake-cortex/aisql)
- [Youtube - Aimpoint Digital Snowflake Cortex Series](https://www.youtube.com/watch?v=Ur1LWpVDtzw)

## Overview

Snowflake Cortex is a fully-managed service that enables access to industry-leading large language models (LLMs) and provides AI features to understand unstructured data, answer freeform questions, and provide intelligent assistance. Since these LLMs are fully hosted and managed by Snowflake, using them requires no setup. Your data stays within Snowflake, giving you the performance, scalability, and governance you expect.

## Core LLM Features

### Available Models
Cortex now supports multiple industry-leading LLMs including Snowflake Arctic, Llama 3 (both 8B and 70B), Reka-Core, models from Mistral AI, Google, and Anthropic. Claude 3.5 Sonnet is a leader in general reasoning and multimodal capabilities and is well-suited for agentic workflows.

### Core LLM Functions
Snowflake Cortex features are provided as SQL functions and are also available in Python:

- **COMPLETE/AI_COMPLETE**: Given a prompt, returns a response that completes the prompt. This function accepts either a single prompt or a conversation with multiple prompts and responses
- **EMBED_TEXT_768/AI_EMBED**: Given a piece of text, returns a vector embedding that represents that text
- **EXTRACT_ANSWER**: Given a question and unstructured data, returns the answer to the question if it can be found in the data
- **SUMMARIZE**: Provides text summarization capabilities
- **TRANSLATE**: Offers translation services
- **SENTIMENT**: Analyzes sentiment in text
- **CLASSIFY**: Categorizes text into user-defined categories

## Data Preparation and Processing for LLMs

### Document Processing with PARSE_DOCUMENT
The PARSE_DOCUMENT function provides the ability to extract text, data, and layout elements from documents. It offers two modes:

- **OCR Mode**: Recommended for quick, high-quality text extraction from documents such as manuals, agreement contracts, product detail pages, insurance policies and claims, and SharePoint documents
- **LAYOUT Mode**: Optimized for extracting text and layout elements like tables. This is the recommended option to improve the context of a document knowledge base to optimize retrieval information systems and for Large Language Model (LLM) inference

### Vector Embeddings and Search
Snowflake Cortex offers the EMBED_TEXT_768 and EMBED_TEXT_1024 functions and several Vector similarity functions to compare them for various applications. Cortex Search enables low-latency, high-quality "fuzzy" search over your Snowflake data and powers Retrieval Augmented Generation (RAG) applications leveraging Large Language Models.

**Vector Similarity Functions**:
- VECTOR_COSINE_SIMILARITY
- VECTOR_INNER_PRODUCT
- VECTOR_L1_DISTANCE
- VECTOR_L2_DISTANCE

### Text Chunking for Optimal Processing
For best search results with Cortex Search, Snowflake recommends splitting the text in your search column into chunks of no more than 512 tokens (about 385 English words). Snowflake provides built-in functions to assist in splitting of text into smaller chunks using SPLIT_TEXT_RECURSIVE_CHARACTER.

## LLM Fine-Tuning Capabilities

### Cortex Fine-Tuning
Cortex Fine-tuning allows users to leverage parameter-efficient fine-tuning (PEFT) to create customized adaptors for use with pre-trained models on more specialized tasks. Cortex Fine-tuning is a fully managed service that lets you fine-tune popular LLMs using your data, all within Snowflake.

**Key Benefits**:
- Fine-tuning can help overcome issues with prompt engineering, offering benefits like reducing computational costs and utilizing leading-edge models without pre-training from scratch
- Using fine-tuning, organizations can make smaller models really good at specific tasks to deliver results with the accuracy of larger models at just a fraction of the cost

### Fine-Tuning Process
The FINETUNE function expects the training data to come from a Snowflake table or view and the query result must contain columns named prompt and completion. The process involves:

1. **Data Preparation**: The goal of the data preparation step is to create a dataset that will be used to train the model and help it learn from the prompt/completion pairs
2. **Training Data Requirements**: Start with a few hundred examples. Starting with too many examples may increase tuning time drastically with minimal improvement in performance
3. **Model Creation**: Using SQL syntax like:
```sql
SELECT SNOWFLAKE.CORTEX.FINETUNE(
  'CREATE', 
  'my_tuned_model', 
  'mistral-7b', 
  'SELECT prompt, completion FROM training_data',
  'SELECT prompt, completion FROM validation_data'
);
```

## RAG (Retrieval Augmented Generation) Implementation

### Cortex Search for RAG
Cortex Search gets you up and running with a hybrid (vector and keyword) search engine on your text data in minutes, without having to worry about embedding, infrastructure maintenance, search quality parameter tuning, or ongoing index refreshes.

**RAG Architecture**:
In retrieval-augmented generation (RAG), a user's query is used to find similar documents using vector similarity. The top document is then passed to a large language model (LLM) along with the user's query, providing context for the generative response.

### Complete RAG Workflow Example
```sql
-- Create embedding vectors for documents
ALTER TABLE documents ADD COLUMN vec VECTOR(FLOAT, 768);
UPDATE documents SET vec = SNOWFLAKE.CORTEX.EMBED_TEXT_768('snowflake-arctic-embed-m', content);

-- Perform semantic search and generate response
WITH result AS (
  SELECT content, query_text, 
         VECTOR_COSINE_SIMILARITY(vec, query_vec) AS similarity
  FROM documents, query_table
  ORDER BY similarity DESC LIMIT 1
)
SELECT SNOWFLAKE.CORTEX.COMPLETE('mistral-7b', 
       CONCAT('Answer this question: ', query_text, ' using this text: ', content))
FROM result;
```

## Advanced Features

### Cortex Agents
Cortex Agents, now available in public preview, orchestrates across structured and unstructured data sources to deliver insights. They break down complex queries, retrieve relevant data and generate precise answers, using Cortex Search, Cortex Analyst and LLMs.

### Enhanced Safety Features
Llama Guard, an LLM-based input-output safeguard model, comes natively integrated with Snowflake Arctic, and will soon be available for use with other models in Cortex LLM Functions.

## Use Cases for LLM Data Operations

1. **Text Analytics**: Running semantic search tasks with the embedding and vector distance functions to more clearly define target segments, then using foundation models to create personalized emails

2. **Document Processing**: Extract key details like invoice numbers, dates, amounts, and vendor names from incoming invoices to speed up processing and reduce human error

3. **Customer Support**: Categorize customer support tickets and generate custom email/text communications tailored to each customer ticket

4. **Healthcare**: Extract ICD10 codes from medical reports using large language models, creating labeled datasets for training smaller, fine-tuned models

## Cost Considerations

Snowflake Cortex AI functions incur compute cost based on the number of tokens processed. A token is the smallest unit of text processed by Snowflake Cortex AI functions, approximately equal to four characters. Fine-tuned models can be shared to other accounts with the USAGE privilege via Data Sharing.

## Security and Governance

All AI models run inside of Snowflake's security and governance perimeter. Your data is not available to other customers or model developers. Snowflake never uses your Customer Data to train models made available to our customer base.

Snowflake Cortex AI provides a comprehensive, integrated platform for working with LLMs, from data preparation and document processing to fine-tuning and deployment, all within Snowflake's secure, governed environment.
