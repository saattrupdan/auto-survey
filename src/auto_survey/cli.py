"""Command-line interface for the application."""

import logging
import os
import subprocess
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
    description: str,
    model_id: str,
    api_base: str | None,
    api_key: str | None,
    output_dir: Path,
) -> None:
    """Conduct a literature survey based on the provided description."""
    # Suppress logging, except for the AutoSurvey logger
    litellm.suppress_debug_info = True
    warnings.filterwarnings("ignore", category=UserWarning)
    warnings.filterwarnings("ignore", category=FutureWarning)
    for logging_name in logging.root.manager.loggerDict:
        if logging_name != "auto_survey":
            logging.getLogger(logging_name).setLevel(logging.CRITICAL)

    # Set up paths
    output_dir.mkdir(parents=True, exist_ok=True)
    markdown_path = output_dir / "report.md"
    pdf_path = output_dir / "report.pdf"

    # Create the Markdown report and save it to a file
    agent = get_literature_survey_agent(
        model_id=model_id, api_base=api_base, api_key=api_key, output_path=markdown_path
    )
    markdown_report = str(agent.run(task=description, reset=True))
    markdown_path.write_text(markdown_report, encoding="utf-8")
    logger.info(f"Markdown report saved to {markdown_path}")

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
                str(markdown_path),
                "-o",
                str(pdf_path),
            ],
            capture_output=True,
        )
        logger.info(f"PDF report saved to {pdf_path}")
    else:
        logger.warning(
            "Pandoc and/or WeasyPrint not installed. Skipping PDF generation. If you "
            "get them installed, you can run the following command to convert the "
            "Markdown report to PDF:\n"
            f"`pandoc --pdf-engine=weasyprint {markdown_path} -o {pdf_path}`"
        )


if __name__ == "__main__":
    main()
