import time
from enum import Enum
from typing import Callable, Any
from core.logger import get_logger

logger = get_logger("infrastructure.circuit_breaker")


class CircuitState(Enum):
    CLOSED = "CLOSED"
    OPEN = "OPEN"
    HALF_OPEN = "HALF_OPEN"


class CircuitBreakerOpenException(Exception):
    """Raised when an operation is attempted while circuit breaker is OPEN"""
    pass


class CircuitBreaker:
    """
    Production-grade Circuit Breaker pattern implementation.
    Prevents cascading service degradation by tripping when failure threshold is exceeded.
    """

    def __init__(
        self,
        name: str = "default",
        failure_threshold: int = 3,
        recovery_timeout: float = 30.0,
    ):
        self.name = name
        self.failure_threshold = failure_threshold
        self.recovery_timeout = recovery_timeout
        self.state = CircuitState.CLOSED
        self.failure_count = 0
        self.last_state_change = time.time()

    def allow_request(self) -> bool:
        """Determines if a request should be permitted to execute"""
        now = time.time()

        if self.state == CircuitState.CLOSED:
            return True

        if self.state == CircuitState.OPEN:
            # Check if recovery timeout has elapsed to test recovery (HALF_OPEN)
            if (now - self.last_state_change) >= self.recovery_timeout:
                logger.info("CircuitBreaker '%s' transitioned to HALF_OPEN (probing remote service)", self.name)
                self.state = CircuitState.HALF_OPEN
                self.last_state_change = now
                return True
            return False

        # In HALF_OPEN state, allow probe request
        return True

    def record_success(self) -> None:
        """Records a successful call and resets failure count/state"""
        if self.state != CircuitState.CLOSED:
            logger.info("CircuitBreaker '%s' recovered successfully, transitioning to CLOSED", self.name)
        self.state = CircuitState.CLOSED
        self.failure_count = 0
        self.last_state_change = time.time()

    def record_failure(self) -> None:
        """Records a failed call and trips circuit if threshold exceeded"""
        self.failure_count += 1
        now = time.time()

        if self.state == CircuitState.HALF_OPEN:
            logger.warning(
                "CircuitBreaker '%s' failed during probe, reverting to OPEN for %.1fs",
                self.name,
                self.recovery_timeout
            )
            self.state = CircuitState.OPEN
            self.last_state_change = now
        elif self.failure_count >= self.failure_threshold:
            logger.warning(
                "CircuitBreaker '%s' tripped to OPEN (%d failures >= threshold %d). Fast-failing for %.1fs",
                self.name,
                self.failure_count,
                self.failure_threshold,
                self.recovery_timeout
            )
            self.state = CircuitState.OPEN
            self.last_state_change = now

    def call(self, func: Callable, *args, **kwargs) -> Any:
        """Executes function wrapped inside circuit breaker protection"""
        if not self.allow_request():
            logger.debug("CircuitBreaker '%s' is OPEN. Fast-failing without calling remote API", self.name)
            raise CircuitBreakerOpenException(f"CircuitBreaker '{self.name}' is OPEN")

        try:
            result = func(*args, **kwargs)
            self.record_success()
            return result
        except Exception as exc:
            self.record_failure()
            raise exc
