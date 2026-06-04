#%%
import boto3
import json
import numpy as np 
import os
import tiktoken

from IPython.display import display, Markdown
from datetime import datetime
from sentence_transformers import CrossEncoder
from sklearn.preprocessing import normalize
from botocore.config import Config

def cosine_similarity(vec1, vec2):
    """
    Compute the cosine similarity between two vectors.

    Args:
        vec1 (np.ndarray): A 1D array of shape (d,).
        vec2 (np.ndarray): A 1D array of shape (d,).

    Returns:
        float: The cosine similarity score between the two vectors.

    Note:
        Assumes input vectors are already L2-normalized (unit vectors).
        If not normalized, this returns the dot product, not true cosine similarity.
    """
    return np.dot(vec1, vec2)
#-----------------------------------------------------------------------------------------------------


def get_top_k_similar(query_vector, embedding_matrix, k=10, return_scores=False):
    """
    Find the top-k most similar vectors to a query vector using dot product similarity.

    Performs a vectorized similarity search against an embedding matrix and returns
    the indices of the k most similar vectors, sorted in descending order by similarity.

    Args:
        query_vector (np.ndarray): A 1D array of shape (d,) representing the query embedding.
        embedding_matrix (np.ndarray): A 2D array of shape (n, d) where each row is an embedding vector.
        k (int, optional): Number of top similar vectors to retrieve. Defaults to 10.
        return_scores (bool, optional): If True, also return the similarity scores. Defaults to False.

    Returns:
        np.ndarray: Array of shape (k,) containing indices of the top-k most similar vectors,
            sorted by similarity in descending order.
        tuple[np.ndarray, np.ndarray]: If return_scores=True, returns (top_k_indices, top_k_scores)
            where top_k_scores contains the corresponding similarity values.

    Note:
        Assumes vectors are normalized if cosine similarity behavior is desired,
        as this function uses dot product for similarity computation.
    """
    # Compute all similarities at once (vectorized)
    similarities = embedding_matrix @ query_vector  # shape (n,)
    
    # Get top-k indices (most similar)
    top_k_indices = np.argpartition(similarities, -k)[-k:]
    
    # Sort the top-k by similarity (descending)
    top_k_indices = top_k_indices[np.argsort(similarities[top_k_indices])][::-1]
    
    if return_scores:
        top_k_scores = similarities[top_k_indices]
        return top_k_indices, top_k_scores
    
    return top_k_indices
#-----------------------------------------------------------------------------------------------------


def init_sagemaker_client():
    """
    Initialize a connection to an AWS SageMaker inference endpoint.

    Args:
        

    Returns:
        tuple[botocore.client.SageMakerRuntime, str]: A tuple containing:
            - runtime_client: The boto3 SageMaker Runtime client for invoking the endpoint.
           

    Note:
        Assumes AWS credentials are configured via environment variables,
        AWS credentials file, or IAM role (e.g., on EC2/Lambda).
    """
    runtime_client = boto3.client(
        'sagemaker-runtime',
    )
    return runtime_client


#--------------------------------------------------------------------------------------------------------------------
def get_reranker(): #In future could make this accept various models, but it's fine for now

    # Download model from S3
    s3 = boto3.client('s3')
    bucket = 'prod-sagemaker-models-s3'
    prefix = 'models/ms-marco-MiniLM-L-6-v2/'
    local_dir = '/tmp/ms-marco-MiniLM-L-6-v2'

    os.makedirs(local_dir, exist_ok=True)

    paginator = s3.get_paginator('list_objects_v2')
    for page in paginator.paginate(Bucket=bucket, Prefix=prefix):
        for obj in page.get('Contents', []):
            key = obj['Key']
            local_path = os.path.join(local_dir, os.path.relpath(key, prefix))
            os.makedirs(os.path.dirname(local_path), exist_ok=True)
            if not os.path.exists(local_path):
                s3.download_file(bucket, key, local_path)

    # Load from local path
    reranker = CrossEncoder(local_dir)
    return reranker


