"""Centralized validation utilities for ExpertGPTs.

This module provides all input validation and sanitization functions used
throughout the application. Having validation in one place ensures
consistency and makes maintenance easier.
"""

import re
from typing import Optional, Literal, List
from utils.constants import LLM_PROVIDERS


class ValidationError(Exception):
    """Raised when validation fails."""
    pass


# Expert name validation
def validate_expert_name(name: str) -> str:
    """Validate and sanitize an expert name.

    Args:
        name: The expert name to validate

    Returns:
        str: The sanitized expert name

    Raises:
        ValidationError: If the name is invalid

    Validation rules:
    - Must be 1-100 characters
    - Must not be empty or just whitespace
    - Must not contain special shell characters (&|`$();)
    - Must not contain HTML/JavaScript tags (basic check)
    """
    if not name or not name.strip():
        raise ValidationError("Expert name cannot be empty")

    if len(name) > 100:
        raise ValidationError("Expert name must be 100 characters or less")

    if len(name.strip()) < 2:
        raise ValidationError("Expert name must be at least 2 characters")

    # Remove potentially dangerous characters
    sanitized = re.sub(r'[;&|`$()]', '', name)

    # Basic HTML tag check
    if re.search(r'<[^>]+>', sanitized):
        raise ValidationError("Expert name cannot contain HTML tags")

    return sanitized.strip()


def validate_description(description: str) -> str:
    """Validate and sanitize an expert description.

    Args:
        description: The description to validate

    Returns:
        str: The sanitized description

    Raises:
        ValidationError: If the description is invalid

    Validation rules:
    - Must be 10-1000 characters
    - Must not be empty or just whitespace
    """
    if not description or not description.strip():
        raise ValidationError("Description cannot be empty")

    if len(description) > 1000:
        raise ValidationError("Description must be 1000 characters or less")

    if len(description.strip()) < 10:
        raise ValidationError("Description must be at least 10 characters")

    return description.strip()


def validate_temperature(temperature: float) -> float:
    """Validate a temperature value.

    Args:
        temperature: The temperature to validate (0.0-2.0)

    Returns:
        float: The validated temperature

    Raises:
        ValidationError: If the temperature is out of range
    """
    if not isinstance(temperature, (int, float)):
        raise ValidationError("Temperature must be a number")

    if not 0.0 <= temperature <= 2.0:
        raise ValidationError("Temperature must be between 0.0 and 2.0")

    return float(temperature)


def validate_provider(provider: str) -> str:
    """Validate an LLM provider.

    Args:
        provider: The provider key to validate

    Returns:
        str: The validated provider key

    Raises:
        ValidationError: If the provider is not supported
    """
    if provider not in LLM_PROVIDERS:
        available = list(LLM_PROVIDERS.keys())
        raise ValidationError(
            f"Unknown provider: {provider}. Available providers: {available}"
        )

    return provider


def validate_model_for_provider(provider: str, model: str) -> str:
    """Validate that a model is available for a provider.

    Args:
        provider: The provider key
        model: The model ID to validate

    Returns:
        str: The validated model ID

    Raises:
        ValidationError: If the model is not available for the provider
    """
    # First validate the provider
    validate_provider(provider)

    # Check if model exists for this provider
    if model not in LLM_PROVIDERS[provider]["models"]:
        available = list(LLM_PROVIDERS[provider]["models"].keys())
        raise ValidationError(
            f"Unknown model: {model} for provider {provider}. Available: {available}"
        )

    return model


def validate_thinking_level(provider: str, thinking_level: str) -> str:
    """Validate a thinking/reasoning level for a provider.

    Args:
        provider: The provider key
        thinking_level: The thinking level to validate

    Returns:
        str: The validated thinking level

    Raises:
        ValidationError: If the thinking level is invalid for the provider

    Note:
        OpenAI supports: "none", "low", "medium", "high", "xhigh"
        Other providers: "none" or any non-empty value (enabled/disabled)
    """
    valid_levels = ["none", "low", "medium", "high", "xhigh"]

    if thinking_level == "none":
        return "none"

    # OpenAI has specific effort levels
    if provider == "openai":
        if thinking_level not in valid_levels:
            raise ValidationError(
                f"Invalid thinking level for OpenAI: {thinking_level}. "
                f"Must be one of: {valid_levels}"
            )
        return thinking_level

    # For other providers, just ensure it's not "none"
    if thinking_level in valid_levels:
        return thinking_level

    # Accept any non-empty string for other providers
    if thinking_level and thinking_level.strip():
        return thinking_level

    return "none"


