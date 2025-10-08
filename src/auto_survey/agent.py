"""Agents used within the application."""

import datetime as dt
import logging
from pathlib import Path

from smolagents import CodeAgent, DuckDuckGoSearchTool, LiteLLMModel

from auto_survey.prompts import (
    MANAGER_AGENT_SYSTEM_PROMPT,
    PAPER_LOCATOR_AGENT_SYSTEM_PROMPT,
    PAPER_READER_AGENT_SYSTEM_PROMPT,
    REPORT_WRITER_AGENT_SYSTEM_PROMPT,
)
from auto_survey.tools import (
    final_answer,
    find_papers,
    load_markdown_document_from_file,
    parse_website,
    write_markdown_document_to_file,
)

logger = logging.getLogger("auto_survey")


def get_literature_survey_agent(
    model_id: str,
    api_base: str | None,
    api_key: str | None,
    output_path: Path,
    stream: bool,
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
        stream:
            Whether to stream outputs from the model.

    Returns:
        The agent.
    """
    output_path.unlink(missing_ok=True)

    searcher = CodeAgent(
        model=LiteLLMModel(
            model_id=model_id,
            api_base=api_base,
            api_key=api_key,
            temperature=0.0,
            max_tokens=10_000,
            stop=[],
        ),
        instructions=PAPER_LOCATOR_AGENT_SYSTEM_PROMPT.strip(),
        max_print_outputs_length=50_000,
        stream_outputs=stream,
        code_block_tags="markdown",
        additional_authorized_imports=[
            "os",
            "re",
            "json",
            "requests",
            "pandas",
            "numpy",
        ],
        tools=[find_papers, DuckDuckGoSearchTool(max_results=100, rate_limit=1)],
        max_steps=100,
        name="paper_locator",
        description="An agent that finds academic papers relevant to a given topic.",
    )

    paper_reader = CodeAgent(
        model=LiteLLMModel(
            model_id=model_id,
            api_base=api_base,
            api_key=api_key,
            temperature=1.0,
            max_tokens=100_000,
            stop=[],
        ),
        instructions=PAPER_READER_AGENT_SYSTEM_PROMPT.strip(),
        max_print_outputs_length=500_000,
        stream_outputs=stream,
        code_block_tags="markdown",
        additional_authorized_imports=[
            "os",
            "re",
            "json",
            "requests",
            "pandas",
            "numpy",
        ],
        tools=[parse_website],
        max_steps=100,
        name="paper_reader",
        description="An agent that reads and summarises academic papers.",
    )

    report_writer = CodeAgent(
        model=LiteLLMModel(
            model_id=model_id,
            api_base=api_base,
            api_key=api_key,
            temperature=0.3,
            max_tokens=10_000,
            stop=[],
        ),
        instructions=REPORT_WRITER_AGENT_SYSTEM_PROMPT.strip().format(
            today_date=dt.date.today().isoformat(), output_path=output_path.as_posix()
        ),
        max_print_outputs_length=50_000,
        stream_outputs=stream,
        code_block_tags="markdown",
        additional_authorized_imports=[
            "os",
            "re",
            "json",
            "requests",
            "pandas",
            "numpy",
        ],
        tools=[write_markdown_document_to_file, load_markdown_document_from_file],
        max_steps=100,
        name="report_writer",
        description="An agent that writes a literature survey report in Markdown.",
    )

    manager = CodeAgent(
        model=LiteLLMModel(
            model_id=model_id,
            api_base=api_base,
            api_key=api_key,
            temperature=0.3,
            max_tokens=1_000,
            stop=[],
        ),
        instructions=MANAGER_AGENT_SYSTEM_PROMPT,
        max_print_outputs_length=5_000,
        stream_outputs=stream,
        code_block_tags="markdown",
        additional_authorized_imports=[
            "os",
            "re",
            "json",
            "requests",
            "pandas",
            "numpy",
        ],
        managed_agents=[searcher, paper_reader, report_writer],
        tools=[final_answer],
        max_steps=100,
        name="manager",
        description="An agent that manages the literature survey process.",
    )

    return manager
