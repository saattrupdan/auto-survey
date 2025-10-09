"""Command-line interface for the application."""

import logging
import os
import re
import warnings
from pathlib import Path

import click
import litellm
from termcolor import colored
from tqdm.auto import tqdm

from auto_survey.ascii import ASCII_LOGO
from auto_survey.data_models import LiteLLMConfig
from auto_survey.pdf_conversion import convert_markdown_file_to_pdf
from auto_survey.search import get_all_papers, is_relevant_paper
from auto_survey.summarisation import summarise_paper
from auto_survey.writing import write_literature_survey

logger = logging.getLogger("auto_survey")


@click.command()
@click.argument("topic", type=str, required=True)
@click.option(
    "--model",
    type=str,
    default="gpt-4.1-mini",
    show_default=True,
    help="The model ID to use.",
)
@click.option(
    "--base-url",
    type=str,
    default=None,
    show_default=True,
    help="The API base URL for the model, if a custom inference server is used. Can be "
    "None if not needed.",
)
@click.option(
    "--api-key-env-var", type=str, default=None, help="The API key for the model."
)
@click.option(
    "--num-papers",
    type=int,
    default=50,
    show_default=True,
    help="The number of relevant papers to find.",
)
@click.option(
    "--num-queries",
    type=int,
    default=10,
    show_default=True,
    help="The number of queries to generate for searching for papers.",
)
@click.option(
    "--search-batch-size",
    type=int,
    default=5,
    show_default=True,
    help="The number of papers to fetch in each batch when searching for papers.",
)
@click.option(
    "--output-dir",
    type=click.Path(file_okay=False, dir_okay=True, writable=True, path_type=Path),
    default=Path("auto_survey_reports"),
    show_default=True,
    help="The directory to save the output files.",
)
@click.option(
    "--verbose/--no-verbose",
    default=False,
    show_default=True,
    help="Whether to show verbose output, including debug information from "
    "LiteLLM and other libraries.",
)
def main(
    topic: str,
    model: str,
    base_url: str | None,
    api_key_env_var: str | None,
    num_papers: int,
    num_queries: int,
    search_batch_size: int,
    output_dir: Path,
    verbose: bool,
) -> None:
    """Conduct a literature survey based on the provided topic."""
    if verbose:
        logger.setLevel(logging.DEBUG)
    else:
        litellm.suppress_debug_info = True
        warnings.filterwarnings("ignore", category=UserWarning)
        warnings.filterwarnings("ignore", category=FutureWarning)
        for logging_name in logging.root.manager.loggerDict:
            if logging_name != "auto_survey":
                logging.getLogger(logging_name).setLevel(logging.CRITICAL)

    # Set up paths
    output_dir.mkdir(parents=True, exist_ok=True)
    topic_filename = re.sub(r"[^a-z_]", "", topic.replace(" ", "_").lower())
    markdown_path = output_dir / f"{topic_filename}_survey.md"
    pdf_path = output_dir / f"{topic_filename}_survey.pdf"

    # Set up LiteLLM configuration to use for all LLM calls
    litellm_config = LiteLLMConfig(
        model=model,
        base_url=base_url,
        api_key=os.getenv(api_key_env_var) if api_key_env_var else None,
    )

    # Show ASCII logo
    logger.info(ASCII_LOGO)

    # Search for relevant papers
    papers = get_all_papers(
        topic=topic,
        num_relevant_papers=num_papers,
        num_queries=num_queries,
        batch_size=search_batch_size,
        litellm_config=litellm_config,
    )

    # Summarise each paper
    for paper in tqdm(
        iterable=papers,
        desc=colored("Summarising papers", "light_yellow"),
        unit="paper",
        ascii="—▰",
        colour="yellow",
    ):
        paper.summary = summarise_paper(
            paper=paper, topic=topic, verbose=verbose, litellm_config=litellm_config
        )

    # Check again that the papers are relevant using their summaries rather than
    # abstracts
    papers = [
        paper
        for paper in papers
        if is_relevant_paper(paper=paper, topic=topic, litellm_config=litellm_config)
    ]
    logger.debug(
        f"After reading the full papers, {len(papers):,} papers continue to be "
        "relevant to the topic."
    )

    # Write the literature survey
    literature_survey = write_literature_survey(
        topic=topic, relevant_papers=papers, litellm_config=litellm_config
    )
    logger.info("All done! 🎉")

    # Save the literature survey in Markdown format and convert to PDF
    markdown_path.write_text(literature_survey)
    convert_markdown_file_to_pdf(markdown_path=markdown_path)
    logger.info(f"Here is the survey in Markdown format: {markdown_path.as_posix()}")
    logger.info(f"Here is the corresponding PDF: {pdf_path.as_posix()}")


if __name__ == "__main__":
    main()
