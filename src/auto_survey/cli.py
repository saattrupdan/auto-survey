"""Command-line interface for the application."""

import logging
import os
import re
import subprocess
import warnings
from pathlib import Path

import click
import litellm
from dotenv import load_dotenv
from termcolor import colored
from tqdm.auto import tqdm

from auto_survey.data_models import LiteLLMConfig
from auto_survey.search import get_all_papers, is_relevant_paper
from auto_survey.summarisation import summarise_paper
from auto_survey.writing import write_literature_survey

load_dotenv()

# Set up logging
fmt = f"[%(asctime)s]\n{colored('%(message)s', 'light_yellow')}\n"
logging.basicConfig(level=logging.INFO, format=fmt, datefmt="%Y-%m-%d %H:%M:%S")
logger = logging.getLogger("auto_survey")


@click.command()
@click.argument("topic", type=str, required=True)
@click.option(
    "--model",
    type=str,
    default="hosted_vllm/synquid/gemma-3-27b-it-FP8",
    show_default=True,
    help="The model ID to use.",
)
@click.option(
    "--base-url",
    type=str,
    default="https://inference.projects.alexandrainst.dk/v1",
    show_default=True,
    help="The API base URL for the model, if a custom inference server is used. Can be "
    "None if not needed.",
)
@click.option(
    "--api-key-env-var",
    type=str,
    default="INFERENCE_SERVER_API_KEY",
    help="The API key for the model.",
)
@click.option(
    "--num-papers",
    type=int,
    default=50,
    show_default=True,
    help="The minimum number of relevant papers to find.",
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
    output_dir: Path,
    verbose: bool,
) -> None:
    """Conduct a literature survey based on the provided topic."""
    # Suppress logging, except for the AutoSurvey logger
    if not verbose:
        logger.setLevel(logging.DEBUG)
        litellm.suppress_debug_info = True
        warnings.filterwarnings("ignore", category=UserWarning)
        warnings.filterwarnings("ignore", category=FutureWarning)
        for logging_name in logging.root.manager.loggerDict:
            if logging_name != "auto_survey":
                logging.getLogger(logging_name).setLevel(logging.CRITICAL)

    # Set up paths
    output_dir.mkdir(parents=True, exist_ok=True)
    topic_filename = re.sub(r"[^a-z_]", "", topic.replace(" ", "_"))
    markdown_path = output_dir / f"{topic_filename}_survey.md"
    pdf_path = output_dir / f"{topic_filename}_survey.pdf"

    # Set up LiteLLM configuration to use for all LLM calls
    litellm_config = LiteLLMConfig(
        model=model,
        base_url=base_url,
        api_key=os.getenv(api_key_env_var) if api_key_env_var else None,
    )

    # Search for relevant papers
    papers = get_all_papers(
        topic=topic,
        min_num_relevant_papers=num_papers,
        batch_size=5,
        litellm_config=litellm_config,
    )

    # Summarise each paper
    for paper in tqdm(papers, desc="Summarising papers", unit="paper"):
        paper.summary = summarise_paper(
            paper=paper, topic=topic, litellm_config=litellm_config
        )

    # Check again that the papers are relevant using their summaries rather than
    # abstracts
    papers = [
        paper
        for paper in papers
        if is_relevant_paper(paper=paper, topic=topic, litellm_config=litellm_config)
    ]
    logger.info(
        f"After summarisation, {len(papers):,} papers continue to be relevant to the "
        "topic."
    )

    # Write the literature survey to a Markdown file
    literature_survey = write_literature_survey(
        topic=topic, relevant_papers=papers, litellm_config=litellm_config
    )
    markdown_path.write_text(literature_survey)
    logger.info(f"Wrote Markdown literature survey to {markdown_path.as_posix()}")

    # Try to convert the Markdown to PDF using Pandoc
    subprocess.run(
        ["pandoc", "--from=markdown", "--to=pdf", f"--output={pdf_path}"],
        input=literature_survey,
        encoding="utf-8",
        check=True,
    )
    logger.info(f"Wrote PDF literature survey to {pdf_path.as_posix()}")


if __name__ == "__main__":
    main()
