"""Generic LLM client supporting multiple providers.

This module provides a unified interface for interacting with multiple
LLM providers (DeepSeek, OpenAI, Z.AI) through the OpenAI-compatible API.
"""

from typing import List, Dict, Optional
from dataclasses import dataclass


try:
    from openai import OpenAI
except ImportError:
    raise ImportError(
        "OpenAI package is required. Install with: pip install openai"
    )

from lib.shared.constants import (
    get_provider_config,
    get_model_config,
    get_provider_base_url,
    SYSTEM_PROMPT_TEMPLATE,
)
from lib.i18n.i18n import i18n


@dataclass
class Message:
    """Represents a chat message."""
    role: str
    content: str


class LLMClient:
    """Generic client for interacting with multiple LLM providers.

    Supports DeepSeek, OpenAI, and Z.AI through their OpenAI-compatible APIs.
    Each provider may have different thinking/reasoning parameter formats.
    """

    def __init__(self, provider: str, api_key: str):
        """Initialize the LLM client for a specific provider.

        Args:
            provider: Provider key (e.g., "deepseek", "openai", "zai")
            api_key: API key for the provider

        Raises:
            ValueError: If provider is not found or api_key is empty
        """
        if not api_key:
            raise ValueError(
                f"{provider.upper()} API key must be provided as a parameter"
            )

        self.provider = provider
        self.config = get_provider_config(provider)
        self.base_url = get_provider_base_url(provider)

        # Initialize OpenAI-compatible client with provider-specific base URL
        self.client = OpenAI(
            api_key=api_key,
            base_url=self.base_url
        )

    def _prepare_thinking_param(self, model: str, thinking_level: str = None) -> dict:
        """Prepare provider-specific thinking/reasoning parameter.

        Args:
            model: Model ID
            thinking_level: Effort level ("none", "low", "medium", "high", "xhigh")

        Returns:
            tuple: (extra_body_dict, direct_params_dict) - Two dictionaries for different
                   ways of passing parameters to the API
        """
        # No thinking specified or explicitly set to none
        if not thinking_level or thinking_level == "none":
            return {}, {}

        # OpenAI: use reasoning effort parameter (direct parameter, not in extra_body)
        if self.provider == "openai":
            # Map our effort levels to OpenAI's reasoning_effort values
            # OpenAI accepts: "low", "medium", "high"
            if thinking_level in ["low", "medium", "high"]:
                # reasoning_effort is a direct parameter for OpenAI
                return {}, {"reasoning_effort": thinking_level}
            elif thinking_level == "xhigh":
                # Map "xhigh" to "high" for OpenAI
                return {}, {"reasoning_effort": "high"}
            else:
                return {}, {}

        # Z.AI: use thinking type parameter (enabled/disabled)
        if self.provider == "zai":
            # Z.AI uses: {"thinking": {"type": "enabled"}} or {"type": "disabled"}
            # Any thinking_level other than "none" means enabled
            return {"thinking": {"type": "enabled"}}, {}

        # DeepSeek: use thinking type parameter from model config (goes in extra_body)
        if self.provider == "deepseek":
            model_config = get_model_config(self.provider, model)
            thinking_param = model_config.get("thinking_param", {})
            return thinking_param, {}

        # Other providers: return empty for now
        return {}, {}

    def chat(
        self,
        messages: List[Dict[str, str]],
        temperature: float = 1.0,
        model: str = None,
        system_prompt: Optional[str] = None,
        thinking_level: str = None,
    ) -> str:
        """Send a non-streaming chat request to the LLM provider.

        Args:
            messages: List of message dictionaries with 'role' and 'content'
            temperature: Sampling temperature (0.0-2.0)
            model: Model to use (if None, uses provider default)
            system_prompt: Optional system prompt to prepend
            thinking_level: Thinking/reasoning effort level (OpenAI: "none"|"low"|"medium"|"high"|"xhigh")

        Returns:
            Assistant's response text

        Raises:
            Exception: If API call fails
        """
        # Use provider default model if not specified
        if model is None:
            model = self.config["default_model"]

        # Prepare messages with system prompt
        prepared_messages = []

        if system_prompt:
            prepared_messages.append({
                "role": "system",
                "content": system_prompt
            })

        prepared_messages.extend(messages)

        # Get thinking parameter (returns tuple: extra_body_dict, direct_params_dict)
        extra_body_params, direct_params = self._prepare_thinking_param(model, thinking_level)

        # Build API call parameters
        api_params = {
            "model": model,
            "messages": prepared_messages,
            "temperature": temperature,
            "stream": False,
        }

        # Add direct parameters (like reasoning_effort for OpenAI)
        api_params.update(direct_params)

        # Add extra_body for provider-specific parameters (like thinking for DeepSeek)
        if extra_body_params:
            api_params["extra_body"] = extra_body_params

        try:
            response = self.client.chat.completions.create(**api_params)
            return response.choices[0].message.content

        except Exception as e:
            raise Exception(f"Error calling {self.config['name']} API: {str(e)}")

    def chat_stream(
        self,
        messages: List[Dict[str, str]],
        temperature: float = 1.0,
        model: str = None,
        system_prompt: Optional[str] = None,
        thinking_level: str = None,
    ):
        """Send a streaming chat request to the LLM provider.

        Args:
            messages: List of message dictionaries with 'role' and 'content'
            temperature: Sampling temperature (0.0-2.0)
            model: Model to use (if None, uses provider default)
            system_prompt: Optional system prompt to prepend
            thinking_level: Thinking/reasoning effort level (OpenAI: "none"|"low"|"medium"|"high"|"xhigh")

        Yields:
            Chunks of the assistant's response

        Raises:
            Exception: If API call fails
        """
        # Use provider default model if not specified
        if model is None:
            model = self.config["default_model"]

        # Prepare messages with system prompt
        prepared_messages = []

        if system_prompt:
            prepared_messages.append({
                "role": "system",
                "content": system_prompt
            })

        prepared_messages.extend(messages)

        # Get thinking parameter (returns tuple: extra_body_dict, direct_params_dict)
        extra_body_params, direct_params = self._prepare_thinking_param(model, thinking_level)

        # Build API call parameters
        api_params = {
            "model": model,
            "messages": prepared_messages,
            "temperature": temperature,
            "stream": True,
        }

        # Add direct parameters (like reasoning_effort for OpenAI)
        api_params.update(direct_params)

        # Add extra_body for provider-specific parameters (like thinking for DeepSeek)
        if extra_body_params:
            api_params["extra_body"] = extra_body_params

        try:
            stream = self.client.chat.completions.create(**api_params)

            for chunk in stream:
                if chunk.choices[0].delta.content:
                    yield chunk.choices[0].delta.content

        except Exception as e:
            raise Exception(f"Error calling {self.config['name']} API: {str(e)}")

    def generate_system_prompt(
        self,
        expert_name: str,
        description: str,
        temperature: float = 1.0,
        model: str = None,
    ) -> str:
        """Generate an AI-powered system prompt for an expert.

        Uses the LLM provider's API to create a customized system prompt
        based on the expert's name and description. Falls back to template
        on error.

        Args:
            expert_name: Name of the expert
            description: Description of the expert's domain
            temperature: Temperature for generation (default: 1.0)
            model: Model to use (if None, uses provider default)

        Returns:
            Generated system prompt, or fallback template if API call fails
        """
        # Use provider default model if not specified
        if model is None:
            model = self.config["default_model"]

        # Get language prefix to instruct LLM on response language
        language_prefix = i18n.get_language_prefix()

        # Generation prompt - instructions for LLM
        generation_prompt = f"""{language_prefix}
{SYSTEM_PROMPT_TEMPLATE.format(expert_name=expert_name, description=description)}"""

        # Fallback template - clean system prompt for direct use
        fallback_template = SYSTEM_PROMPT_TEMPLATE.format(
            expert_name=expert_name,
            description=description
        )

        try:
            # Ask LLM to generate an enhanced system prompt
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
