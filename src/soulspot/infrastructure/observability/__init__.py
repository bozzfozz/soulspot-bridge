"""Observability infrastructure for structured logging."""

from soulspot.infrastructure.observability.circuit_breaker import (
    CircuitBreaker,
    CircuitBreakerConfig,
    CircuitBreakerError,
    CircuitState,
    circuit_breaker,
)
from soulspot.infrastructure.observability.logging import (
    configure_logging,
    get_correlation_id,
    set_correlation_id,
)

__all__ = [
    "CircuitBreaker",
    "CircuitBreakerConfig",
    "CircuitBreakerError",
    "CircuitState",
    "circuit_breaker",
    "configure_logging",
    "get_correlation_id",
    "set_correlation_id",
]
