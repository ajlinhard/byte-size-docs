
import json
import boto3
import tiktoken


class Chatbot: #TODO: Add internal history that records everything processed and summarized as well
    MAX_TOKENS = 30000

    def __init__(self, message_history=None, endpoint=None, system_prompt="You are a helpful assistant.", 
                 display_response_bool=True, document=None, document_prompt=None, 
                 max_summarization_tokens = None):
        self.display_response_bool = display_response_bool
        self.endpoint_name = endpoint or 'gpt-oss-120b-endpoint'
        self.full_history = []
        if message_history is None:
            self.history = [
                {"role": "system", "content": system_prompt}
            ]
        else:
            self.history = message_history

        self.runtime_client = boto3.client(
                'sagemaker-runtime',
            )
        
        # self.encoder = tiktoken.get_encoding("o200k_base")
        self.tokens_used = self.get_history_tokens()
        
        if document is not None:
            prompt = document_prompt or "Extract all relevant information from this document."
            self.process_large_document(document, prompt)
    
    def get_n_tokens(self, text):
        # if not isinstance(text, str):
        #     return 0
        # return len(self.encoder.encode(text))
        return len(text)//4
    
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
            
            
    # def display_response(self, response):
    #     content = response['choices'][0]['message']['content']
    #     reasoning = response['choices'][0]['message'].get('reasoning', '')
        
    #     display(Markdown(f"{content}"))
        
    #     if reasoning:
    #         display(Markdown(
    #             f"<details><summary>Reasoning</summary>\n\n{reasoning}\n\n</details>"
    #         ))

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
        

        
        response = self.generate_response(message_history=self.history, max_tokens = response_max_tokens_used, temperature=temperature)
        self.full_history.append({'input' : self.history, 'output': response})
        if not append_chat:
            self.history = self.history[:-1]
        
        
        assistant_message = response['choices'][0]['message']['content']
        if assistant_message is None:
            assistant_message = ""
        if append_chat:
            self.history.append({"role": "assistant", "content": assistant_message})
            
        # if self.display_response_bool:
        #     self.display_response(response)
        self.tokens_used = self.get_history_tokens()
        if return_response:
            return response['choices'][0]['message']['content']
    
    def generate_response(self,
                        prompt: str = None,  
                        role: str = 'You are a helpful assistant',
                        endpoint_name: str = None,
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
        if endpoint_name is None:
            endpoint_name = self.endpoint_name
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

        response = self.runtime_client.invoke_endpoint(
            EndpointName=endpoint_name,
            ContentType='application/json',
            Body=json.dumps(payload)
        )
        
        result = json.loads(response['Body'].read().decode())
        return result
