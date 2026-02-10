"""Shared utilities and constants."""

# Core utilities
from lib.shared.constants import (
    LLM_PROVIDERS,
    SYSTEM_PROMPT_TEMPLATE,
    EXAMPLE_EXPERTS_COUNT,
    CONFIG_CACHE_TTL,
    CONTEXT_USAGE_ALERT_THRESHOLD,
    CONTEXT_USAGE_WARNING_THRESHOLD,
    CONTEXT_USAGE_SAFE_THRESHOLD,
    CONTEXT_USAGE_COLORS,
    EXPERT_BEHAVIOR_DOCS,
    get_provider_config,
    get_model_config,
    get_provider_base_url,
    get_provider_display_name,
    get_model_display_name,
    get_max_tokens,
    get_default_model_for_provider,
    get_expert_behavior_docs,
    get_expert_behavior_docs_edit,
    get_provider_links,
    get_provider_avatar,
)
from lib.shared.helpers import sanitize_name, translate_expert_name, validate_expert_name, validate_api_key
from lib.shared.file_ops import (
    get_project_root,
    get_streamlit_path,
    safe_path_join,
    validate_cwd,
    set_secure_permissions,
    ensure_file_exists,
    ensure_directory_exists,
)
from lib.shared.format_ops import (
    read_toml,
    write_toml,
    read_yaml,
    write_yaml,
    read_json,
    write_json,
)

# Session state
from lib.shared.session_state import (
    initialize_shared_session_state,
    handle_pending_navigation,
)

# Page generation
from lib.shared.page_generator import PageGenerator

# Types
from lib.shared.types import (
    ThinkingLevel,
    Provider,
    Message,
    ExpertConfig,
    ExpertInfo,
    PageInfo,
    ProviderConfig,
    ModelConfig,
    TokenUsage,
    ChatState,
    CacheStats,
    ValidationResult,
    # Type aliases
    ExpertID,
    PageNumber,
    Temperature,
    MessagesList,
    ProviderKey,
    ModelID,
    ApiKey,
    SystemPrompt,
    ThinkingLevelType,
)

__all__ = [
    # Constants
    "LLM_PROVIDERS",
    "SYSTEM_PROMPT_TEMPLATE",
    "EXAMPLE_EXPERTS_COUNT",
    "CONFIG_CACHE_TTL",
    "CONTEXT_USAGE_ALERT_THRESHOLD",
    "CONTEXT_USAGE_WARNING_THRESHOLD",
    "CONTEXT_USAGE_SAFE_THRESHOLD",
    "CONTEXT_USAGE_COLORS",
    "EXPERT_BEHAVIOR_DOCS",
    "get_provider_config",
    "get_model_config",
    "get_provider_base_url",
    "get_provider_display_name",
    "get_model_display_name",
    "get_max_tokens",
    "get_default_model_for_provider",
    "get_expert_behavior_docs",
    "get_expert_behavior_docs_edit",
    "get_provider_links",
    "get_provider_avatar",
    # Helpers
    "sanitize_name",
    "translate_expert_name",
    "validate_expert_name",
    "validate_api_key",
    # File operations
    "get_project_root",
    "get_streamlit_path",
    "safe_path_join",
    "validate_cwd",
    "set_secure_permissions",
    "ensure_file_exists",
    "ensure_directory_exists",
    # Format operations
    "read_toml",
    "write_toml",
    "read_yaml",
    "write_yaml",
    "read_json",
    "write_json",
    # Session state
    "initialize_shared_session_state",
    "handle_pending_navigation",
    # Page generation
    "PageGenerator",
    # Types
    "ThinkingLevel",
    "Provider",
    "Message",
    "ExpertConfig",
    "ExpertInfo",
    "PageInfo",
    "ProviderConfig",
    "ModelConfig",
    "TokenUsage",
    "ChatState",
    "CacheStats",
    "ValidationResult",
    "ExpertID",
    "PageNumber",
    "Temperature",
    "MessagesList",
    "ProviderKey",
    "ModelID",
    "ApiKey",
    "SystemPrompt",
    "ThinkingLevelType",
]
