"""Exception hierarchy. Every failure mode the lab knows about has a named type so that
the orchestrator can decide whether to recover, skip a research line, or abort."""


class XQuantError(Exception):
    """Base class for all X-QUANT errors."""


class ConfigError(XQuantError):
    """Invalid or inconsistent configuration."""


class DataUnavailableError(XQuantError):
    """A data source could not be reached or is not configured. Never fabricate a substitute."""


class DataNotFound(DataUnavailableError):
    """The source answered but has no data for the request (e.g. HTTP 404 for a period with no file)."""


class RateLimited(DataUnavailableError):
    """The source asked us to slow down (HTTP 429). ``retry_after`` is in seconds when the server says."""

    def __init__(self, msg: str, retry_after: float | None = None) -> None:
        super().__init__(msg)
        self.retry_after = retry_after


class DataQualityError(XQuantError):
    """Data failed validation badly enough that research on it would be meaningless."""


class InsufficientDataError(XQuantError):
    """Not enough observations to run a statistically meaningful test."""


class LookAheadError(XQuantError):
    """A computation used information that would not have been available at decision time."""


class SplitAccessError(XQuantError):
    """Attempt to use a protected data split (TEST / FINAL) for optimisation or more than allowed."""


class BudgetExceeded(XQuantError):
    """A research budget limit was hit. Not an error in the scientific sense: a stop condition."""
