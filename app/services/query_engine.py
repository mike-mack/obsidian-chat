from typing import List, Dict, Any, Optional
from app.services.vectorstore import VectorStore
from app.services.embedder.base import BaseEmbedder
from app.services.embedder.openai_impl import OpenAIEmbedder
from app.services.embedder.local_impl import LocalEmbedder
from app.db.models import Vault
from app.db.session import get_db_context
from app.config import EMBEDDING_MODEL


class QueryEngine:
    """
    Engine for querying document collections and generating responses.
    Handles semantic search and response generation.
    """
    
    def __init__(self, vector_store: Optional[VectorStore] = None):
        """
        Initialize the query engine.
        
        Args:
            vector_store: The vector store to use for querying
        """
        if vector_store:
            self.vector_store = vector_store
        else:
            # Create default embedder based on config
            if EMBEDDING_MODEL.lower() == "openai":
                embedder = OpenAIEmbedder()
            else:
                embedder = LocalEmbedder()
                
            self.vector_store = VectorStore(embedder)
    
    def query(self, vault_id: str, query_text: str, top_k: int = 5) -> Dict[str, Any]:
        """
        Query the vault with a natural language question.
        
        Args:
            vault_id: The ID of the vault to query
            query_text: The query text
            top_k: The number of results to return
            
        Returns:
            Dict: The query results with context and response
        """
        # Check if vault exists
        with get_db_context() as db:
            vault = db.query(Vault).filter(Vault.id == vault_id).first()
            if not vault:
                raise ValueError(f"Vault with ID '{vault_id}' not found")
        
        # Get relevant chunks from vector store
        results = self.vector_store.search(vault_id, query_text, top_k)
        
        # Extract context from results
        context = [result["content"] for result in results]
        
        # For now, just return the raw results
        # In a full implementation, we would use an LLM to generate a response
        return {
            "query": query_text,
            "results": results,
            "sources": [{"document_name": r["document_name"], "document_path": r["document_path"]} for r in results]
        }
    
    def generate_response(self, query_text: str, context: List[str]) -> str:
        """
        Generate a response to a query using the provided context.
        
        Args:
            query_text: The query text
            context: List of context strings
            
        Returns:
            str: The generated response
        """
        try:
            from openai import OpenAI
            from app.config import OPENAI_API_KEY
            
            if not OPENAI_API_KEY:
                return "OpenAI API key not configured. Unable to generate response."
                
            client = OpenAI(api_key=OPENAI_API_KEY)
            
            # Join context with separators
            context_text = "\n\n---\n\n".join(context)
            
            # Create system prompt
            system_prompt = (
                "You are a helpful assistant that answers questions based on the provided context from an Obsidian vault. "
                "If the answer cannot be found in the context, say that you don't know based on the available information. "
                "Do not make up information. Cite the documents you used in your answer."
            )
            
            # Create messages
            messages = [
                {"role": "system", "content": system_prompt},
                {"role": "user", "content": f"Context:\n{context_text}\n\nQuestion: {query_text}"}
            ]
            
            # Generate response
            response = client.chat.completions.create(
                model="gpt-4",
                messages=messages,  # type: ignore
                temperature=0.3,
                max_tokens=1000
            )
            
            return response.choices[0].message.content or ""
        except Exception as e:
            return f"Error generating response: {str(e)}"