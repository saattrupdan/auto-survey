"""Command-line interface for the application."""

import logging
import os
import warnings
from pathlib import Path

import click
import litellm
from dotenv import load_dotenv
from termcolor import colored

from auto_survey.agent import get_literature_survey_agent

load_dotenv()

# Set up logging
fmt = colored("%(asctime)s", "light_blue") + " ⋅ " + colored("%(message)s", "green")
logging.basicConfig(level=logging.INFO, format=fmt, datefmt="%Y-%m-%d %H:%M:%S")

logging.basicConfig(
    level=logging.INFO, format="%(asctime)s - %(name)s - %(levelname)s - %(message)s"
)
logger = logging.getLogger("auto_survey")


@click.command()
@click.argument("description", type=str, required=True)
@click.option(
    "--model-id",
    type=str,
    default="hosted_vllm/synquid/gemma-3-27b-it-FP8",
    show_default=True,
    help="The model ID to use.",
)
@click.option(
    "--api-base",
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
    "--output-dir",
    type=click.Path(file_okay=False, dir_okay=True, writable=True, path_type=Path),
    default=Path("auto_survey_reports"),
    show_default=True,
    help="The directory to save the output files.",
)
@click.option(
    "--stream/--no-stream",
    default=False,
    show_default=True,
    help="Whether to stream outputs from the model.",
)
def main(
    description: str,
    model_id: str,
    api_base: str | None,
    api_key_env_var: str | None,
    output_dir: Path,
    stream: bool,
) -> None:
    """Conduct a literature survey based on the provided description."""
    # Suppress logging, except for the AutoSurvey logger
    litellm.suppress_debug_info = True
    warnings.filterwarnings("ignore", category=UserWarning)
    warnings.filterwarnings("ignore", category=FutureWarning)
    for logging_name in logging.root.manager.loggerDict:
        if logging_name != "auto_survey":
            logging.getLogger(logging_name).setLevel(logging.CRITICAL)

    agent = get_literature_survey_agent(
        model_id=model_id,
        api_base=api_base,
        api_key=os.getenv(api_key_env_var) if api_key_env_var else None,
        output_path=output_dir / "report.md",
        stream=stream,
    )
    agent.run(task=description, reset=True)


if __name__ == "__main__":
    main()
