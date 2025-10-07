"""Tools to use during agent execution."""

import logging
import re
import subprocess
from pathlib import Path

from docling.document_converter import DocumentConverter
from smolagents import tool

logger = logging.getLogger("auto_survey")


@tool
def fetch_pdf_as_markdown(pdf_url: str) -> str:
    """Fetch a PDF from a URL and convert it to Markdown.

    Args:
        pdf_url:
            The URL of the PDF to fetch.

    Returns:
        The content of the PDF converted to Markdown.

    Raises:
        RuntimeError:
            If the PDF could not be parsed.
    """
    result = DocumentConverter().convert(source=pdf_url)
    markdown = result.document.export_to_markdown()
    return markdown


@tool
def write_markdown_document_to_file(markdown: str, file_path: str) -> str:
    """Write a Markdown document to a file.

    Args:
        markdown:
            The Markdown document to write.
        file_path:
            The path to the file to write the document to.

    Returns:
        A message indicating that the document was written successfully.

    Raises:
        ValueError:
            If the file path does not end with .md.
    """
    if not file_path.endswith(".md"):
        raise ValueError("The file path must end with .md")
    path = Path(file_path)
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(data=markdown, encoding="utf-8")
    return f"Markdown document written to {file_path}"


@tool
def load_markdown_document_from_file(file_path: str) -> str:
    """Load a Markdown document from a file.

    Args:
        file_path:
            The path to the file to load the document from.

    Returns:
        The loaded Markdown document.

    Raises:
        ValueError:
            If the file path does not end with .md.
        FileNotFoundError:
            If the file does not exist.
    """
    if not file_path.endswith(".md"):
        raise ValueError("The file path must end with .md")
    path = Path(file_path)
    if not path.exists():
        raise FileNotFoundError(f"The file {file_path} does not exist.")
    return path.read_text(encoding="utf-8")


@tool
def final_answer(path_to_markdown_report: str) -> str:
    """Provide the final answer to the user.

    Args:
        path_to_markdown_report:
            The path to the saved Markdown report file.

    Returns:
        A message indicating that the final answer was provided.
    """
    # Raise error if the file does not exist
    path = Path(path_to_markdown_report)
    if not path.exists():
        raise FileNotFoundError(f"The file {path_to_markdown_report} does not exist.")

    # Raise error if the report is too short
    markdown = path.read_text(encoding="utf-8")
    if len(markdown) < 10_000:
        raise ValueError(
            "The report is too short to be a final answer. It only contains "
            f"{len(markdown):,} characters, which is less than the minimum of 10,000 "
            "characters. Elaborate further on the papers you found, or consider "
            "finding more papers to include in the report."
        )

    # Raise error if the report does not contain a References section
    if "## References" not in markdown:
        raise ValueError(
            "The report does not contain a References section. Please ensure that the "
            "report includes a References section, starting with '## References'."
        )

    # Ensure that there are double newlines between references in the References section
    references_section = markdown.split("## References")[-1]
    references_section = re.sub(r"\n+", "\n\n", references_section.strip())
    markdown = (
        markdown.split("## References")[0]
        + "\n\n## References\n\n"
        + references_section
    )

    # Convert the Markdown file to a PDF file, if dependencies are installed
    pandoc_installed = (
        subprocess.run(["pandoc", "--version"], capture_output=True).returncode == 0
    )
    weasyprint_installed = (
        subprocess.run(["weasyprint", "--version"], capture_output=True).returncode == 0
    )
    if pandoc_installed and weasyprint_installed:
        subprocess.run(
            [
                "pandoc",
                "--pdf-engine=weasyprint",
                str(path),
                "-o",
                str(path.with_suffix(".pdf")),
            ],
            capture_output=True,
        )
        logger.info(f"PDF report saved to {path.with_suffix('.pdf')}")
    else:
        logger.warning(
            "Pandoc and/or WeasyPrint not installed. Skipping PDF generation. If you "
            "get them installed, you can run the following command to convert the "
            "Markdown report to PDF:\n"
            f"`pandoc --pdf-engine=weasyprint {path} -o {path.with_suffix('.pdf')}`"
        )

    return path.as_posix()
