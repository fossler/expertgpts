"""Structured logging system for ExpertGPTs.

This module provides structured logging capabilities for debugging,
monitoring, and performance analysis.
"""

import logging
import json
import time
from datetime import datetime
from typing import Dict, Any, Optional
from pathlib import Path
from contextlib import contextmanager


class StructuredLogger:
    """Structured logger with JSON formatting for log analysis.

    This logger outputs logs in a structured JSON format that can be
    easily parsed by log analysis tools and dashboards.
    """

    def __init__(self, name: str, log_file: Optional[str] = None):
        """Initialize the structured logger.

        Args:
            name: Logger name (usually __name__ of the calling module)
            log_file: Optional log file path. If None, logs to console only.
        """
        self.logger = logging.getLogger(name)
        self.logger.setLevel(logging.INFO)

        # Remove existing handlers to avoid duplicates
        self.logger.handlers.clear()

        # Create formatter
        formatter = logging.Formatter(
            '%(asctime)s - %(name)s - %(levelname)s - %(message)s'
        )

        # Console handler
        console_handler = logging.StreamHandler()
        console_handler.setFormatter(formatter)
        self.logger.addHandler(console_handler)

        # File handler (if specified)
        if log_file:
            log_path = Path(log_file)
            log_path.parent.mkdir(parents=True, exist_ok=True)
            file_handler = logging.FileHandler(log_file)
            file_handler.setFormatter(formatter)
            self.logger.addHandler(file_handler)

    def log_api_call(
        self,
        provider: str,
        model: str,
        prompt_tokens: int,
        completion_tokens: int,
        total_tokens: int,
        duration: float,
        success: bool = True,
        error: Optional[str] = None
    ) -> None:
        """Log an API call with structured data.

        Args:
            provider: LLM provider (e.g., "deepseek", "openai")
            model: Model identifier
            prompt_tokens: Number of tokens in prompt
            completion_tokens: Number of tokens in completion
            total_tokens: Total tokens used
            duration: Request duration in seconds
            success: Whether the call succeeded
            error: Error message if call failed
        """
        log_data = {
            "event": "api_call",
            "provider": provider,
            "model": model,
            "prompt_tokens": prompt_tokens,
            "completion_tokens": completion_tokens,
            "total_tokens": total_tokens,
            "duration_ms": round(duration * 1000, 2),
            "success": success,
            "timestamp": datetime.now().isoformat()
        }

        if error:
            log_data["error"] = error

        if success:
            self.logger.info(json.dumps(log_data))
        else:
            self.logger.error(json.dumps(log_data))

    def log_page_generation(
        self,
        expert_id: str,
        expert_name: str,
        page_number: int,
        duration: float,
        success: bool = True
    ) -> None:
        """Log a page generation event.

        Args:
            expert_id: Expert's unique identifier
            expert_name: Expert's display name
            page_number: Page number
            duration: Generation duration in seconds
            success: Whether generation succeeded
        """
        log_data = {
            "event": "page_generation",
            "expert_id": expert_id,
            "expert_name": expert_name,
            "page_number": page_number,
            "duration_ms": round(duration * 1000, 2),
            "success": success,
            "timestamp": datetime.now().isoformat()
        }

        if success:
            self.logger.info(json.dumps(log_data))
        else:
            self.logger.error(json.dumps(log_data))

    def log_config_load(
        self,
        expert_id: str,
        duration: float,
        success: bool = True,
        error: Optional[str] = None
    ) -> None:
        """Log a configuration load event.

        Args:
            expert_id: Expert's unique identifier
            duration: Load duration in seconds
            success: Whether load succeeded
            error: Error message if load failed
        """
        log_data = {
            "event": "config_load",
            "expert_id": expert_id,
            "duration_ms": round(duration * 1000, 2),
            "success": success,
            "timestamp": datetime.now().isoformat()
        }

        if error:
            log_data["error"] = error

        if success:
            self.logger.info(json.dumps(log_data))
        else:
            self.logger.warning(json.dumps(log_data))

    def log_cache_operation(
        self,
        operation: str,
        cache_key: str,
        hit: bool,
        duration: float
    ) -> None:
        """Log a cache operation.

        Args:
            operation: Operation type (e.g., "get", "set", "invalidate")
            cache_key: The cache key
            hit: Whether it was a cache hit
            duration: Operation duration in seconds
        """
        log_data = {
            "event": "cache_operation",
            "operation": operation,
            "cache_key": cache_key,
            "hit": hit,
            "duration_ms": round(duration * 1000, 2),
            "timestamp": datetime.now().isoformat()
        }

        self.logger.debug(json.dumps(log_data))

    def log_error(
        self,
        error_type: str,
        message: str,
        context: Optional[Dict[str, Any]] = None
    ) -> None:
        """Log an error with context.

        Args:
            error_type: Type of error (e.g., "ValidationError", "APIError")
            message: Error message
            context: Additional context information
        """
        log_data = {
            "event": "error",
            "error_type": error_type,
            "message": message,
            "timestamp": datetime.now().isoformat()
        }

        if context:
            log_data["context"] = context

        self.logger.error(json.dumps(log_data))


