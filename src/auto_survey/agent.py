"""Agents used within the application."""

import logging
from pathlib import Path

from smolagents import CodeAgent, DuckDuckGoSearchTool, LiteLLMModel, VisitWebpageTool

from auto_survey.tools import (
    get_search_google_scholar_tool,
    load_markdown_document_from_file,
    write_markdown_document_to_file,
)

logger = logging.getLogger("auto_survey")


LITERATURE_SURVEY_AGENT_SYSTEM_PROMPT = """
You are an expert research assistant specialising in conducting literature surveys.

Your task is to help users find and summarise relevant academic papers based on what
they are currently researching.

This is no small task, and you are expected to be thorough and methodical in your
approach.

A literature survey should end with a comprehensive report in Markdown that
includes all relevant papers and a summary of how they relate to the user's research.
You need to fetch and read the papers to write this report.


The report should be well-structured and written in a coherent story, rather than simply
listing all the papers.

Use [1], [2], etc. to refer to papers in your summaries, and include a references
section at the end, formatted in APA style.

To help you find the papers, you can search academic databases such as Google Scholar
and ArXiv, as well as general web searches.

Your report should be at least 3 pages long. That is, it should be at least 1500 words.

When you are done with your report, you should save it to the {output_path} file. Feel
free to store draft versions of the report as you go along, just overwrite the file each
time you save it.
""".strip()


def get_literature_survey_agent(
    model_id: str, api_base: str | None, api_key: str | None, output_path: Path
) -> CodeAgent:
    """Create an agent that conducts literature reviews.

    Args:
        model_id:
            The model ID to use.
        api_base:
            The API base URL for the model. Can be None if not needed.
        api_key:
            The API key for the model. Can be None if not needed.
        output_path:
            The path to save the output Markdown report to.

    Returns:
        The agent.
    """
    model = LiteLLMModel(
        model_id=model_id,
        api_base=api_base,
        api_key=api_key,
        temperature=0.0,
        max_tokens=10_000,
        stop=[],
    )
    agent = CodeAgent(
        model=model,
        instructions=LITERATURE_SURVEY_AGENT_SYSTEM_PROMPT.format(
            output_path=output_path.as_posix()
        ),
        max_print_outputs_length=10_000,
        stream_outputs=True,
        code_block_tags="markdown",
        additional_authorized_imports=[
            "os",
            "re",
            "json",
            "requests",
            "pandas",
            "numpy",
        ],
        tools=[
            get_search_google_scholar_tool(),
            write_markdown_document_to_file,
            load_markdown_document_from_file,
            DuckDuckGoSearchTool(max_results=10, rate_limit=1),
            VisitWebpageTool(max_output_length=40_000),
        ],
        max_steps=1000,
    )
    return agent