def rerank_chunks_local(reranker, query, chunks, top_k=10, return_scores=False):
    pairs = [[query, chunk] for chunk in chunks]
    scores = reranker.predict(pairs)

    scores = np.array(scores)  # existing line YN

    # Minimal guard: if no scores, return empty iterable YN 
    if scores.size == 0:
        return (np.array([], dtype=int), np.array([], dtype=float)) if return_scores else np.array([], dtype=int)

    # Minimal fix: clamp top_k YN 
    top_k = min(top_k, len(scores))

    # Minimal guard: if k becomes 0, return empty iterable YN 
    if top_k == 0:
        return (np.array([], dtype=int), np.array([], dtype=float)) if return_scores else np.array([], dtype=int)

    top_k_indices = np.argpartition(scores, -top_k)[-top_k:]
    top_k_indices = top_k_indices[np.argsort(scores[top_k_indices])][::-1]

    if return_scores:
        top_k_scores = scores[top_k_indices]
        return top_k_indices, top_k_scores

    return top_k_indices

    #----------------------------------------------------------------------------------------------------------------


def generate_response(
                      prompt: str = None,  
                      role: str = 'You are a helpful assistant',
                      endpoint_name: str = 'gpt-oss-120b-endpoint',
                      max_tokens: int = 2560, 
                      temperature: float = 0.0,
                      message_history: list = None
                      ) -> str:
    """
    Generate a text response from a LLM model hosted on a SageMaker endpoint.

    Sends a prompt to the specified SageMaker endpoint and returns the generated text.
    Automatically handles different response formats from the endpoint.

    Args:
        role (str): The role passed to the LLM to assume.
        prompt (str): The input prompt to send to the model.
        client (botocore.client.SageMakerRuntime): The SageMaker Runtime client for 
            invoking the endpoint. Defaults to module-level `client`.
        endpoint_name (str): The name of the SageMaker endpoint. 
            Defaults to module-level `endpoint_name`.
        max_tokens (int, optional): Maximum number of tokens to generate. Defaults to 256.
        temperature (float, optional): Sampling temperature. Higher values increase 
            randomness. Set to 0 for deterministic output. Defaults to 0.1.

    Returns:
        str: The generated text response from the model.

    Note:
        - Uses top_p=0.95 and repetition_penalty=1.2 as fixed parameters.
        - Generation stops at newline characters by default.
        - Sampling is automatically disabled when temperature=0.
    """
    client = init_sagemaker_client()

    if message_history is None:
        payload = {
            "model": endpoint_name,  # must match SM_VLLM_SERVED_MODEL_NAME or the HF model ID
            "messages": [
                {"role": "system", "content": role},
                {"role": "user", "content": prompt}
            ],
            "max_tokens": max_tokens,
            "temperature": temperature,
            "top_p": 1.0,
            "seed": 42
        }
    else:
        payload = {
            "model": endpoint_name,  # must match SM_VLLM_SERVED_MODEL_NAME or the HF model ID
            "messages": message_history,
            "max_tokens": max_tokens,
            "temperature": temperature,
            "top_p": 1.0,
            "seed": 42
        }

    response = client.invoke_endpoint(
        EndpointName=endpoint_name,
        ContentType='application/json',
        Body=json.dumps(payload)
    )
    
    result = json.loads(response['Body'].read().decode())
    return result


class NumpyEncoder(json.JSONEncoder):
    def default(self, obj):
        if isinstance(obj, np.integer):
            return int(obj)
        elif isinstance(obj, np.floating):
            return float(obj)
        elif isinstance(obj, np.ndarray):
            return obj.tolist()
        return super(NumpyEncoder, self).default(obj)


def save_dbq_locally(dbq_json, claim_id, local_folder='output_jsons', save_for_benchmarking = False):
    """Save completed DBQ locally and return the file path"""
    
    # Create local output directory if it doesn't exist
    os.makedirs(local_folder, exist_ok=True)
    
    # Create filename with veteran ID and timestamp
    
    if save_for_benchmarking:
        filename = f"completed_dbq_{claim_id}_benchmark.json"
    else:
        timestamp = datetime.now().strftime('%Y%m%d_%H%M%S')
        filename = f"completed_dbq_{claim_id}_{timestamp}.json"
    # Create full local path
    local_path = os.path.join(local_folder, filename)
    
    # Save locally to the output_jsons folder
    with open(local_path, 'w') as f:
        json.dump(dbq_json, f, indent=2, cls=NumpyEncoder)
    
    print(f"✓ Saved locally to {local_path}")
    return local_path


