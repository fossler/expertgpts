"""Centralized logging configuration for ExpertGPTs application.

This module provides:
- Application-wide logger configuration
- Security audit logging for sensitive operations
- Structured logging for debugging
- Separation from Streamlit's UI messages

Usage:
    from utils.logger import get_logger, get_audit_logger

    # Application logging
    logger = get_logger(__name__)
    logger.info("Application started")
    logger.warning("Configuration file not found")
    logger.error("Failed to connect to API")

    # Audit logging
    audit = get_audit_logger()
    audit.log_api_key_change("openai", True)
    audit.log_expert_action("CREATE", "expert_123", True)
"""

import logging
import sys
from pathlib import Path
from typing import Optional


# Log file paths
LOG_DIR = Path(__file__).parent.parent / "logs"
SECURITY_LOG = LOG_DIR / "security.log"
APPLICATION_LOG = LOG_DIR / "application.log"

# Ensure log directory exists
LOG_DIR.mkdir(exist_ok=True)


class AuditLogger:
    """Security audit logger for sensitive operations.

    This logger creates a separate audit trail for security-relevant events:
    - API key changes
    - Expert CRUD operations
    - Configuration exports
    - Security events (path traversal attempts, etc.)
    """

    def __init__(self):
        self.logger = logging.getLogger("expertgpts.audit")
        self.logger.setLevel(logging.INFO)

        # Prevent duplicate handlers
        if self.logger.handlers:
            return

        # File handler for security audit log
        handler = logging.FileHandler(SECURITY_LOG)
        handler.setLevel(logging.INFO)

        # Audit format: timestamp | AUDIT | event_type | details
        formatter = logging.Formatter(
            '%(asctime)s | AUDIT | %(message)s',
            datefmt='%Y-%m-%d %H:%M:%S'
        )
        handler.setFormatter(formatter)
        self.logger.addHandler(handler)

        # Don't propagate to root logger (keep audit separate)
        self.logger.propagate = False

    def log_api_key_change(self, provider: str, success: bool):
        """Log API key changes.

        Args:
            provider: Provider name (openai, deepseek, zai)
            success: Whether the operation succeeded
        """
        status = "SUCCESS" if success else "FAILED"
        self.logger.info(f"API_KEY_CHANGE | provider={provider} | status={status}")

    def log_config_export(self, expert_count: int):
        """Log configuration export.

        Args:
            expert_count: Number of expert configs exported
        """
        self.logger.info(f"CONFIG_EXPORT | expert_count={expert_count}")

    def log_expert_action(self, action: str, expert_id: str, success: bool):
        """Log expert CRUD operations.

        Args:
            action: CREATE, UPDATE, DELETE, READ
            expert_id: Expert identifier
            success: Whether the operation succeeded
        """
        status = "SUCCESS" if success else "FAILED"
        self.logger.info(f"EXPERT_{action} | expert_id={expert_id} | status={status}")

    def log_security_event(self, event_type: str, details: str):
        """Log security-related events.

        Args:
            event_type: Type of security event (e.g., PATH_TRAVERSAL_ATTEMPT)
            details: Additional details about the event
        """
        self.logger.info(f"SECURITY_EVENT | type={event_type} | {details}")


class AppLogger:
    """Application logger for general logging.

    Provides both console and file logging with appropriate formatting:
    - Console: INFO level, human-readable
    - File: DEBUG level, detailed with file/line info
    """

    def __init__(self, name: str = "expertgpts"):
        self.logger = logging.getLogger(name)
        self.logger.setLevel(logging.DEBUG)

        # Prevent duplicate handlers
        if self.logger.handlers:
            return

        # Console handler with color (INFO level)
        console_handler = logging.StreamHandler(sys.stdout)
        console_handler.setLevel(logging.INFO)
        console_formatter = logging.Formatter(
            '%(asctime)s - %(name)s - %(levelname)s - %(message)s',
            datefmt='%Y-%m-%d %H:%M:%S'
        )
        console_handler.setFormatter(console_formatter)
        self.logger.addHandler(console_handler)

        # File handler for application log (DEBUG level)
        file_handler = logging.FileHandler(APPLICATION_LOG)
        file_handler.setLevel(logging.DEBUG)
        file_formatter = logging.Formatter(
            '%(asctime)s - %(name)s - %(levelname)s - %(filename)s:%(lineno)d - %(message)s',
            datefmt='%Y-%m-%d %H:%M:%S'
        )
        file_handler.setFormatter(file_formatter)
        self.logger.addHandler(file_handler)


# Global instances (singleton pattern)
_audit_logger = None
_app_logger = None


def get_audit_logger() -> AuditLogger:
    """Get the global audit logger instance.

    Returns:
        AuditLogger: Singleton audit logger instance
    """
    global _audit_logger
    if _audit_logger is None:
        _audit_logger = AuditLogger()
    return _audit_logger


def get_logger(name: Optional[str] = None) -> logging.Logger:
    """Get a configured application logger.

    Args:
        name: Logger name (defaults to "expertgpts")
              Typically use __name__ for module-specific loggers

    Returns:
        logging.Logger: Configured logger instance

    Example:
        from utils.logger import get_logger

        logger = get_logger(__name__)
        logger.info("Processing started")
        logger.debug("Debug information")
        logger.warning("Warning message")
        logger.error("Error occurred")
    """
    global _app_logger
    if _app_logger is None:
        _app_logger = AppLogger(name or "expertgpts")
    return _app_logger.logger


# Convenience functions for quick access
def log_security_event(event_type: str, details: str):
    """Log a security event.

    Args:
        event_type: Type of security event
        details: Event details
    """
    get_audit_logger().log_security_event(event_type, details)


def log_api_key_change(provider: str, success: bool):
    """Log an API key change.

    Args:
        provider: Provider name
        success: Whether the operation succeeded
    """
    get_audit_logger().log_api_key_change(provider, success)


def log_config_export(expert_count: int):
    """Log a configuration export.

    Args:
        expert_count: Number of expert configs exported
    """
    get_audit_logger().log_config_export(expert_count)


def log_expert_action(action: str, expert_id: str, success: bool):
    """Log an expert CRUD operation.

    Args:
        action: CREATE, UPDATE, DELETE, READ
        expert_id: Expert identifier
        success: Whether the operation succeeded
    """
    get_audit_logger().log_expert_action(action, expert_id, success)
