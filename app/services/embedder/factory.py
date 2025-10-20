"""
Factory for creating embedder instances based on configuration.
"""
from app.config import EMBEDDING_MODEL, OPENAI_API_KEY
from app.services.embedder.base import BaseEmbedder
from app.services.embedder.openai_impl import OpenAIEmbedder
from app.services.embedder.local_impl import LocalEmbedder
from app.core import get_logger

logger = get_logger(__name__)


def get_embedder() -> BaseEmbedder:
    """
    Factory function to create and return the appropriate embedder instance
    based on the EMBEDDING_MODEL configuration.
    
    Returns:
        BaseEmbedder: An instance of the configured embedder
        
    Raises:
        ValueError: If the configured embedding model is not supported
    """
    model_type = EMBEDDING_MODEL.lower()
    
    logger.info(f"Initializing embedder with model type: {model_type}")
    
    if model_type == "openai":
        if not OPENAI_API_KEY:
            logger.warning(
                "OpenAI model selected but no API key found. "
                "Falling back to local embedder."
            )
            return LocalEmbedder()
        return OpenAIEmbedder()
    elif model_type == "local":
        return LocalEmbedder()
    else:
        raise ValueError(
            f"Unsupported embedding model: {model_type}. "
            f"Supported models: 'openai', 'local'"
        )
