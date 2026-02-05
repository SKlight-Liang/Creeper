'''
Copyright(c) Liang Yiyan, Pekin University, 2025. All rights reserved.

I hope to provide a universal model calling interface to facilitate future calls that may be needed.
The interface will accept a prompt and a list of several images as input,
and output the model's response and thinking process, if it exists.
The content related to the interface will be encapsulated into a class, 
so that it can be easily extended in the future to support more formats and models. 
I used the OpenAI library during the implementation process, 
so please confirm that the model supports OpenAI interfaces.

Function Table:
ModelInterface(BaseURL: str, ModelName: str, APIToken: str) -- Initialize the model interface
ModelResponse(Prompt: str, ImageURLs: list, Temperature: float = 0.0, MaxTokens: int = 2048) -> dict 
-- Get model response based on prompt and images
ConcurrentModelAPI(Prompts: list, BatchImageURLs: list, Information: list, Temperature: float = 0.0, 
MaxTokens: int = 2048, Concurrency: int, SaveJsonlPath: str) -> list 
-- Concurrently call interface for a batch of prompts and images
'''

import json
import threading

from openai import OpenAI
from FileProcess import LogMessage

from concurrent.futures import ThreadPoolExecutor
from concurrent.futures import as_completed

from tqdm import tqdm

# Universal model calling interface
class ModelInterface:
    def __init__(self, BaseURL: str = None, ModelName: str = None, APIToken: str = None):
        self.BaseURL = BaseURL
        self.ModelName = ModelName
        self.APIToken = APIToken

        if not all([self.BaseURL, self.ModelName, self.APIToken]):
            raise ValueError("BaseURL, ModelName, and APIToken must be provided.")
        
        self.Client = OpenAI(
            base_url = self.BaseURL,
            api_key = self.APIToken
        )
        
        # Add a lock for thread-safe file writing
        self.FileLock = threading.Lock()


    # Get model response based on prompt and images
    
    # Note that we use "user" role for simplicity
    # If you want to use different roles like "system" or "assistant",
    # Perhaps you need to modify this function accordingly

    # Here ImageURLs supports images that are publicly accessible via URLs or base64 encoded images
    # The format of base64 encoded images should be like: "data:image/png;base64,{Base64String}"
    def ModelResponse(self, Prompt: str = "", ImageURLs: list = [],
                        Temperature: float = 0.0, MaxTokens: int = 2048          
    ) -> dict:
        # Construct contents for the model
        Contents = []

        # Add prompt as text content
        if Prompt: 
            Contents.append({
                "type": "text",
                "text": Prompt
            })

        # Add images as image contents
        for ImageURL in ImageURLs:
            Contents.append({
                "type": "image_url",
                "image_url": {
                    "url": ImageURL
                }
            })

        # Construct message for the model
        # Here we use the "user" role for simplicity
        # In practice, you may want to use different roles based on your needs
        Message = {
            "role": "user",
            "content": Contents
        }
        
        # Call the model API
        Response = self.Client.chat.completions.create(
            model = self.ModelName,
            messages = [Message],
            temperature = Temperature,
            max_tokens = MaxTokens
        )

        # Extract the model's reply, including model reponse and thinking process if available
        try:
            ModelReply = Response.choices[0].message.content
            ModelReasoning = None
            if hasattr(Response.choices[0].message, 'reasoning_content'):
                ModelReasoning = Response.choices[0].message.reasoning_content

            return {
                "Response": ModelReply,
                "Reasoning": ModelReasoning
            }
        
        except Exception as e:
            LogMessage(f"Error extracting model response: {str(e)}", Type="ERROR")
            return {
                "Response": None,
                "Reasoning": None
            }

    # Concurrently call interface for a batch of prompts and images to improve efficiency
    # Here we provide an output file interface here to save the results to a jsonl file 
    # The writing process is real-time and appended to avoid data loss.
    def ConcurrentModelAPI(self, 
        Prompts: list = [], BatchImageURLs: list = [], Information: list = [],
        Temperature: float = 0.0, MaxTokens: int = 2048, 
        Concurrency: int = 32, SaveJsonlPath: str = None) -> list:

        # Store all results
        Results = []

        with ThreadPoolExecutor(max_workers=Concurrency) as Executor:
            FutureToIdx = {}
            # Submit tasks to the executor
            for idx, Prompt in enumerate(Prompts):
                ImageURLs = BatchImageURLs[idx] if idx < len(BatchImageURLs) else []
                Future = Executor.submit(self.ModelResponse, Prompt, ImageURLs, Temperature, MaxTokens)
                FutureToIdx[Future] = idx

            # Process completed futures
            for Future in tqdm(as_completed(FutureToIdx.keys()), total=len(FutureToIdx), desc="Processing"):
                Result = Future.result()
                idx = FutureToIdx[Future]
                
                # Add additional information if provided
                if Information and idx < len(Information):
                    Result["Information"] = Information[idx]

                Results.append(Result)

                # Save to jsonl file if path is provided (thread-safe)
                if SaveJsonlPath:
                    try:
                        with self.FileLock:
                            with open(SaveJsonlPath, 'a', encoding='utf-8') as F:
                                F.write(json.dumps(Result, ensure_ascii=False) + '\n')

                    except Exception as e:
                        LogMessage(f"Error writing to jsonl file: {str(e)}", Type="ERROR")

        return Results