from fastapi import APIRouter, HTTPException, Depends, Query, Body
from typing import List, Dict, Any, Optional
import time
import traceback
from pydantic import BaseModel
from app.services.query_engine import QueryEngine
from app.services.embedder.openai_impl import OpenAIEmbedder
from app.services.vectorstore import VectorStore
from app.core import get_logger

# Initialize logger
logger = get_logger(__name__)

router = APIRouter(prefix="/query", tags=["query"])

# Initialize services
embedder = OpenAIEmbedder()
vector_store = VectorStore(embedder)
query_engine = QueryEngine(vector_store)


# Pydantic models for API
class QueryRequest(BaseModel):
    query: str
    top_k: int = 5


class QueryResponse(BaseModel):
    query: str
    results: List[Dict[str, Any]]
    sources: List[Dict[str, str]]


@router.post("/{vault_id}", response_model=QueryResponse)
def query_vault(vault_id: str, query_data: QueryRequest):
    """
    Query a vault with natural language.
    """
    logger.info(f"Processing query for vault {vault_id}: '{query_data.query}' (top_k={query_data.top_k})")
    start_time = time.time()
    
    try:
        # Log debug information
        logger.debug(f"Starting vector search for vault {vault_id}")
        
        # Execute query
        results = query_engine.query(vault_id, query_data.query, query_data.top_k)
        
        # Log successful execution
        execution_time = time.time() - start_time
        logger.info(f"Query completed in {execution_time:.3f}s with {len(results['results'])} results")
        
        return results
    except ValueError as e:
        logger.warning(f"Vault not found: {vault_id} - {str(e)}")
        raise HTTPException(status_code=404, detail=str(e))
    except Exception as e:
        logger.error(f"Error processing query: {str(e)}")
        logger.debug(f"Query error details: {traceback.format_exc()}")
        raise HTTPException(status_code=500, detail=f"An error occurred: {str(e)}")


@router.post("/{vault_id}/generate", response_model=Dict[str, Any])
def generate_response(vault_id: str, query_data: QueryRequest):
    """
    Query a vault and generate a response using an LLM.
    """
    logger.info(f"Generating response for vault {vault_id}: '{query_data.query}'")
    start_time = time.time()
    
    try:
        # First, get the relevant chunks
        logger.debug(f"Retrieving context chunks for query")
        results = query_engine.query(vault_id, query_data.query, query_data.top_k)
        
        # Extract context from results
        context = [result["content"] for result in results["results"]]
        context_length = sum(len(c) for c in context)
        logger.debug(f"Retrieved {len(context)} context chunks ({context_length} chars total)")
        
        # Generate response
        logger.info(f"Generating LLM response using {len(context)} context chunks")
        response_start = time.time()
        response = query_engine.generate_response(query_data.query, context)
        response_time = time.time() - response_start
        logger.debug(f"LLM response generated in {response_time:.3f}s")
        
        # Log completion metrics
        total_time = time.time() - start_time
        logger.info(f"Response generation completed in {total_time:.3f}s")
        
        # Prepare and return response
        sources = [{"document_name": r["document_name"], "document_path": r["document_path"]} 
                  for r in results["results"]]
        
        return {
            "query": query_data.query,
            "response": response,
            "sources": sources
        }
    except ValueError as e:
        logger.warning(f"Vault not found: {vault_id} - {str(e)}")
        raise HTTPException(status_code=404, detail=str(e))
    except Exception as e:
        logger.error(f"Error generating response: {str(e)}")
        logger.debug(f"Error details: {traceback.format_exc()}")
        raise HTTPException(status_code=500, detail=f"An error occurred: {str(e)}")