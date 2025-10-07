"""Agents used within the application."""

import logging
from pathlib import Path

from smolagents import CodeAgent, DuckDuckGoSearchTool, LiteLLMModel, VisitWebpageTool

from auto_survey.tools import (
    fetch_pdf_as_markdown,
    final_answer,
    load_markdown_document_from_file,
    write_markdown_document_to_file,
)

logger = logging.getLogger("auto_survey")


LITERATURE_SURVEY_AGENT_SYSTEM_PROMPT = """
You are an expert research assistant specialising in conducting literature surveys.

Your task is to help users find and summarise relevant academic papers based on what
the users are requesting, and to write a comprehensive report to the user in Markdown
format.

The report has the following requirements:

1. It should be at least 5 pages long (at least 2,500 words).
2. Each claim in the report should be backed up by at least one reference to a relevant
   paper.
3. All references follow the APA format, meaning that inline citations are either of the
   form "Author (Year)" or "(Author, Year)", whichever is more appropriate in the
   context.
4. There is a references section (## References) at the end of the report in APA style,
   with double newlines between references. References have to contain all the authors,
   the year, the title, the venue (e.g., conference or journal name), and a link to the
    paper (prefer DOI links where possible).
5. The report should be well-structured and written in a coherent story, rather than
   simply listing all the papers or being overly to-the-point.
6. When you are done with your report, you should save it to the {output_path!r} file.

You can search the web for relevant papers, visit webpages, and fetch and read
academic papers in PDF format. You should prioritise academic papers from reputable
sources over random webpages.

Before you start writing the report, make sure to plan out the structure of the report
and the key points you want to cover.

Your final answer should be the path to the Markdown file containing the report.
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
    output_path.unlink(missing_ok=True)
    model = LiteLLMModel(
        model_id=model_id,
        api_base=api_base,
        api_key=api_key,
        temperature=0.3,
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
            fetch_pdf_as_markdown,
            write_markdown_document_to_file,
            load_markdown_document_from_file,
            DuckDuckGoSearchTool(max_results=10, rate_limit=1),
            VisitWebpageTool(max_output_length=40_000),
            final_answer,
        ],
        max_steps=1000,
    )
    return agent
