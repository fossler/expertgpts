"""Abstract base class for LLM providers.

This module defines the interface that all LLM provider clients must implement,
ensuring consistency across different providers (DeepSeek, OpenAI, Z.AI, etc.).
"""

from abc import ABC, abstractmethod
from typing import List, Dict, Generator, Optional, Tuple
from utils.types import Message, ThinkingLevelType
from utils.exceptions import APIError


class BaseLLMClient(ABC):
    """Abstract base class for LLM provider clients.

    All LLM provider implementations must inherit from this class and
    implement the required methods. This ensures a consistent interface
    across all providers.
    """

    def __init__(self, provider: str, api_key: str, base_url: str):
        """Initialize the LLM client.

        Args:
            provider: Provider key (e.g., "deepseek", "openai", "zai")
            api_key: API key for the provider
            base_url: Base URL for the provider's API

        Raises:
            ValueError: If api_key is empty
        """
        if not api_key:
            raise ValueError(f"{provider.upper()} API key must be provided")

        self.provider = provider
        self.api_key = api_key
        self.base_url = base_url

    @abstractmethod
    def chat(
        self,
        messages: List[Dict[str, str]],
        temperature: float = 1.0,
        model: Optional[str] = None,
        system_prompt: Optional[str] = None,
        thinking_level: Optional[str] = None,
        **kwargs
    ) -> str:
        """Send a non-streaming chat request to the LLM provider.

        Args:
            messages: List of message dictionaries with 'role' and 'content'
            temperature: Sampling temperature (0.0-2.0)
            model: Model to use (if None, uses provider default)
            system_prompt: Optional system prompt to prepend
            thinking_level: Thinking/reasoning effort level
            **kwargs: Additional provider-specific parameters

        Returns:
            str: Assistant's response text

        Raises:
            APIError: If the API call fails
        """
        pass

    @abstractmethod
    def chat_stream(
        self,
        messages: List[Dict[str, str]],
        temperature: float = 1.0,
        model: Optional[str] = None,
        system_prompt: Optional[str] = None,
        thinking_level: Optional[str] = None,
        **kwargs
    ) -> Generator[str, None, None]:
        """Send a streaming chat request to the LLM provider.

        Args:
            messages: List of message dictionaries with 'role' and 'content'
            temperature: Sampling temperature (0.0-2.0)
            model: Model to use (if None, uses provider default)
            system_prompt: Optional system prompt to prepend
            thinking_level: Thinking/reasoning effort level
            **kwargs: Additional provider-specific parameters

        Yields:
            str: Chunks of the assistant's response as they arrive

        Raises:
            APIError: If the API call fails
        """
        pass

    @abstractmethod
    def count_tokens(self, text: str, encoding: str = "cl100k_base") -> int:
        """Count the number of tokens in a text string.

        Args:
            text: The text to count tokens in
            encoding: The token encoding to use

        Returns:
            int: The number of tokens
        """
        pass

    @abstractmethod
    def count_messages_tokens(
        self,
        messages: List[Dict[str, str]],
        encoding: str = "cl100k_base"
    ) -> int:
        """Count the total tokens in a list of messages.

        Args:
            messages: List of message dictionaries
            encoding: The token encoding to use

        Returns:
            int: The total number of tokens
        """
        pass

    @abstractmethod
    def get_max_tokens(self, model: str) -> int:
        """Get the maximum context tokens for a model.

        Args:
            model: The model identifier

        Returns:
            int: Maximum context length
        """
        pass

    def get_default_model(self) -> str:
        """Get the default model for this provider.

        Returns:
            str: Default model identifier
        """
        # Default implementation - can be overridden
        from utils.constants import get_default_model_for_provider
        return get_default_model_for_provider(self.provider)

    def prepare_thinking_param(
        self,
        model: str,
        thinking_level: Optional[str] = None
    ) -> Tuple[Dict[str, Dict], Dict[str, str]]:
        """Prepare provider-specific thinking/reasoning parameters.

        Args:
            model: Model identifier
            thinking_level: Thinking effort level ("none", "low", "medium", "high", "xhigh")

        Returns:
            tuple: (extra_body_dict, direct_params_dict) - Two dictionaries for different
                   ways of passing parameters to the API

        Note:
            Different providers use different formats for thinking/reasoning:
            - OpenAI: Uses "reasoning_effort" as a direct parameter
            - DeepSeek: Uses "thinking" in extra_body
            - Z.AI: Uses "thinking" in extra_body
        """
        # Default implementation - should be overridden by providers
        if not thinking_level or thinking_level == "none":
            return {}, {}

        # Provider-specific implementations should override this
        return {}, {}

    def validate_api_key_format(self, api_key: str) -> bool:
        """Validate the format of an API key for this provider.

        Args:
            api_key: The API key to validate

        Returns:
            bool: True if the format is valid, False otherwise
        """
        # Default implementation - just check it's not empty
        return bool(api_key and api_key.strip())

    def get_provider_info(self) -> Dict[str, str]:
        """Get information about this provider.

        Returns:
            dict: Provider information including name, base_url, etc.
        """
        from utils.constants import get_provider_config
        return get_provider_config(self.provider)

    def __repr__(self) -> str:
        """String representation of the client."""
        return f"{self.__class__.__name__}(provider='{self.provider}')"