def upload_dbq_to_s3(local_path, bucket_name='dbq-templates', bucket_key='input/'):
    """Upload a local file to S3"""
    
    # Extract filename from local path
    filename = os.path.basename(local_path)
    
    # Upload to S3
    s3_client = boto3.client('s3')
    s3_key = bucket_key + filename
    
    try:
        s3_client.upload_file(local_path, bucket_name, s3_key)
        print(f"✓ Uploaded to s3://{bucket_name}/{s3_key}")
        return f"s3://{bucket_name}/{s3_key}"
    except Exception as e:
        print(f"✗ Upload failed: {e}")
        return None

def list_s3_folders(bucket_name: str, folder_prefix: str = '', remove_folder_prefix = False) -> list:
    """
    List immediate subfolders within an S3 bucket prefix
    
    Args:
        bucket_name: Name of the S3 bucket
        folder_prefix: Folder path (e.g., 'logs/' or 'data/subfolder/')
                      Leave empty for root
    
    Returns:
        List of folder names (immediate subdirectories only)
    """
    s3 = boto3.client('s3')
    
    # Use delimiter to get only immediate folders
    result = s3.list_objects_v2(
        Bucket=bucket_name,
        Prefix=folder_prefix,
        Delimiter='/'
    )
    
    folders = []
    if 'CommonPrefixes' in result:
        for prefix in result['CommonPrefixes']:
            folders.append(prefix['Prefix'])
    
    if remove_folder_prefix:
        return [i.replace(folder_prefix, '') for i in folders]
    return folders

def list_s3_files(bucket_name: str, folder_prefix: str = '') -> list:
    """
    List all files in an S3 bucket folder
    
    Args:
        bucket_name: Name of the S3 bucket
        folder_prefix: Folder path (e.g., 'logs/' or 'data/subfolder/')
                      Leave empty for root
    
    Returns:
        List of file keys (full paths)
    """
    s3 = boto3.client('s3')
    
    files = []
    paginator = s3.get_paginator('list_objects_v2')
    
    for page in paginator.paginate(Bucket=bucket_name, Prefix=folder_prefix):
        if 'Contents' in page:
            for obj in page['Contents']:
                # Skip folders (keys ending with /)
                if not obj['Key'].endswith('/'):
                    files.append(obj['Key'])    
    return files

def pool_and_normalize_embeddings(embeddings_list, pooling_method='mean', squeeze_single=True):
    pooled_embeddings = []
    
    for embedding in embeddings_list:
        embedding = np.array(embedding)
        if embedding.ndim == 2:
            # Handle 2D: (sequence_length, embedding_dim)
            # Pool along axis=0 (sequence dimension)
            if pooling_method == 'mean':
                pooled = np.mean(embedding, axis=0)
            elif pooling_method == 'max':
                pooled = np.max(embedding, axis=0)
            else:
                raise ValueError(f"Unknown pooling method: {pooling_method}")
            
            # Normalize (pooled is 1D, so normalize directly)
            pooled = pooled.reshape(1, -1)  # Reshape to 2D for normalize
            normalized = normalize(pooled, norm='l2', axis=1)
            normalized = normalized.squeeze(0)  # Back to 1D
            
        elif embedding.ndim == 3:
            # Handle 3D: (batch, sequence_length, embedding_dim)
            # Pool along axis=1 (sequence dimension)
            if pooling_method == 'mean':
                pooled = np.mean(embedding, axis=1)
            elif pooling_method == 'max':
                pooled = np.max(embedding, axis=1)
            else:
                raise ValueError(f"Unknown pooling method: {pooling_method}")
            
            # Normalize for cosine similarity (L2 normalization)
            normalized = normalize(pooled, norm='l2', axis=1)
            
            # Squeeze if single batch element
            if squeeze_single and normalized.shape[0] == 1:
                normalized = normalized.squeeze(0)
        else:
            raise ValueError(f"Expected 2D or 3D array, got {embedding.ndim}D array")
        
        pooled_embeddings.append(normalized)
    
    return np.array(normalized)

def get_embedding(text, endpoint_name = 'bge-large-en-v1-5-tei-endpoint'):
    config = Config (
        retries={
            'max_attempts': 5,
            'mode': 'standard'
        }
    )
    client = boto3.client('sagemaker-runtime', config=config)
    response = client.invoke_endpoint(
        EndpointName=endpoint_name,
        ContentType='application/json',
        Body=json.dumps({"inputs": text})
    )
    embeddings = json.loads(response['Body'].read().decode())
    # embeddings = pool_and_normalize_embeddings(embeddings)

    return np.array(embeddings)

