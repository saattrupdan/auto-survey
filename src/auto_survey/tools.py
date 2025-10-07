"""Tools to use during agent execution."""

import logging
import os
import re
import subprocess
import tempfile
import time
from pathlib import Path

import httpx
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
        httpx.HTTPStatusError:
            If the website returns a non-200 status code.
    """
    headers = {
        "User-Agent": (
            "Mozilla/5.0 (Macintosh; Intel Mac OS X 10.15; rv:143.0) Gecko/20100101 "
            "Firefox/143.0"
        )
    }
    response = httpx.get(url=url, headers=headers)
    response.raise_for_status()
    with tempfile.NamedTemporaryFile(mode="w+b") as temp_file:
        temp_file.write(response.content)
        temp_file.flush()
        result = DocumentConverter().convert(source=temp_file.name)
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
    markdown_without_references = markdown.split("## References")[0]
    num_words = len(re.findall(r"\b\w+\b", markdown_without_references))
    if num_words < 1_500:
        raise ValueError(
            "The report is too short to be a final answer. It only contains "
            f"{num_words} words, excluding references. Please expand the report to at "
            "least 1,500 words (without references), e.g., by adding more details to "
            "your sections and/or finding more papers to include in the report."
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
def find_papers(query: str, num_results: int) -> list[dict]:
    """Find academic papers related to a query.

    Args:
        query:
            The query to search for.
        num_results:
            The number of results to return.

    Returns:
        A list of dictionaries containing the title, URL, year and authors of the
        papers found.

    Raises:
        httpx.HTTPStatusError:
            If the API returns a non-200 status code.
    """
    while True:
        response = httpx.get(
            url="https://api.semanticscholar.org/graph/v1/paper/search",
            params=dict(
                query=query,
                limit=num_results,
                fields="title,url,year,authors,abstract,openAccessPdf",
            ),
            headers={
                "User-Agent": (
                    "Mozilla/5.0 (Macintosh; Intel Mac OS X 10.15; rv:143.0) "
                    "Gecko/20100101 Firefox/143.0"
                ),
                "x-api-key": os.getenv("SEMANTIC_SCHOLAR_API_KEY", ""),
            },
            timeout=30,
        )
        if response.status_code == 429:
            logger.warning(
                "Rate limit exceeded when querying Semantic Scholar API. "
                "Waiting 10 seconds before retrying..."
            )
            time.sleep(10)
            continue
        break
    response.raise_for_status()
    results = response.json().get("data", [])
    return results
