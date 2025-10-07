"""Run the AutoSurvey application."""

import logging
import os
import warnings
from pathlib import Path

import click
import litellm
from dotenv import load_dotenv
from smolagents import GradioUI
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
    "--api-key",
    type=str,
    default=os.getenv("INFERENCE_SERVER_API_KEY", None),
    help="The API key for the model, if needed. Can be None if not needed.",
)
@click.option(
    "--output-dir",
    type=click.Path(file_okay=False, dir_okay=True, writable=True, path_type=Path),
    default=Path("auto_survey_reports"),
    show_default=True,
    help="The directory to save the output files.",
)
def main(
    model_id: str, api_base: str | None, api_key: str | None, output_dir: Path
) -> None:
    """Run the AutoSurvey application."""
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
        api_key=api_key,
        output_path=output_dir / "report.md",
    )
    app = GradioUI(agent=agent)
    app.launch(share=True)


if __name__ == "__main__":
    main()
