from langchain_core.embeddings import Embeddings
from langchain_openai import OpenAIEmbeddings, AzureOpenAIEmbeddings
import os
from typing import Optional, List

class OpenAIEmbeddingsWrapper:
    def __init__(self, api_key: Optional[str] = None, **kwargs):
        """
        Initializes the OpenAI embeddings object with the API key and optional parameters.

        Args:
            api_key (str, optional): The API key for OpenAI. If not provided, it will use the 
                                     `OPENAI_API_KEY` environment variable.
            **kwargs: Additional parameters for configuring the embeddings model.
                      For example, `model` or other OpenAI settings.
        """
        self.api_key = api_key or os.getenv("OPENAI_API_KEY")
        if not self.api_key:
            raise ValueError("OpenAI API key is required. Provide it as an argument or set it in the 'OPENAI_API_KEY' environment variable.")
        
        # Pass the API key and additional parameters to the OpenAIEmbeddings initializer
        self.embeddings = OpenAIEmbeddings(api_key=self.api_key, **kwargs)
    
    def _return_embed_model(self):
        """
        Returns the underlying OpenAI embeddings model.
        """
        return self.embeddings



class AzureOpenAIEmbeddingsWrapper:
    def __init__(self, api_key: Optional[str] = None, azure_endpoint: Optional[str] = None, **kwargs):
        """
        Initializes the Azure OpenAI embeddings object with the API key, endpoint, and optional parameters.

        Args:
            api_key (str, optional): The API key for Azure OpenAI. If not provided, it will use the
                                     `AZURE_OPENAI_API_KEY` environment variable.
            endpoint (str, optional): The endpoint for Azure OpenAI. If not provided, it will use the
                                       `AZURE_OPENAI_ENDPOINT` environment variable.
            **kwargs: Additional parameters for configuring the embeddings model.
                      For example, `deployment_name`, `model_version`, or other Azure-specific settings.
        """
        self.api_key = api_key or os.getenv("AZURE_OPENAI_API_KEY")
        self.endpoint = azure_endpoint or os.getenv("AZURE_OPENAI_ENDPOINT")
        
        if not self.api_key:
            raise ValueError("Azure OpenAI API key is required. Provide it as an argument or set it in the 'AZURE_OPENAI_API_KEY' environment variable.")
        if not self.endpoint:
            raise ValueError("Azure OpenAI endpoint is required. Provide it as an argument or set it in the 'AZURE_OPENAI_ENDPOINT' environment variable.")
        
        # Pass the API key, endpoint, and additional parameters to the AzureOpenAIEmbeddings initializer
        self.embeddings = AzureOpenAIEmbeddings(api_key=self.api_key, azure_endpoint=self.endpoint, **kwargs)
    
    def _return_embed_model(self):
        """
        Returns the underlying Azure OpenAI embeddings model.
        """
        return self.embeddings
