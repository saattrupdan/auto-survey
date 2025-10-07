"""Tools to use during agent execution."""

import logging
import re
import subprocess
from pathlib import Path

from docling.document_converter import DocumentConverter
from smolagents import tool

logger = logging.getLogger("auto_survey")


@tool
def parse_website(url: str) -> str:
    """Visit a website and return its content as Markdown.

    This can parse both HTML, PDF content and more.

    Args:
        url:
            The URL of the website to visit.

    Returns:
        The content of the website converted to Markdown.

    Raises:
        RuntimeError:
            If the website could not be fetched or parsed.
    """
    result = DocumentConverter().convert(source=url)
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

    Raises:
        FileNotFoundError:
            If the file does not exist.
        ValueError:
            If the report is too short, does not contain a References section, or
            contains fewer than 10 references.
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
    references_section = markdown.split("## References")[-1].strip()
    if "\n\n" not in references_section:
        references_section = re.sub(r"\n+", "\n\n", references_section.strip())
        markdown = (
            markdown.split("## References")[0]
            + "\n\n## References\n\n"
            + references_section
        )
        path.write_text(data=markdown, encoding="utf-8")
        logger.info(
            "Replaced the newlines between references in the References section with "
            "double newlines."
        )
    else:
        logger.info(
            "The References has correctly formatted double newlines between "
            "references 🎉"
        )

    # Raise error if there are fewer than 10 references in the References section
    num_references = len(
        [
            line.strip()
            for line in markdown.split("## References")[-1].splitlines()
            if line.strip()
        ]
    )
    if num_references < 10:
        raise ValueError(
            "The report contains fewer than 10 references in the References section. "
            f"It only contains {num_references} references. Please find more academic "
            "papers to include in the report."
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

    return (
        f"All done! You can find the Markdown report at {path.as_posix()} and the "
        "associated PDF version of the report at "
        f"{path.with_suffix('.pdf').as_posix()}."
    )


@tool
def count_characters(text: str) -> int:
    """Count the number of characters in a text.

    Args:
        text:
            The text to count the characters in.

    Returns:
        The number of characters in the text.
    """
    return len(text)


# TODO: Consider Semantic Scholar API tool
# Search API: https://api.semanticscholar.org/graph/v1/paper/search?limit=NUM_RESULTS&query=QUERY
#   - This API gives a list of paper IDs
# Paper API: https://api.semanticscholar.org/graph/v1/paper/PAPER_ID?fields=url,year,authors
#   - This API gives the title, URL, year and author IDs of a paper given its paper ID