def get_file_text(s3_key , s3_bucket = 'api-datalake'):

    s3_client = boto3.client('s3')
    response = s3_client.get_object(Bucket=s3_bucket, Key=s3_key)
    full_text = response['Body'].read().decode('utf-8')

    return full_text

def get_n_tokens(text): #built for GPT OSS right now
    encoder = tiktoken.get_encoding("o200k_base")
    tokens = encoder.encode(text)

    return len(tokens)

def semantic_similarity_retrieval(filtered_df, query_text, k=100):
    """Retrieve top-k chunks using cosine similarity."""
    question_embedding = get_embedding(query_text).squeeze()

    vectors = [emb for embs in filtered_df['embeddings'] for emb in embs]
    chunks = [t for texts in filtered_df['texts'] for t in texts]
    metadata = [key for key, texts in zip(filtered_df['s3_key_pdf'], filtered_df['texts']) for _ in texts]
    metadata_ocr = [key for key, texts in zip(filtered_df['s3_key'], filtered_df['texts']) for _ in texts]
    page_numbers = [page_number for page_numbers in filtered_df['chunk_pages'] for page_number in page_numbers]

    vectors = np.array(vectors)
    if len(vectors.shape) > 1 and vectors.shape[1] == 1:
        vectors = vectors.squeeze(axis=1)

    k = min(k, len(vectors))
    top_cosine_indices = get_top_k_similar(question_embedding, vectors, k=k)

    top_cosine_chunks = [chunks[i] for i in top_cosine_indices]
    top_cosine_files = [metadata[i] for i in top_cosine_indices]
    top_cosine_files_ocr = [metadata_ocr[i] for i in top_cosine_indices]
    top_cosine_page_numbers = [page_numbers[i] for i in top_cosine_indices]

    return top_cosine_chunks, top_cosine_files, top_cosine_files_ocr, top_cosine_page_numbers

def rerank_and_select(reranker, question_text, top_cosine_chunks, top_cosine_files, top_cosine_files_ocr, top_cosine_page_numbers, top_k=20):
    """Rerank cosine similarity results and return the top-k refined chunks."""
    reranked_indices = rerank_chunks_local(reranker, question_text, top_cosine_chunks, top_k=top_k)

    top_chunks = [top_cosine_chunks[i] for i in reranked_indices]
    top_files = [top_cosine_files[i] for i in reranked_indices]
    top_ocr_files = [top_cosine_files_ocr[i] for i in reranked_indices]
    top_page_numbers = [top_cosine_page_numbers[i] for i in reranked_indices]

    return top_chunks, top_files, top_ocr_files, top_page_numbers

