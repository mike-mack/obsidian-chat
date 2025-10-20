from abc import ABC, abstractmethod
from typing import List, Union, Dict, Any


class BaseEmbedder(ABC):
    """
    Abstract base class for embedders.
    Defines the interface that all embedder implementations must follow.
    """
    
    @abstractmethod
    def embed_text(self, text: str) -> List[float]:
        """
        Embed a single text string into a vector.
        
        Args:
            text: The text to embed
            
        Returns:
            List[float]: The embedding vector
        """
        pass
    
    @abstractmethod
    def embed_batch(self, texts: List[str]) -> List[List[float]]:
        """
        Embed a batch of text strings into vectors.
        
        Args:
            texts: List of text strings to embed
            
        Returns:
            List[List[float]]: List of embedding vectors
        """
        pass
    
    @abstractmethod
    def get_embedding_dimension(self) -> int:
        """
        Get the dimension of the embedding vectors.
        
        Returns:
            int: The dimension of the embedding vectors
        """
        pass