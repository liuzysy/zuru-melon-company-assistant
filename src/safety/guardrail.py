"""Safety and compliance guardrail module for content filtering."""

import logging
from typing import Tuple
from openai import OpenAI

from src.config import settings

logger = logging.getLogger(__name__)


class SafetyGuardrail:
    """Implements content safety checks for both user input and assistant output."""

    def __init__(self) -> None:
        """Initialize the SafetyGuardrail with configuration from settings."""
        self.blocked_keywords = settings.BLOCKED_KEYWORDS
        self.llm_model = settings.LLM_MODEL
        self.client = OpenAI(
            api_key=settings.OPENROUTER_API_KEY,
            base_url=settings.OPENROUTER_BASE_URL,
        )

    def _keyword_check(self, text: str) -> bool:
        """
        Check text for blocked keywords.

        Args:
            text: The text to check.

        Returns:
            bool: True if blocked keywords are found, False otherwise.
        """
        text_lower = text.lower()
        for keyword in self.blocked_keywords:
            if keyword.lower() in text_lower:
                logger.warning(f"Blocked keyword detected: {keyword}")
                return True
        return False

    def _llm_safety_check(self, text: str) -> bool:
        """
        Use LLM to check for safety and policy violations.

        Args:
            text: The text to check.

        Returns:
            bool: True if a violation is detected, False otherwise.
        """
        system_prompt = """You are a content safety moderator for an internal company assistant.
        Your ONLY task is to determine if the user's input violates any of the following strict policies:
        1. Promotes illegal activities, violence, or harm to others
        2. Contains hate speech, discrimination, harassment, or abusive language
        3. Requests or attempts to disclose confidential, proprietary, or private sensitive information
        4. Contains instructions for creating malware, hacking, exploits, or malicious code
        5. Includes sexually explicit or inappropriate content that violates workplace policies

        CRITICAL NOTE: Normal business queries about company policies, coding guidelines, work procedures, internal processes, or general professional questions are ALWAYS SAFE and must be marked as compliant.

        Respond with ONLY the word "YES" if a violation is detected, or ONLY the word "NO" if the content is safe and compliant. Do NOT add any explanation, notes, or extra text.
        """

        try:
            response = self.client.chat.completions.create(
                model=self.llm_model,
                messages=[
                    {"role": "system", "content": system_prompt},
                    {"role": "user", "content": text},
                ],
                temperature=0.0,
                max_tokens=5,
            )
            result = response.choices[0].message.content.strip().upper()
            return result == "YES"
        except Exception as e:
            logger.error(f"LLM safety check failed: {e}")
            return False  # Fail open to avoid blocking valid business queries

    def check_input(self, user_input: str) -> Tuple[bool, str]:
        """
        Check user input for safety and policy violations.

        Args:
            user_input: The user's input text.

        Returns:
            Tuple[bool, str]: (is_safe, message) where is_safe is True if input is safe,
                              False otherwise, and message contains the rejection message.
        """
        if self._keyword_check(user_input):
            return False, "I'm sorry, but I can't assist with that request as it violates our usage policies."

        if self._llm_safety_check(user_input):
            return False, "I'm sorry, but I can't assist with that request as it violates our company's usage policies."

        return True, ""

    def check_output(self, output: str) -> Tuple[bool, str]:
        """
        Check assistant output for safety and policy violations.

        Args:
            output: The assistant's generated output text.

        Returns:
            Tuple[bool, str]: (is_safe, message) where is_safe is True if output is safe,
                              False otherwise, and message contains the rejection message.
        """
        if self._keyword_check(output):
            return False, "I'm sorry, but I can't provide that information as it violates our policies."

        return True, ""