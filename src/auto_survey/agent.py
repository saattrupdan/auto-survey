"""Agents used within the application."""

import logging

from smolagents import CodeAgent, LiteLLMModel, VisitWebpageTool, WebSearchTool

from auto_survey.tools import search_google_scholar

logger = logging.getLogger("auto_survey")


LITERATURE_SURVEY_AGENT_SYSTEM_PROMPT = """
You are an expert research assistant specialising in conducting literature surveys.

Your task is to help users find and summarise relevant academic papers based on what
they are currently researching.

This is no small task, and you are expected to be thorough and methodical in your
approach. A literature survey should end with a comprehensive report in Markdown that
includes all relevant papers and a summary of how they relate to the user's research.
The report should be well-structured and written in a coherent story, rather than simply
listing all the papers. Use [1], [2], etc. to refer to papers in your summaries, and
include a references section at the end, formatted in APA style.

To help you find the papers, you can search academic databases such as Google Scholar
and ArXiv, as well as general web searches.
""".strip()


def get_literature_survey_agent(
    model_id: str, api_base: str | None, api_key: str | None
) -> CodeAgent:
    """Create an agent that conducts literature reviews.

    Args:
        model_id:
            The model ID to use.
        api_base:
            The API base URL for the model. Can be None if not needed.
        api_key:
            The API key for the model. Can be None if not needed.

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
        instructions=LITERATURE_SURVEY_AGENT_SYSTEM_PROMPT,
        max_print_outputs_length=500,
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
            search_google_scholar,
            WebSearchTool(max_results=10, engine="duckduckgo"),
            VisitWebpageTool(max_output_length=40_000),
        ],
        max_steps=1000,
    )
    return agent