def validate_api_key(api_key: str, provider: str) -> str:
    """Validate an API key format for a provider.

    Args:
        api_key: The API key to validate
        provider: The provider key

    Returns:
        str: The validated API key

    Raises:
        ValidationError: If the API key format is invalid

    Note:
        This is a basic format check. The actual validation happens
        when the API key is used to make requests.
    """
    if not api_key or not api_key.strip():
        raise ValidationError(f"{provider.upper()} API key cannot be empty")

    api_key = api_key.strip()

    # Basic format validation for common patterns
    patterns = {
        "deepseek": r'^sk-[a-zA-Z0-9]{20,}$',
        "openai": r'^sk-[a-zA-Z0-9\-]{20,}$',
        "zai": r'^[a-zA-Z0-9]{20,}$'
    }

    pattern = patterns.get(provider)
    if pattern and not re.match(pattern, api_key):
        raise ValidationError(
            f"Invalid {provider.upper()} API key format. "
            f"Expected format for {provider.upper()} API keys."
        )

    return api_key


def validate_system_prompt(system_prompt: Optional[str]) -> Optional[str]:
    """Validate a system prompt.

    Args:
        system_prompt: The system prompt to validate (can be None)

    Returns:
        Optional[str]: The validated system prompt or None

    Raises:
        ValidationError: If the system prompt is invalid
    """
    if system_prompt is None:
        return None

    if not system_prompt.strip():
        return None

    if len(system_prompt) > 5000:
        raise ValidationError("System prompt must be 5000 characters or less")

    return system_prompt.strip()


def validate_page_number(page_number: int) -> int:
    """Validate a page number.

    Args:
        page_number: The page number to validate

    Returns:
        int: The validated page number

    Raises:
        ValidationError: If the page number is invalid

    Note:
        Page numbers must be between 1001 and 9997 (1000 is Home, 9998 is Settings, 9999 is Help)
    """
    if not isinstance(page_number, int):
        raise ValidationError("Page number must be an integer")

    if not (1001 <= page_number <= 9997):
        raise ValidationError(
            f"Page number must be between 1001 and 9997 (got {page_number}). "
            "Note: 1000 is reserved for Home, 9998 for Settings, 9999 for Help."
        )

    return page_number


def sanitize_user_input(text: str, max_length: int = 1000) -> str:
    """Sanitize user input to prevent XSS and injection attacks.

    Args:
        text: The user input to sanitize
        max_length: Maximum allowed length

    Returns:
        str: The sanitized text

    Raises:
        ValidationError: If the input is too long or invalid
    """
    if not text:
        return ""

    if len(text) > max_length:
        raise ValidationError(f"Input too long (max {max_length} characters)")

    # Remove potentially dangerous shell characters
    sanitized = re.sub(r'[;&|`$()]', '', text)

    # Escape HTML special characters
    html_escape_map = {
        '&': '&amp;',
        '<': '&lt;',
        '>': '&gt;',
        '"': '&quot;',
        "'": '&#x27;'
    }

    for char, escaped in html_escape_map.items():
        sanitized = sanitized.replace(char, escaped)

    return sanitized.strip()


def validate_expert_config(config: dict) -> dict:
    """Validate a complete expert configuration.

    Args:
        config: The configuration dictionary to validate

    Returns:
        dict: The validated configuration

    Raises:
        ValidationError: If any part of the configuration is invalid
    """
    required_fields = ["expert_id", "expert_name", "description"]

    # Check required fields
    for field in required_fields:
        if field not in config:
            raise ValidationError(f"Missing required field: {field}")

    # Validate individual fields
    config["expert_name"] = validate_expert_name(config["expert_name"])
    config["description"] = validate_description(config["description"])

    if "temperature" in config:
        config["temperature"] = validate_temperature(config["temperature"])

    if "provider" in config:
        config["provider"] = validate_provider(config["provider"])

        # Validate model if provider is specified
        if "model" in config:
            config["model"] = validate_model_for_provider(
                config["provider"],
                config["model"]
            )

    if "thinking_level" in config:
        provider = config.get("provider", "deepseek")
        config["thinking_level"] = validate_thinking_level(
            provider,
            config["thinking_level"]
        )

    if "system_prompt" in config:
        config["system_prompt"] = validate_system_prompt(config["system_prompt"])

    if "page_number" in config:
        config["page_number"] = validate_page_number(config["page_number"])

    return config
