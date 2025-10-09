"""Utility functions in the application."""

import os
import sys


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
