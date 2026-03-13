"""Tool execution module for the agent."""

import logging
from typing import List, Dict, Optional
from langchain_core.documents import Document

from src.config import settings
from src.knowledge_base.retriever import KnowledgeBaseRetriever

logger = logging.getLogger(__name__)


class ToolExecutor:
    """Executes the tools selected by the agent router."""

    def __init__(self) -> None:
        """Initialize the ToolExecutor with required tool instances."""
        self.kb_retriever = KnowledgeBaseRetriever()
        self.search_client = None
        # Initialize internet search only if Serper API key is configured
        if settings.SERPER_API_KEY:
            try:
                from langchain_community.utilities import GoogleSerperAPIWrapper
                self.search_client = GoogleSerperAPIWrapper(serper_api_key=settings.SERPER_API_KEY)
                logger.info("Internet search enabled with Serper API")
            except ImportError:
                logger.warning("langchain-community not installed, internet search is disabled")

    def execute(self, tool_name: str, arguments: Dict[str, str]) -> Optional[str]:
        """
        Execute the specified tool with the given arguments.

        Args:
            tool_name: The name of the tool to execute.
            arguments: The arguments for the selected tool.

        Returns:
            Optional[str]: The formatted result of the tool execution, or None if not applicable.
        """
        logger.info(f"Executing tool: {tool_name}")

        try:
            if tool_name == "search_knowledge_base":
                return self._search_knowledge_base(arguments.get("query", ""))
            elif tool_name == "search_internet":
                return self._search_internet(arguments.get("query", ""))
            elif tool_name == "ask_clarification":
                return arguments.get("question", "Could you please provide more details to help me assist you better?")
            elif tool_name == "fallback_to_knowledge":
                return None
            else:
                logger.warning(f"Unknown tool requested: {tool_name}")
                return None
        except Exception as e:
            logger.error(f"Tool execution failed for {tool_name}: {e}")
            return f"An error occurred while executing the tool: {str(e)}"

    def _search_knowledge_base(self, query: str) -> str:
        """
        Search the internal knowledge base and format the results.

        Args:
            query: The search query.

        Returns:
            str: Formatted search results from the knowledge base.
        """
        if not query:
            return "No query provided for the knowledge base search."

        documents = self.kb_retriever.retrieve(query)
        if not documents:
            return "No relevant information was found in the company knowledge base."

        # Format the results for the LLM
        formatted_results = []
        for i, doc in enumerate(documents, 1):
            source = doc.metadata.get("source", "Unknown Document")
            formatted_results.append(f"--- Document {i} | Source: {source} ---\n{doc.page_content}")

        return "\n\n".join(formatted_results)

    def _search_internet(self, query: str) -> str:
        """
        Search the public internet and format the results.

        Args:
            query: The search query.

        Returns:
            str: Formatted search results from the internet.
        """
        if not self.search_client:
            return "Internet search is currently disabled (no valid Serper API key configured)."

        if not query:
            return "No query provided for the internet search."

        try:
            search_results = self.search_client.results(query)
            organic_results = search_results.get("organic", [])

            if not organic_results:
                return "No relevant information was found from the internet search."

            # Format the top 3 results
            formatted_results = []
            for i, result in enumerate(organic_results[:3], 1):
                title = result.get("title", "No Title")
                link = result.get("link", "")
                snippet = result.get("snippet", "No content available")
                formatted_results.append(f"--- Web Result {i}: {title} ---\nSource: {link}\n{snippet}")

            return "\n\n".join(formatted_results)
        except Exception as e:
            logger.error(f"Internet search failed: {e}")
            return "Failed to retrieve results from the internet search."