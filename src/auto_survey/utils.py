"""Utility functions in the application."""

from functools import partialmethod

from tqdm import tqdm


class no_progress_bars:
    """Context manager that disables all `tqdm` progress bars."""

    def __init__(self) -> None:
        """Initialise the context manager."""
        self.old_init = tqdm.__init__

    def __enter__(self) -> None:
        """Disable all `tqdm` progress bars."""
        tqdm.__init__ = partialmethod(tqdm.__init__, disable=True)

    def __exit__(
        self,
        exc_type: type[BaseException] | None,
        exc_val: BaseException | None,
        exc_tb: type[BaseException] | None,
    ) -> None:
        """Re-enable the progress bar."""
        tqdm.__init__ = self.old_init
