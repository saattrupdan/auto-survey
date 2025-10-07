"""Agents used within the application."""

import datetime as dt
import logging
from pathlib import Path

from smolagents import CodeAgent, DuckDuckGoSearchTool, LiteLLMModel

from auto_survey.tools import (
    count_words,
    final_answer,
    find_papers,
    load_markdown_document_from_file,
    parse_website,
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
2. It must contain data from at least 10 academic papers.
3. All references follow the APA format, meaning that inline citations are either of the
   form "Author (Year)" or "(Author, Year)", whichever is more appropriate in the
   context. If there are one or two authors than both should be listed, otherwise use
   "Author et al. (Year)" or "(Author et al., Year)". Only use the last names of the
   authors.
4. There is a references section (## References) at the end of the report in APA style,
   with double newlines between references. The references in this section have to
   contain all the authors (no "et al." required here), the year, the title, the venue
   (e.g., conference or journal name), and a link to the paper (prefer DOI links where
   possible). If the reference is to a webpage, include the title, the author (if
   available), the year (if available), the URL, and the date you accessed the page
   (today's date is {today_date}).
5. Each claim in the report should be backed up by at least one reference, which must
   appear in the References section.
6. The report should be well-structured and written in a coherent story, rather than
   simply listing all the papers or being overly to-the-point.
7. When you are done with your report, you should save it to the {output_path!r} file.
   Use your tool to save the report, do not write the file directly yourself.

Use your tools to find academic papers that are relevant to the user's request.

You can also search the web for relevant webpages to complement the academic papers.
Note that you can limit your search to a specific site with the "site:" operator, e.g.,
"<query> site:scholar.google.com", "<query> site:arxiv.org", "<query> site:biorxiv.org"
and so on.

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
            output_path=output_path.as_posix(), today_date=dt.date.today().isoformat()
        ),
        max_print_outputs_length=100_000,
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
            find_papers,
            parse_website,
            write_markdown_document_to_file,
            load_markdown_document_from_file,
            count_words,
            DuckDuckGoSearchTool(max_results=100, rate_limit=1),
            final_answer,
        ],
        max_steps=1000,
    )
    return agent
