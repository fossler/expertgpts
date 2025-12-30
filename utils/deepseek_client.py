"""DeepSeek API client for chat functionality."""

import os
from pathlib import Path
from typing import List, Dict, Optional
from dataclasses import dataclass


# Load environment variables from .env file if it exists
env_path = Path(__file__).parent.parent / ".env"
if env_path.exists():
    try:
        from dotenv import load_dotenv
        load_dotenv(env_path)
    except ImportError:
        pass  # python-dotenv not installed, continue without it


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

    def __init__(self, api_key: Optional[str] = None):
        """Initialize the DeepSeek client.

        Args:
            api_key: DeepSeek API key. If None, will try to get from environment
        """
        if api_key is None:
            api_key = os.getenv("DEEPSEEK_API_KEY")

        if not api_key:
            raise ValueError(
                "DeepSeek API key must be provided either as parameter or "
                "through DEEPSEEK_API_KEY environment variable"
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
