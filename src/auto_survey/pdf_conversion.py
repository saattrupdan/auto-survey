"""Conversion of Markdown to PDF using Pandoc."""

import logging
import subprocess
from pathlib import Path

logger = logging.getLogger("auto_survey")


def convert_markdown_file_to_pdf(markdown_path: Path) -> bool:
    """Convert a Markdown file to PDF using Pandoc.

    Args:
        markdown_path:
            The path to the Markdown file.

    Returns:
        Whether the conversion was successful.
    """
    pdf_path = markdown_path.with_suffix(".pdf")

    # Raise an error if Pandoc is not installed
    pandoc_installed = (
        subprocess.run(
            ["pandoc", "--version"], capture_output=True, text=True
        ).returncode
        == 0
    )
    if not pandoc_installed:
        logger.error(
            "We cannot convert the Markdown to PDF because Pandoc is not installed. "
            "Please install Pandoc and try again. Installation instructions can be "
            "found at https://pandoc.org/installing.html. When Pandoc is installed, "
            f"you can convert the Markdown at {markdown_path.as_posix()} to PDF by "
            f"running `pandoc --from=markdown --to=pdf --output={pdf_path.as_posix()} "
            f"--pdf-engine=weasyprint {markdown_path.as_posix()}` in your terminal."
        )
        return False

    # Read the Markdown file
    markdown = markdown_path.read_text(encoding="utf-8")

    try:
        subprocess.run(
            [
                "pandoc",
                "--from=markdown",
                "--to=pdf",
                f"--output={pdf_path}",
                "--pdf-engine=weasyprint",
            ],
            input=markdown,
            encoding="utf-8",
            check=True,
        )
    except subprocess.CalledProcessError as e:
        logger.error(
            f"Failed to convert the Markdown to PDF. The error was {e!r}. You can "
            f"try to do this manually by running "
            f"`pandoc --from=markdown --to=pdf --output={pdf_path.as_posix()} "
            f"--pdf-engine=weasyprint {markdown_path.as_posix()}` in your terminal."
        )
        return False

    return pdf_path.exists()