class Chatbot: #TODO: Add internal history that records everything processed and summarized as well
    MAX_TOKENS = 30000

    def __init__(self, message_history=None, system_prompt="You are a helpful assistant.", 
                 display_response_bool=True, document=None, document_prompt=None, max_summarization_tokens = None):
        self.display_response_bool = display_response_bool
        self.full_history = []
        if message_history is None:
            self.history = [
                {"role": "system", "content": system_prompt}
            ]
        else:
            self.history = message_history
        
        self.encoder = tiktoken.get_encoding("o200k_base")
        self.tokens_used = self.get_history_tokens()
        
        if document is not None:
            prompt = document_prompt or "Extract all relevant information from this document."
            self.process_large_document(document, prompt)
    
    def get_n_tokens(self, text):
        if not isinstance(text, str):
            return 0
        return len(self.encoder.encode(text))
    
    def get_history_tokens(self):  # <-- same indent level as __init__
        return sum(self.get_n_tokens(msg['content']) for msg in self.history)

    def split_into_chunks(self, text, chunk_size, overlap):
        chunks = []
        start = 0
        while start < len(text):
            end = start + chunk_size
            chunks.append(text[start:end])
            start = end - overlap
        return chunks

    def process_large_document(self, document_text, prompt, chunk_size=20000, overlap=400, max_summarization_tokens = None):
        chunks = self.split_into_chunks(document_text, chunk_size, overlap)
        
        chunk_answers = []
        for i, chunk in enumerate(chunks):
            chunk_bot = Chatbot(system_prompt=self.history[0]['content'], display_response_bool=False)
            chunk_bot.chat(
                f"You are reviewing section {i+1} of {len(chunks)} "
                f"from a document.\n\n"
                f"Document section:\n{chunk}\n\n"
                f"{prompt}\n\n"
                f"If this section contains nothing relevant, respond with 'NO_RELEVANT_INFO'."
            )
            
            response = chunk_bot.history[-1]['content']
            if "NO_RELEVANT_INFO" not in response:
                chunk_answers.append(response)
        
        if chunk_answers:
            combined = "\n---\n".join(chunk_answers)
            self.chat(
                f"The following information was extracted from different "
                f"sections of the same document:\n\n{combined}\n\n"
                f"Synthesize a single coherent response.",
                response_max_tokens_used = max_summarization_tokens if not None else 2560
            )
        else:
            self.history.append({"role": "assistant", "content": "No relevant information found in the document."})

    def summarize_history(self):
        system_prompt = self.history[0]
        old_history = self.history[1:-2]
        recent = self.history[-2:]
        
        if not old_history:
            return
        
        history_text = "\n".join(
            f"{msg['role'].upper()}: {msg['content']}" 
            for msg in old_history
        )
        
        summary_bot = Chatbot(
            # system_prompt="You summarize medical document review conversations, " # Maybe keep for DBQ analysis
            #               "preserving all clinical findings, values, and diagnoses.",
            display_response_bool = False
        )
        summary_bot.chat(
            f"Summarize the key findings from this conversation:\n\n{history_text}"
        )
        
        summary = summary_bot.history[-1]['content']
        
        self.history = [
            system_prompt,
            {"role": "user", "content": f"Summary of prior analysis:\n{summary}"},
            {"role": "assistant", "content": "Understood. I have the context from the prior analysis."},
            *recent
        ]
        self.tokens_used = self.get_history_tokens()

    def process_large_message(self, message, chunk_size=20000, overlap=2000):
        chunks = self.split_into_chunks(message, chunk_size, overlap)
        
        chunk_answers = []
        for i, chunk in enumerate(chunks):
            chunk_bot = Chatbot(
                system_prompt=self.history[0]['content'], 
                display_response_bool=False
            )
            chunk_bot.chat( #TODO: fix me to store the meaning of the original message better
                f"You are reviewing section {i+1} of {len(chunks)} "
                f"of a large input.\n\n"
                f"Section:\n{chunk}\n\n"
                f"Extract any relevant information. If this section contains "
                f"nothing relevant, respond with 'NO_RELEVANT_INFO'."
            )
            
            response = chunk_bot.history[-1]['content']
            if "NO_RELEVANT_INFO" not in response:
                chunk_answers.append(response)
        
        if chunk_answers:
            combined = "\n---\n".join(chunk_answers)
            self.chat(
                f"The following information was extracted from different "
                f"sections of a large input:\n\n{combined}\n\n"
                f"Synthesize a complete answer."
            )
        else:
            self.history.append({"role": "assistant", "content": "No relevant information found."})
            
            
    def display_response(self, response):
        content = response['choices'][0]['message']['content']
        reasoning = response['choices'][0]['message'].get('reasoning', '')
        
        display(Markdown(f"{content}"))
        
        if reasoning:
            display(Markdown(
                f"<details><summary>Reasoning</summary>\n\n{reasoning}\n\n</details>"
            ))
    def chat(self, user_message, append_chat = True, return_response = True, response_max_tokens_used = 2560, temperature = 0.0):
        incoming_tokens = self.get_n_tokens(user_message)
        history_tokens = self.get_history_tokens()
        
        # Case 1: The message itself is too large to ever fit
        if incoming_tokens > self.MAX_TOKENS - 2000:  # reserve space for system prompt + response
            self.process_large_message(user_message)
            return
        
        # Case 2: Message fits on its own, but history is too bloated
        if incoming_tokens + history_tokens > self.MAX_TOKENS:
            self.summarize_history()
        
        
        self.history.append({"role": "user", "content": user_message})
        

        
        response = generate_response(message_history=self.history, max_tokens = response_max_tokens_used, temperature=temperature)
        self.full_history.append({'input' : self.history, 'output': response})
        if not append_chat:
            self.history = self.history[:-1]
        
        
        assistant_message = response['choices'][0]['message']['content']
        if assistant_message is None:
            assistant_message = ""
        if append_chat:
            self.history.append({"role": "assistant", "content": assistant_message})
            
        if self.display_response_bool:
            self.display_response(response)
        self.tokens_used = self.get_history_tokens()
        if return_response:
            return response['choices'][0]['message']['content']
