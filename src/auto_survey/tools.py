"""Tools to use during agent execution."""

import logging
from pathlib import Path

from smolagents import tool
from tika import parser as pdf_parser

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
        ValueError:
            If the URL does not end with .pdf.
        RuntimeError:
            If the PDF could not be parsed.
    """
    if not pdf_url.endswith(".pdf"):
        raise ValueError("The URL must end with .pdf")

    parsed_pdf = pdf_parser.from_file(pdf_url, service="text")
    if not isinstance(parsed_pdf, dict):
        raise RuntimeError(
            f"Failed to parse the PDF, received {parsed_pdf} instead of a dict."
        )
    pdf_content = parsed_pdf["content"]
    if pdf_content is None:
        raise RuntimeError("Failed to extract content from the PDF, as it was None.")
    return pdf_content


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
