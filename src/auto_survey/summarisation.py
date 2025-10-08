"""Read and summarise relevant papers on a given topic."""

import logging
import tempfile
from time import sleep

import httpx
import litellm
from docling.document_converter import DocumentConverter
from litellm.types.utils import ModelResponse

from auto_survey.data_models import LiteLLMConfig, Paper, Summary
from auto_survey.utils import no_progress_bars

logger = logging.getLogger("auto_survey")


def summarise_paper(paper: Paper, topic: str, litellm_config: LiteLLMConfig) -> str:
    """Summarise a paper where the summary focuses on a given topic.

    Args:
        paper:
            The paper to summarise.
        topic:
            The topic to focus the summary on.
        litellm_config:
            The LiteLLM configuration to use.

    Returns:
        The summary of the paper.
    """
    content = ""

    # Try to get the content from the PDF if a URL is provided
    if paper.url != "":
        for _ in range(num_attempts := 3):
            try:
                content = parse_pdf(pdf_url=paper.url)
                break
            except httpx.HTTPStatusError as e:
                if e.response.status_code == 403:
                    logger.warning(
                        f"Access forbidden when trying to fetch PDF from {paper.url}."
                    )
                    break
                logger.warning(
                    f"Failed to fetch PDF from {paper.url}. The error was {e!r}. "
                    f"Retrying in a second..."
                )
                sleep(1)
            except httpx.ConnectError as e:
                logging.warning(
                    f"Connection error while trying to fetch PDF from {paper.url}. "
                    f"The error was {e!r}. Retrying in a second..."
                )
                sleep(1)
        else:
            logger.warning(
                f"Failed to fetch PDF from {paper.url}, after {num_attempts} attempts."
            )

    # If we couldn't get the content from the PDF, use the title and summary
    if content == "":
        content = f"# {paper.title}"
        if paper.summary != "":
            content += f"\n\n## Summary\n\n{paper.summary}"

    response = litellm.completion(
        messages=[
            dict(
                role="system",
                content="""
                    You are an expert research assistant. Your task is to read and
                    summarise research papers. The summary should focus on the provided
                    topic, highlighting the most relevant points from the paper. The
                    summary should be concise and informative.
                """.strip(),
            ),
            dict(
                role="user",
                content=f"""
                    Summarise the following paper, focusing on the topic {topic!r}. The
                    summary should be concise and informative, highlighting the most
                    relevant points from the paper.

                    <paper>
                    {content}
                    </paper>

                    You should return a JSON dictionary with a single key 'summary'
                    mapping to the summary string.
                """.strip(),
            ),
        ],
        temperature=0.0,
        max_tokens=1024,
        response_format=Summary,
        **litellm_config.model_dump(),
    )
    assert isinstance(response, ModelResponse)
    choice = response.choices[0]
    assert isinstance(choice, litellm.Choices)
    json_dict = choice.message.content or "{}"
    summary = Summary.model_validate_json(json_data=json_dict).summary
    return summary


def parse_pdf(pdf_url: str) -> str:
    """Parse the content of a PDF from a URL and convert it to Markdown.

    Args:
        pdf_url:
            The URL of the PDF to parse.

    Returns:
        The content of the PDF converted to Markdown.

    Raises:
        httpx.HTTPStatusError:
            If the PDF URL returns a non-200 status code.
    """
    # Get the raw PDF. We use a normal-looking header here to prevent blocking
    headers = {
        "User-Agent": (
            "Mozilla/5.0 (Macintosh; Intel Mac OS X 10.15; rv:143.0) Gecko/20100101 "
            "Firefox/143.0"
        )
    }
    response = httpx.get(
        url=pdf_url, headers=headers, follow_redirects=True, timeout=30
    )
    response.raise_for_status()

    # Parse the raw PDF as Markdown
    with tempfile.NamedTemporaryFile(mode="w+b") as temp_file, no_progress_bars():
        temp_file.write(response.content)
        temp_file.flush()
        result = DocumentConverter().convert(source=temp_file.name)
    markdown = result.document.export_to_markdown()

    return markdown
