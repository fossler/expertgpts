"""DeepSeek API client for chat functionality."""

from typing import List, Dict, Optional
from dataclasses import dataclass


try:
    from openai import OpenAI
except ImportError:
    raise ImportError(
        "OpenAI package is required. Install with: pip install openai"
    )


@dataclass
class Message:
    """Represents a chat message."""
    role: str
    content: str


class DeepSeekClient:
    """Client for interacting with DeepSeek API."""

    def __init__(self, api_key: str):
        """Initialize the DeepSeek client.

        Args:
            api_key: DeepSeek API key (required)

        Raises:
            ValueError: If api_key is None or empty
        """
        if not api_key:
            raise ValueError(
                "DeepSeek API key must be provided as a parameter"
            )

        # DeepSeek uses OpenAI-compatible API
        self.client = OpenAI(
            api_key=api_key,
            base_url="https://api.deepseek.com"
        )

    def chat(
        self,
        messages: List[Dict[str, str]],
        temperature: float = 1.0,
        model: str = "deepseek-chat",
        system_prompt: Optional[str] = None,
    ) -> str:
        """Send a chat request to DeepSeek API.

        Args:
            messages: List of message dictionaries with 'role' and 'content'
            temperature: Sampling temperature (0.0-2.0)
            model: Model to use (default: deepseek-chat)
            system_prompt: Optional system prompt to prepend

        Returns:
            Assistant's response text
        """
        # Prepare messages with system prompt
        prepared_messages = []

        if system_prompt:
            prepared_messages.append({
                "role": "system",
                "content": system_prompt
            })

        prepared_messages.extend(messages)

        try:
            response = self.client.chat.completions.create(
                model=model,
                messages=prepared_messages,
                temperature=temperature,
                stream=False,
            )

            return response.choices[0].message.content

        except Exception as e:
            raise Exception(f"Error calling DeepSeek API: {str(e)}")

    def chat_stream(
        self,
        messages: List[Dict[str, str]],
        temperature: float = 1.0,
        model: str = "deepseek-chat",
        system_prompt: Optional[str] = None,
    ):
        """Send a streaming chat request to DeepSeek API.

        Args:
            messages: List of message dictionaries with 'role' and 'content'
            temperature: Sampling temperature (0.0-2.0)
            model: Model to use (default: deepseek-chat)
            system_prompt: Optional system prompt to prepend

        Yields:
            Chunks of the assistant's response
        """
        # Prepare messages with system prompt
        prepared_messages = []

        if system_prompt:
            prepared_messages.append({
                "role": "system",
                "content": system_prompt
            })

        prepared_messages.extend(messages)

        try:
            stream = self.client.chat.completions.create(
                model=model,
                messages=prepared_messages,
                temperature=temperature,
                stream=True,
            )

            for chunk in stream:
                if chunk.choices[0].delta.content:
                    yield chunk.choices[0].delta.content

        except Exception as e:
            raise Exception(f"Error calling DeepSeek API: {str(e)}")

    def generate_system_prompt(
        self,
        expert_name: str,
        description: str,
        temperature: float = 1.0,
        model: str = "deepseek-chat",
    ) -> str:
        """Generate an AI-powered system prompt for an expert.

        Uses DeepSeek API to create a customized system prompt based on
        the expert's name and description. Falls back to template on error.

        Args:
            expert_name: Name of the expert
            description: Description of the expert's domain
            temperature: Temperature for generation (default: 1.0)
            model: Model to use (default: deepseek-chat)

        Returns:
            Generated system prompt, or fallback template if API call fails
        """
        # Generation prompt - instructions for DeepSeek API
        generation_prompt = f"""Create a system prompt, the output must be in Markdown:
You are {expert_name}, a domain-specific expert AI assistant.

Role description:
{description}

## Guidelines
- Provide accurate, expert-level information in your domain
- If you're unsure about something, acknowledge it honestly
- Use clear, professional language appropriate for your domain
- Ask clarifying questions when needed to provide better assistance
- Provide practical, actionable advice when applicable

Remember: You are a specialized expert. Stay within your domain of expertise and provide high-quality, accurate information."""

        # Fallback template - clean system prompt for direct use
        fallback_template = f"""You are {expert_name}, a domain-specific expert AI assistant.

{description}

## Guidelines
- Provide accurate, expert-level information in your domain
- If you're unsure about something, acknowledge it honestly
- Use clear, professional language appropriate for your domain
- Ask clarifying questions when needed to provide better assistance
- Provide practical, actionable advice when applicable

Remember: You are a specialized expert. Stay within your domain of expertise and provide high-quality, accurate information."""

        try:
            # Ask DeepSeek to generate an enhanced system prompt
            response = self.chat(
                messages=[{
                    "role": "user",
                    "content": generation_prompt
                }],
                temperature=temperature,
                model=model,
            )

            return response.strip()

        except Exception:
            # Silent fallback - return the clean template
            return fallback_template
