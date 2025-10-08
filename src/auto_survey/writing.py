"""Writing up literature surveys."""

import logging

import litellm
from litellm.types.utils import ModelResponse

from auto_survey.data_models import LiteLLMConfig, Paper

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
    papers_str = "\n\n".join(str(paper) for paper in relevant_papers)
    response = litellm.completion(
        messages=[
            dict(
                role="system",
                content="""
                You are an expert academic researcher and writer.

                Your task is to write a literature survey on a given topic using the
                provided relevant papers. The literature survey should be
                well-structured, comprehensive, and written in clear, concise English.

                The literature survey should be formatted in Markdown, with appropriate
                headings, subheadings, and paragraphs.

                The survey should include:
                - An introduction to the topic, explaining its significance and context.
                - 1-3 sections, each with several paragraphs, covering different aspects
                  of the topic. Each section should synthesise information from multiple
                  papers, highlighting information that is relevant to the topic.
                - A conclusion that summarises the key points discussed in the survey
                  and suggests potential directions for future research.
                - References to the provided papers, formatted in APA style, meaning
                  that the references should be of the form "Author (Year)" or
                  "(Author, Year)", depending on the sentence structure. If there are 2
                  authors use "Author1 and Author2 (Year)" or "(Author1 and Author2,
                  Year)". If there are 3 or more authors use "Author1 et al. (Year)" or
                  "(Author1 et al., Year)". All references should be separated by double
                  newlines.
                - All papers should be cited at least once in the survey.

                  Return only the Markdown content of the literature survey, without any
                  additional commentary or explanation.
                """.strip(),
            ),
            dict(
                role="user",
                content=f"""
                Write a literature survey on the topic of {topic!r}, using the following
                relevant papers:

                <papers>
                {papers_str}
                </papers>
                """.strip(),
            ),
        ],
        temperature=0.5,
        max_tokens=10_000,
        **litellm_config.model_dump(),
    )
    assert isinstance(response, ModelResponse)
    choice = response.choices[0]
    assert isinstance(choice, litellm.Choices)
    survey = choice.message.content or ""
    return survey
