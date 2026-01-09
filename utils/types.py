"""Type definitions and schemas for ExpertGPTs.

This module provides TypedDict schemas and type aliases used throughout
the application for better type safety and IDE support.
"""

from typing import TypedDict, List, Dict, Optional, Literal, Union
from enum import Enum


class ThinkingLevel(str, Enum):
    """Standard thinking/reasoning levels for LLM providers.

    OpenAI supports specific effort levels, while other providers
    use simpler enabled/disabled models.
    """
    NONE = "none"
    LOW = "low"
    MEDIUM = "medium"
    HIGH = "high"
    XHIGH = "xhigh"


class Provider(str, Enum):
    """Supported LLM providers."""
    DEEPSEEK = "deepseek"
    OPENAI = "openai"
    ZAI = "zai"


class Message(TypedDict):
    """A chat message."""
    role: str
    content: str


class ExpertConfig(TypedDict, total=False):
    """Configuration for an expert agent.

    All fields are optional to allow partial updates.
    """
    expert_id: str
    expert_name: str
    description: str
    temperature: float
    provider: str
    model: str
    system_prompt: Optional[str]
    thinking_level: str
    page_number: Optional[int]
    metadata: Dict[str, Union[str, int, float, bool]]


class ExpertInfo(TypedDict):
    """Basic information about an expert."""
    expert_id: str
    expert_name: str
    description: str
    filename: str


class PageInfo(TypedDict):
    """Information about a page file."""
    filename: str
    expert_name: str
    page_number: int


class ProviderConfig(TypedDict):
    """Configuration for an LLM provider."""
    name: str
    api_key_env: str
    base_url: str
    default_model: str
    icon_path: str
    models: Dict[str, "ModelConfig"]


class ModelConfig(TypedDict):
    """Configuration for a specific model."""
    display_name: str
    max_tokens: int
    thinking_param: Dict[str, Dict[str, str]]


class TokenUsage(TypedDict):
    """Token usage information."""
    prompt_tokens: int
    completion_tokens: int
    total_tokens: int


class ChatState(TypedDict):
    """State of a chat conversation."""
    messages: List[Message]
    provider: str
    model: str
    temperature: float
    thinking_enabled: bool


class CacheStats(TypedDict):
    """Cache performance statistics."""
    total_clients: int
    providers: Dict[str, int]


class ValidationResult(TypedDict):
    """Result of a validation operation."""
    valid: bool
    errors: List[str]
    warnings: List[str]


# Type aliases for common patterns
ExpertID = str
PageNumber = int
Temperature = float
PromptTokens = int
CompletionTokens = int
TotalTokens = int
MessagesList = List[Message]
ProviderKey = Literal["deepseek", "openai", "zai"]
ModelID = str
ApiKey = str
SystemPrompt = str
ThinkingLevelType = Literal["none", "low", "medium", "high", "xhigh"]
