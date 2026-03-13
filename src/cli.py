"""Interactive CLI interface for the ZURU Company Assistant."""

import sys
import logging
from typing import List, Dict

from src.config import settings
from src.agent.router import AgentRouter, ToolCall
from src.agent.executor import ToolExecutor
from src.safety.guardrail import SafetyGuardrail

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s - %(name)s - %(levelname)s - %(message)s",
    stream=sys.stderr
)

logger = logging.getLogger(__name__)


class AssistantCLI:
    """Interactive CLI for the ZURU Company Assistant."""

    def __init__(self) -> None:
        """Initialize all core components of the assistant."""
        logger.info("Initializing ZURU Company Assistant...")
        self.guardrail = SafetyGuardrail()
        self.router = AgentRouter()
        self.executor = ToolExecutor()
        self.dialogue_history: List[Dict[str, str]] = []
        self.max_history = settings.MAX_DIALOGUE_HISTORY
        logger.info("Assistant initialized successfully")

    def _update_dialogue_history(self, user_message: str, assistant_message: str) -> None:
        """
        Update the dialogue history with new messages, maintaining the maximum length.

        Args:
            user_message: The user's input message.
            assistant_message: The assistant's response message.
        """
        self.dialogue_history.append({"role": "user", "content": user_message})
        self.dialogue_history.append({"role": "assistant", "content": assistant_message})

        # Trim history if it exceeds the maximum length
        if len(self.dialogue_history) > self.max_history * 2:
            self.dialogue_history = self.dialogue_history[-self.max_history * 2:]

    def _clear_history(self) -> None:
        """Clear the entire dialogue history."""
        self.dialogue_history = []
        print("Dialogue history has been cleared.\n")

    def _print_welcome(self) -> None:
        """Print the welcome banner and usage instructions."""
        print("=" * 60)
        print("       ZURU COMPANY ASSISTANT AGENT")
        print("=" * 60)
        print("Type 'quit' or 'exit' to end the session.")
        print("Type 'clear' to clear the dialogue history.")
        print("-" * 60)
        print()

    def _print_progress(self, status: str = "Processing...") -> None:
        """Print a simple progress indicator."""
        sys.stdout.write(f"\r{status}  [------------------------------------]    0%")
        sys.stdout.flush()

    def _print_progress_complete(self, status: str = "Processing...") -> None:
        """Complete the progress indicator."""
        sys.stdout.write(f"\r{status}  [####################################]  100%\n")
        sys.stdout.flush()

    def run(self) -> None:
        """Run the main interactive CLI loop."""
        self._print_welcome()

        while True:
            try:
                # Get user input
                user_input = input("You: ").strip()
                print()

                # Handle exit commands
                if user_input.lower() in ["quit", "exit", "q"]:
                    print("Thank you for using the ZURU Company Assistant. Goodbye!")
                    break

                # Handle clear command
                if user_input.lower() in ["clear", "cls"]:
                    self._clear_history()
                    continue

                # Skip empty input
                if not user_input:
                    continue

                # Step 1: Safety check on user input
                is_safe, rejection_message = self.guardrail.check_input(user_input)
                if not is_safe:
                    print(f"\nAssistant: {rejection_message}\n")
                    self._update_dialogue_history(user_input, rejection_message)
                    continue

                # Step 2: Show progress indicator
                status_text = "Processing..."
                self._print_progress(status_text)

                # Step 3: Agent routing decision
                tool_call: ToolCall = self.router.decide(user_input, self.dialogue_history)

                # Step 4: Execute the selected tool
                tool_result = self.executor.execute(tool_call["name"], tool_call["arguments"])

                # Step 5: Generate final response
                response = self.router.generate_response(
                    user_query=user_input,
                    tool_result=tool_result,
                    tool_name=tool_call["name"],
                    dialogue_history=self.dialogue_history
                )

                # Step 6: Safety check on the generated output
                is_output_safe, output_rejection = self.guardrail.check_output(response)
                if not is_output_safe:
                    final_response = output_rejection
                else:
                    final_response = response

                # Complete progress indicator
                self._print_progress_complete(status_text)

                # Print the final response
                print(f"\nAssistant: {final_response}\n")

                # Update dialogue history
                self._update_dialogue_history(user_input, final_response)

            except KeyboardInterrupt:
                print("\n\nSession interrupted. Type 'quit' to exit.")
                continue
            except Exception as e:
                logger.error(f"Session error: {e}")
                print(f"\nAssistant: I'm sorry, but an unexpected error occurred: {str(e)}\n")


def main():
    """Entry point for the CLI application."""
    try:
        cli = AssistantCLI()
        cli.run()
    except Exception as e:
        logger.critical(f"Failed to start the assistant: {e}")
        print(f"Failed to start the assistant: {e}")
        sys.exit(1)


if __name__ == "__main__":
    main()