@contextmanager
def log_duration(logger: StructuredLogger, event_name: str, **context):
    """Context manager for logging the duration of an operation.

    Args:
        logger: StructuredLogger instance
        event_name: Name of the event being logged
        **context: Additional context to log

    Example:
        >>> with log_duration(logger, "api_call", provider="deepseek"):
        ...     # Perform operation
        ...     pass
    """
    start_time = time.time()
    try:
        yield
    finally:
        duration = time.time() - start_time
        log_data = {
            "event": event_name,
            "duration_ms": round(duration * 1000, 2),
            "timestamp": datetime.now().isoformat(),
            **context
        }
        logger.logger.info(json.dumps(log_data))


def get_logger(name: str, log_file: Optional[str] = None) -> StructuredLogger:
    """Get or create a StructuredLogger instance.

    Args:
        name: Logger name (usually __name__)
        log_file: Optional log file path

    Returns:
        StructuredLogger instance

    Example:
        >>> from utils.logging import get_logger
        >>> logger = get_logger(__name__)
        >>> logger.log_api_call(...)
    """
    return StructuredLogger(name, log_file)


# Performance monitoring class
class PerformanceMonitor:
    """Monitor and track performance metrics."""

    def __init__(self):
        """Initialize the performance monitor."""
        self.metrics = {}
        self.logger = get_logger("performance")

    def track_api_call(
        self,
        provider: str,
        model: str,
        tokens: int,
        duration: float
    ) -> None:
        """Track an API call's performance.

        Args:
            provider: LLM provider
            model: Model identifier
            tokens: Total tokens used
            duration: Duration in seconds
        """
        key = f"{provider}_{model}"
        if key not in self.metrics:
            self.metrics[key] = {
                "call_count": 0,
                "total_tokens": 0,
                "total_duration": 0.0
            }

        self.metrics[key]["call_count"] += 1
        self.metrics[key]["total_tokens"] += tokens
        self.metrics[key]["total_duration"] += duration

        # Log the call
        self.logger.log_api_call(
            provider=provider,
            model=model,
            prompt_tokens=0,  # Not tracked separately
            completion_tokens=tokens,
            total_tokens=tokens,
            duration=duration,
            success=True
        )

    def get_stats(self) -> Dict[str, Dict]:
        """Get performance statistics.

        Returns:
            Dict with performance metrics for each provider/model combination
        """
        stats = {}
        for key, data in self.metrics.items():
            if data["call_count"] > 0:
                stats[key] = {
                    "call_count": data["call_count"],
                    "total_tokens": data["total_tokens"],
                    "avg_duration_ms": round(
                        (data["total_duration"] / data["call_count"]) * 1000, 2
                    ),
                    "avg_tokens_per_call": round(
                        data["total_tokens"] / data["call_count"], 2
                    )
                }
        return stats

    def reset(self) -> None:
        """Reset all metrics."""
        self.metrics.clear()


# Global performance monitor instance
_performance_monitor = PerformanceMonitor()


def get_performance_monitor() -> PerformanceMonitor:
    """Get the global performance monitor instance.

    Returns:
        PerformanceMonitor: Global performance monitor
    """
    return _performance_monitor
