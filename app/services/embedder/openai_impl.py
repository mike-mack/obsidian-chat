from typing import List, Dict, Any, Optional
import os
import time
from openai import OpenAI
from app.services.embedder.base import BaseEmbedder
from app.config import OPENAI_API_KEY, EMBEDDING_DIMENSION


class OpenAIEmbedder(BaseEmbedder):
    """
    Embedder implementation using OpenAI's embedding API.
    """
    
    def __init__(self, api_key: Optional[str] = None, model: str = "text-embedding-ada-002"):
        """
        Initialize the OpenAI embedder.
        
        Args:
            api_key: OpenAI API key (if None, will use from config)
            model: The embedding model to use
        """
        self.api_key = api_key or OPENAI_API_KEY
        if not self.api_key:
            raise ValueError("OpenAI API key is required")
        
        self.client = OpenAI(api_key=self.api_key)
        self.model = model
        self.embedding_dimension = EMBEDDING_DIMENSION
        
    def embed_text(self, text: str) -> List[float]:
        """
        Embed a single text string using OpenAI's API.
        
        Args:
            text: The text to embed
            
        Returns:
            List[float]: The embedding vector
        """
        if not text.strip():
            # Return zero vector for empty text
            return [0.0] * self.embedding_dimension
            
        try:
            response = self.client.embeddings.create(
                input=text,
                model=self.model
            )
            return response.data[0].embedding
        except Exception as e:
            print(f"Error embedding text: {str(e)}")
            # Retry once with exponential backoff
            time.sleep(2)
            try:
                response = self.client.embeddings.create(
                    input=text,
                    model=self.model
                )
                return response.data[0].embedding
            except Exception as retry_error:
                print(f"Retry failed: {str(retry_error)}")
                # Return zero vector on error
                return [0.0] * self.embedding_dimension
    
    def embed_batch(self, texts: List[str]) -> List[List[float]]:
        """
        Embed a batch of text strings.
        
        Args:
            texts: List of text strings to embed
            
        Returns:
            List[List[float]]: List of embedding vectors
        """
        if not texts:
            return []
            
        # Filter out empty strings and keep track of indices
        non_empty_texts = []
        indices = []
        for i, text in enumerate(texts):
            if text.strip():
                non_empty_texts.append(text)
                indices.append(i)
                
        # If all texts are empty, return zero vectors
        if not non_empty_texts:
            return [[0.0] * self.embedding_dimension for _ in texts]
            
        try:
            response = self.client.embeddings.create(
                input=non_empty_texts,
                model=self.model
            )
            
            # Create results list with zero vectors
            results = [[0.0] * self.embedding_dimension for _ in texts]
            
            # Fill in the embeddings for non-empty texts
            for i, idx in enumerate(indices):
                results[idx] = response.data[i].embedding
                
            return results
        except Exception as e:
            print(f"Error batch embedding texts: {str(e)}")
            # Return zero vectors on error
            return [[0.0] * self.embedding_dimension for _ in texts]
    
    def get_embedding_dimension(self) -> int:
        """
        Get the dimension of the embedding vectors.
        
        Returns:
            int: The dimension of the embedding vectors
        """
        return self.embedding_dimension