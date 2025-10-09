"""Writing up literature surveys."""

import logging
import re

from auto_survey.data_models import LiteLLMConfig, Paper
from auto_survey.llm import get_llm_completion

logger = logging.getLogger("auto_survey")


def write_literature_survey(
    topic: str, relevant_papers: list[Paper], litellm_config: LiteLLMConfig
) -> str:
    """Write a literature survey on a given topic using relevant papers.

    Args:
        topic:
            The topic to write the literature survey on.
        papers_with_summaries:
            A dictionary mapping relevant papers to their summaries.
        litellm_config:
            The LiteLLM configuration to use.

    Returns:
        The literature survey, as a Markdown string.
    """
    logger.info(f"Writing literature survey on topic {topic!r}...")

    system_prompt = """
        You are an expert academic researcher and writer.

        Your task is to write a literature survey on a given topic using the provided
        relevant papers. The literature survey should be well-structured, comprehensive,
        and written in clear, concise English.

        The literature survey should be formatted in Markdown, with appropriate
        headings, subheadings, and paragraphs. Rather than simply listing each paper
        summary one after the other, you should synthesise the information from the
        papers to provide a coherent overview of the topic.

        The survey should include:
        - An introduction to the topic (named "Introduction"), explaining its
          significance and context.
        - 2-3 main content sections, each with multiple paragraphs separated by double
          newlines, covering different aspects of the topic. Each section should
          synthesise information from multiple papers, highlighting information that is
          relevant to the topic.
        - A conclusion (named "Conclusion") that summarises the key points discussed in
          the survey.
        - A references section (named "References") that lists all the papers cited in
          the survey, formatted in APA style. This means that the references should be
          of the form "Author (Year)" or "(Author, Year)", depending on the sentence
          structure. If there are 2 authors use "Author1 and Author2 (Year)" or
          "(Author1 and Author2, Year)". If there are 3 or more authors use "Author1 et
          al. (Year)" or "(Author1 et al., Year)". All references in the References
          section should be separated by double newlines.
        - In the References section, the papers should be listed in alphabetical order
          by the surname of the first author, and then by year of publication (earliest
          first) for papers with the same first author.
        - All references in the References section must contain the authors, title of
          the paper, venue, year, and URL (if available).

        Return only the Markdown content of the literature survey, without any
        additional commentary or explanation.
    """.strip()

    papers_str = "\n\n".join(str(paper) for paper in relevant_papers)
    user_prompt = f"""
        Write a literature survey on the topic of {topic!r}, using the following
        relevant papers:

        <papers>
        {papers_str}
        </papers>
    """.strip()

    literature_survey = get_llm_completion(
        messages=[
            dict(role="system", content=system_prompt),
            dict(role="user", content=user_prompt),
        ],
        temperature=0.5,
        max_tokens=10_000,
        litellm_config=litellm_config,
        response_format=None,
    )

    # Check if all papers are cited at least once
    papers_missing_citations: list[Paper] = []
    for paper in relevant_papers:
        citation_in_parens = paper.get_citation(in_parens=True)
        citation_not_in_parens = paper.get_citation(in_parens=False)
        if (
            citation_in_parens not in literature_survey
            and citation_not_in_parens not in literature_survey
        ):
            papers_missing_citations.append(paper)

    # If there are any smissing citations, log a warning and remove them from the
    # references section
    papers_still_missing_citations: list[Paper] = []
    for paper in relevant_papers:
        citation_in_parens = paper.get_citation(in_parens=True)
        citation_not_in_parens = paper.get_citation(in_parens=False)
        if (
            citation_in_parens not in literature_survey
            and citation_not_in_parens not in literature_survey
        ):
            papers_still_missing_citations.append(paper)
    if papers_still_missing_citations:
        logger.debug(
            f"There are {len(papers_still_missing_citations)} papers that are not "
            "cited in the literature survey. These papers will be omitted from the "
            "references section."
        )
        content_part, references_part = literature_survey.rsplit("## References", 1)
        references_lines = references_part.strip().splitlines()

        lines_to_remove = set()
        for paper in papers_still_missing_citations:
            line_idxs = [
                i
                for i, line in enumerate(references_lines)
                if re.search(rf"\b{re.escape(paper.title)}\b", line)
            ]
            lines_to_remove.update(line_idxs)
        references_lines = [
            line for i, line in enumerate(references_lines) if i not in lines_to_remove
        ]

        corrected_references_part = re.sub(
            r"\n{2,}", "\n\n", "\n".join(references_lines)
        ).strip()

        literature_survey = (
            content_part.strip() + "\n\n## References\n\n" + corrected_references_part
        )

    return literature_survey
