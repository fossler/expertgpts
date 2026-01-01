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
