"""Document loading and splitting module for the knowledge base."""

import os
import logging
from typing import List
from langchain_core.documents import Document
from langchain_text_splitters import RecursiveCharacterTextSplitter
from langchain_community.document_loaders import DirectoryLoader, TextLoader

from src.config import settings

logger = logging.getLogger(__name__)


class KnowledgeBaseLoader:
    """Loads and splits documents from the company knowledge base directory."""

    def __init__(self) -> None:
        """Initialize the KnowledgeBaseLoader with configuration from settings."""
        self.kb_path = settings.KNOWLEDGE_BASE_PATH
        self.chunk_size = settings.CHUNK_SIZE
        self.chunk_overlap = settings.CHUNK_OVERLAP
        self.text_splitter = self._initialize_text_splitter()

    def _initialize_text_splitter(self) -> RecursiveCharacterTextSplitter:
        """
        Initialize the text splitter for document chunking.

        Returns:
            RecursiveCharacterTextSplitter: An initialized text splitter.
        """
        return RecursiveCharacterTextSplitter(
            chunk_size=self.chunk_size,
            chunk_overlap=self.chunk_overlap,
            separators=["\n\n", "\n", ". ", " ", ""],
        )

    def load_documents(self) -> List[Document]:
        """
        Load all supported documents from the knowledge base directory.

        Returns:
            List[Document]: A list of loaded Document objects.
        """
        logger.info(f"Loading documents from {self.kb_path}")
        
        if not os.path.exists(self.kb_path):
            logger.warning(f"Knowledge base directory {self.kb_path} does not exist")
            return []
        
        # Load all text-based files using TextLoader (works for .md and .txt)
        loader = DirectoryLoader(
            self.kb_path,
            glob="**/*",
            loader_cls=TextLoader,
            loader_kwargs={"autodetect_encoding": True},
            silent_errors=True
        )

        all_documents = loader.load()
        logger.info(f"Successfully loaded {len(all_documents)} documents")
        return all_documents

    def load_and_split(self) -> List[Document]:
        """
        Load all documents and split them into chunks for retrieval.

        Returns:
            List[Document]: A list of split document chunks.
        """
        documents = self.load_documents()
        logger.info(f"Splitting {len(documents)} documents into chunks")
        chunks = self.text_splitter.split_documents(documents)
        logger.info(f"Created {len(chunks)} document chunks")
        return chunks