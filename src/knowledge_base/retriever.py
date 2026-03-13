"""Knowledge base retrieval module with keyword-based matching."""

import logging
from typing import List, Optional
from langchain_core.documents import Document

from src.config import settings
from src.knowledge_base.loader import KnowledgeBaseLoader

logger = logging.getLogger(__name__)


class KnowledgeBaseRetriever:
    """Manages the company knowledge base and provides document retrieval functionality."""

    def __init__(self) -> None:
        """Initialize the KnowledgeBaseRetriever and load documents."""
        self.top_k = settings.RETRIEVE_TOP_K
        self.document_chunks: List[Document] = []
        self._load_and_split_documents()

    def _load_and_split_documents(self) -> None:
        """Load all documents from the knowledge base and split them into chunks."""
        logger.info("Loading and splitting knowledge base documents...")
        loader = KnowledgeBaseLoader()
        self.document_chunks = loader.load_and_split()
        logger.info(f"Successfully loaded {len(self.document_chunks)} document chunks")

    def retrieve(self, query: str) -> List[Document]:
        """
        Retrieve the most relevant document chunks for the user's query using keyword matching.

        Args:
            query: The user's search query.

        Returns:
            List[Document]: A list of the top-k most relevant document chunks.
        """
        logger.info(f"Retrieving relevant documents for query: {query}")
        
        # Preprocess query for keyword matching
        query_lower = query.lower()
        query_keywords = query_lower.split()
        
        # Score documents based on keyword matches
        scored_documents = []
        for doc in self.document_chunks:
            match_score = 0
            content_lower = doc.page_content.lower()
            
            # Calculate match score based on keyword presence
            for keyword in query_keywords:
                if keyword in content_lower:
                    match_score += 1
            
            # Add to results if there's any match
            if match_score > 0:
                scored_documents.append((match_score, doc))
        
        # Sort by match score (highest first) and take top_k
        scored_documents.sort(key=lambda x: x[0], reverse=True)
        top_results = [doc for (score, doc) in scored_documents[:self.top_k]]
        
        # Fallback: if no matches found, return the first few chunks
        if not top_results:
            logger.warning("No keyword matches found, returning default document chunks")
            top_results = self.document_chunks[:self.top_k]
        
        logger.info(f"Returning {len(top_results)} relevant documents")
        return top_results

    def refresh_index(self) -> None:
        """Reload and reprocess all documents from the knowledge base."""
        logger.info("Refreshing the knowledge base index...")
        self._load_and_split_documents()
        logger.info("Knowledge base refresh completed")