"""Agentic router for intent recognition and tool selection."""

import logging
from typing import Dict, List, Optional, TypedDict
from openai import OpenAI

from src.config import settings

logger = logging.getLogger(__name__)


class ToolCall(TypedDict):
    """Type definition for a tool call decision."""
    name: str
    arguments: Dict[str, str]


class AgentRouter:
    """Handles user intent recognition and decides which tool to execute."""

    def __init__(self) -> None:
        """Initialize the AgentRouter with configuration from settings."""
        self.llm_model = settings.LLM_MODEL
        self.temperature = settings.TEMPERATURE
        self.client = OpenAI(
            api_key=settings.OPENROUTER_API_KEY,
            base_url=settings.OPENROUTER_BASE_URL,
        )
        self._init_system_prompt()
        self._init_tools()

    def _init_system_prompt(self) -> None:
        """Initialize the core system prompt for the agent."""
        self.system_prompt = """You are the official ZURU Melon Company Assistant, an intelligent agent designed to help employees with company-related questions and work-related queries.

        Your core responsibilities:
        1. Accurately decide the best tool to answer the user's query using the available tools
        2. Ask clarifying questions if the user's query is ambiguous or lacks critical context
        3. Provide helpful, accurate, and policy-compliant responses based on the tool results
        4. Never make up or fabricate information. If you don't have the information, clearly state that and guide the user to the right resource.

        STRICT Decision Guidelines:
        - ALWAYS use "search_knowledge_base" for ANY questions about ZURU Melon's internal policies, procedures, coding standards, guidelines, company rules, benefits, or internal processes.
        - Use "search_internet" ONLY for questions about current events, general public knowledge, or external information that is NOT specific to ZURU Melon.
        - Use "fallback_to_knowledge" ONLY for simple greetings, conversational queries, or very basic questions that do not require any internal or external information.
        - Use "ask_clarification" ONLY when the query is ambiguous, incomplete, or you need more context to select the right tool.

        Make your decision based solely on the query content and these guidelines.
        """

    def _init_tools(self) -> None:
        """Initialize the official tool definitions for function calling."""
        self.tools = [
            {
                "type": "function",
                "function": {
                    "name": "search_knowledge_base",
                    "description": "Search ZURU Melon's internal company knowledge base for policies, procedures, coding guidelines, and internal company information.",
                    "parameters": {
                        "type": "object",
                        "properties": {
                            "query": {
                                "type": "string",
                                "description": "The search query to look up in the internal knowledge base."
                            }
                        },
                        "required": ["query"]
                    }
                }
            },
            {
                "type": "function",
                "function": {
                    "name": "search_internet",
                    "description": "Search the public internet for current events, general knowledge, or external information not related to ZURU Melon's internal operations.",
                    "parameters": {
                        "type": "object",
                        "properties": {
                            "query": {
                                "type": "string",
                                "description": "The search query to look up on the internet."
                            }
                        },
                        "required": ["query"]
                    }
                }
            },
            {
                "type": "function",
                "function": {
                    "name": "ask_clarification",
                    "description": "Ask the user for clarification when their query is ambiguous, incomplete, or lacks necessary context.",
                    "parameters": {
                        "type": "object",
                        "properties": {
                            "question": {
                                "type": "string",
                                "description": "The clarifying question to ask the user."
                            }
                        },
                        "required": ["question"]
                    }
                }
            },
            {
                "type": "function",
                "function": {
                    "name": "fallback_to_knowledge",
                    "description": "Use for simple greetings, conversational queries, or basic questions that do not require internal or external data.",
                    "parameters": {
                        "type": "object",
                        "properties": {},
                        "required": []
                    }
                }
            }
        ]

    def decide(self, user_query: str, dialogue_history: List[Dict[str, str]]) -> ToolCall:
        """
        Decide which tool to use based on the user's query and dialogue history.

        Args:
            user_query: The user's current input query.
            dialogue_history: A list of previous messages in the conversation.

        Returns:
            ToolCall: A dictionary with the selected tool name and its arguments.
        """
        logger.info(f"Making routing decision for query: {user_query}")

        # Build the message context
        messages = [{"role": "system", "content": self.system_prompt}]
        messages.extend(dialogue_history)
        messages.append({"role": "user", "content": user_query})

        try:
            # Call LLM to make the tool decision
            response = self.client.chat.completions.create(
                model=self.llm_model,
                messages=messages,
                tools=self.tools,
                tool_choice="auto",
                temperature=self.temperature,
            )

            choice = response.choices[0]
            # Check if the LLM decided to call a tool
            if choice.message.tool_calls and len(choice.message.tool_calls) > 0:
                tool_call = choice.message.tool_calls[0]
                # Parse the tool call
                result = ToolCall(
                    name=tool_call.function.name,
                    arguments=eval(tool_call.function.arguments)
                )
                logger.info(f"Routing decision: {result['name']}")
                return result
            else:
                # No tool call, default to fallback
                logger.info("No tool call selected, defaulting to fallback_to_knowledge")
                return ToolCall(name="fallback_to_knowledge", arguments={})

        except Exception as e:
            logger.error(f"Routing decision failed: {e}, defaulting to fallback_to_knowledge")
            return ToolCall(name="fallback_to_knowledge", arguments={})

    def generate_response(
        self,
        user_query: str,
        tool_result: Optional[str],
        tool_name: str,
        dialogue_history: List[Dict[str, str]]
    ) -> str:
        """
        Generate the final natural language response using the tool execution results.

        Args:
            user_query: The user's original query.
            tool_result: The result returned from the executed tool (if any).
            tool_name: The name of the tool that was executed.
            dialogue_history: A list of previous messages in the conversation.

        Returns:
            str: The final formatted response to the user.
        """
        # Build the message context for response generation
        messages = [{"role": "system", "content": self.system_prompt}]
        messages.extend(dialogue_history)

        # Add context from the tool result
        if tool_name == "search_knowledge_base" and tool_result:
            context_prompt = f"""Here is the relevant information retrieved from ZURU Melon's internal knowledge base:

{tool_result}

Use ONLY this information to answer the user's query. If the information does not fully answer the question, clearly state what is available and advise the user to consult the full internal document or the relevant team for complete details. Do NOT make up any information not included in the provided context.
"""
            messages.append({"role": "system", "content": context_prompt})
        elif tool_name == "search_internet" and tool_result:
            context_prompt = f"""Here is the information retrieved from the internet search:

{tool_result}

Use this information to answer the user's query, and clearly note that the information comes from a public internet search.
"""
            messages.append({"role": "system", "content": context_prompt})
        elif tool_name == "ask_clarification" and tool_result:
            # Directly return the clarifying question
            return tool_result

        # Add the user's original query
        messages.append({"role": "user", "content": user_query})

        try:
            # Generate the final response
            response = self.client.chat.completions.create(
                model=self.llm_model,
                messages=messages,
                temperature=self.temperature,
            )
            return response.choices[0].message.content.strip()
        except Exception as e:
            logger.error(f"Response generation failed: {e}")
            return "I'm sorry, but I encountered an error while generating a response. Please try again later."