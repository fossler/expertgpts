"""Custom exception hierarchy for ExpertGPTs.

This module defines all custom exceptions used throughout the application
for better error handling and user feedback.
"""


class ExpertGPTsError(Exception):
    """Base exception for all ExpertGPTs errors.

    All custom exceptions inherit from this class, allowing for easy
    catching of any application-specific error.
    """
    pass


class ConfigurationError(ExpertGPTsError):
    """Raised when configuration is invalid or missing.

    This includes errors in:
    - Expert configuration files
    - API key configuration
    - Provider/model configuration
    - Page configuration
    """
    pass


class ValidationError(ExpertGPTsError):
    """Raised when input validation fails.

    This includes errors in:
    - User input (names, descriptions, etc.)
    - API key formats
    - Parameter values (temperature, thinking levels, etc.)
    - File paths and names
    """
    pass


class APIError(ExpertGPTsError):
    """Raised when API calls fail.

    This includes errors from:
    - LLM provider APIs (DeepSeek, OpenAI, Z.AI)
    - Network connectivity issues
    - Authentication failures
    - Rate limiting
    - Invalid API responses
    """
    pass


class FileSystemError(ExpertGPTsError):
    """Raised when file system operations fail.

    This includes errors in:
    - Reading/writing configuration files
    - Creating/deleting page files
    - Directory operations
    - File permissions
    """
    pass


class PageGenerationError(ExpertGPTsError):
    """Raised when page generation fails.

    This includes errors in:
    - Template processing
    - Page file creation
    - Expert ID generation
    - Page numbering conflicts
    """
    pass


class TokenLimitError(ExpertGPTsError):
    """Raised when token limits are exceeded.

    This includes errors when:
    - Context window is exceeded
    - Token counting fails
    - Input/output is too long
    """
    pass


class ProviderError(ExpertGPTsError):
    """Raised when provider operations fail.

    This includes errors when:
    - Provider is not supported
    - Model is not available
    - Provider-specific functionality fails
    """
    pass
