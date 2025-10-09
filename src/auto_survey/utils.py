"""Utility functions in the application."""

import logging
import os
import sys
import warnings

import litellm


class no_terminal_output:
    """Context manager that suppresses all terminal output."""

    def __init__(self, disable: bool = False) -> None:
        """Initialise the context manager.

        Args:
            disable:
                If True, this context manager does nothing.
        """
        self.disable = disable
        self._original_stdout = sys.stdout
        self._original_stderr = sys.stderr

    def __enter__(self) -> None:
        """Suppress all terminal output."""
        if not self.disable:
            sys.stdout = open(os.devnull, "w")
            sys.stderr = open(os.devnull, "w")

    def __exit__(
        self,
        exc_type: type[BaseException] | None,
        exc_val: BaseException | None,
        exc_tb: type[BaseException] | None,
    ) -> None:
        """Re-enable terminal output."""
        if not self.disable:
            sys.stdout.close()
            sys.stderr.close()
            sys.stdout = self._original_stdout
            sys.stderr = self._original_stderr


def suppress_logging() -> None:
    """Suppress logging from all other libraries than ours."""
    litellm.suppress_debug_info = True

    warnings.filterwarnings("ignore", category=UserWarning)
    warnings.filterwarnings("ignore", category=FutureWarning)

    logger_names_to_ignore = [
        logger
        for logger in logging.root.manager.loggerDict.keys()
        if logger != "auto_survey"
    ]
    for logging_name in logger_names_to_ignore:
        logging.getLogger(logging_name).setLevel(logging.CRITICAL)
