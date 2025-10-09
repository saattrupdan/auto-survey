"""Searching for papers."""

import logging
import os
import time

import httpx
from tqdm.auto import tqdm

from auto_survey.data_models import Author, IsRelevant, LiteLLMConfig, Paper, Queries
from auto_survey.llm import get_llm_completion

logger = logging.getLogger("auto_survey")


def get_all_papers(
    topic: str,
    min_num_relevant_papers: int,
    batch_size: int,
    litellm_config: LiteLLMConfig,
) -> list[Paper]:
    """Get a list of relevant papers on a given topic.

    Args:
        topic:
            The topic to search for.
        min_num_relevant_papers:
            The minimum number of relevant papers to find.
        batch_size:
            The number of papers to fetch in each batch.
        litellm_config:
            The LiteLLM configuration to use.

    Returns:
        A list of relevant papers.
    """
    queries = get_list_of_queries(
        topic=topic, num_queries=10, litellm_config=litellm_config
    )

    logger.info("Searching for papers...")
    offset = 0
    relevant_papers: list[Paper] = list()
    with tqdm(
        total=min_num_relevant_papers, desc="Relevant papers found", unit="paper"
    ) as pbar:
        while len(relevant_papers) < min_num_relevant_papers and queries:
            for query in queries:
                # Find papers for the current query. If this returns None, it means that
                # the offset is too high, so we remove the query from the list of
                # queries.
                papers = find_papers(query=query, num_results=batch_size, offset=offset)
                if papers is None:
                    queries.remove(query)
                    continue

                # Remove already found relevant papers
                papers = [paper for paper in papers if paper not in relevant_papers]

                # Check if the papers are relevant, and keep only the relevant ones
                new_relevant_papers = [
                    paper
                    for paper in papers
                    if is_relevant_paper(
                        paper=paper, topic=topic, litellm_config=litellm_config
                    )
                ]
                if new_relevant_papers:
                    relevant_papers.extend(new_relevant_papers)
                    pbar.update(
                        len(new_relevant_papers)
                        - max(len(relevant_papers) - min_num_relevant_papers, 0)
                    )

                # Stop if we have found enough relevant papers
                if len(relevant_papers) >= min_num_relevant_papers:
                    break

            # Raise the offset to keep searching for papers with the same queries
            offset += batch_size

    logger.info(f"Found a total of {len(relevant_papers):,} relevant papers.")
    return relevant_papers


def get_list_of_queries(
    topic: str, num_queries: int, litellm_config: LiteLLMConfig
) -> list[str]:
    """Generate a list of queries to search for papers on a given topic.

    Args:
        topic:
            The topic to generate queries for.
        num_queries:
            The number of queries to generate.
        litellm_config:
            The LiteLLM configuration to use.

    Returns:
        A list of queries.
    """
    logger.info(f"Generating {num_queries} search queries for the topic {topic!r}...")

    system_prompt = """
        You are an expert academic researcher. Your task is to generate a list of
        concise search queries that can be used to find academic papers related to a
        given topic. The queries should be specific enough to yield relevant results,
        but not so specific that they miss important papers. Each query should be a
        single line of text. Do not use 'OR' or 'AND' statements in the queries.
    """.strip()

    user_prompt = f"""
        Generate a list of exactly {num_queries} concise search queries to find academic
        papers related to the following topic: {topic!r}. Return the queries as a JSON
        object with a single key 'queries' mapping to a list of strings.
    """.strip()

    completion = get_llm_completion(
        messages=[
            dict(role="system", content=system_prompt),
            dict(role="user", content=user_prompt),
        ],
        temperature=0.5,
        max_tokens=256,
        response_format=Queries,
        litellm_config=litellm_config,
    )
    queries = Queries.model_validate_json(json_data=completion).queries

    queries_str = "\n".join(f"- {query}" for query in queries)
    logger.info(f"Generated {len(queries)} queries:\n{queries_str}")
    return queries


def is_relevant_paper(paper: Paper, topic: str, litellm_config: LiteLLMConfig) -> bool:
    """Determine if a paper is relevant to a given topic.

    Args:
        paper:
            The paper to evaluate.
        topic:
            The topic to evaluate relevance against.
        litellm_config:
            The LiteLLM configuration to use.

    Returns:
        True if the paper is relevant, False otherwise.
    """
    system_prompt = """
        You are an expert academic researcher. Your task is to determine whether a given
        academic paper is relevant to a specified topic. If it is not directly relevant
        to the topic, but is related to a closely related topic, consider it relevant.

        You will be provided with the title and summary of the paper, as well as the
        topic. Your response should be a JSON object with a single key 'is_relevant'
        mapping to a boolean value: true if the paper is relevant to the topic, false
        otherwise.
    """.strip()

    user_prompt = f"""
        Determine if the following paper is relevant to the topic {topic!r}. Return your
        answer as a JSON object with a single key 'is_relevant' mapping to a boolean
        value.

        <paper>
        {paper.model_dump_json()}
        </paper>
    """.strip()

    completion = get_llm_completion(
        messages=[
            dict(role="system", content=system_prompt),
            dict(role="user", content=user_prompt),
        ],
        temperature=0.0,
        max_tokens=32,
        response_format=IsRelevant,
        litellm_config=litellm_config,
    )
    relevant = IsRelevant.model_validate_json(json_data=completion).is_relevant
    return relevant


def find_papers(query: str, num_results: int, offset: int = 0) -> list["Paper"] | None:
    """Find academic papers related to a query.

    Args:
        query:
            The query to search for.
        num_results:
            The number of results to return.
        offset (optional):
            Used for pagination. When returning a list of results, start with the
            element at this position in the list. Defaults to 0.

    Returns:
        A list of dictionaries containing the title, URL, year and authors of the
        papers found. Can also be None if the request is invalid (e.g., too high
        offset).

    Raises:
        httpx.HTTPStatusError:
            If the API returns a non-200 status code.
    """
    while True:
        response = httpx.get(
            url="https://api.semanticscholar.org/graph/v1/paper/search",
            params=dict(
                query=query,
                fields="title,authors,year,publicationVenue,openAccessPdf,abstract",
                limit=num_results,
                offset=offset,
            ),
            headers={
                "User-Agent": (
                    "Mozilla/5.0 (Macintosh; Intel Mac OS X 10.15; rv:143.0) "
                    "Gecko/20100101 Firefox/143.0"
                ),
                "x-api-key": os.getenv("SEMANTIC_SCHOLAR_API_KEY", ""),
            },
            timeout=30,
            follow_redirects=True,
        )
        if response.status_code == 429:
            logger.debug(
                "Rate limit exceeded when querying Semantic Scholar API. "
                "Waiting 10 seconds before retrying..."
            )
            time.sleep(10)
            continue
        elif response.status_code == 400:
            if "this limit and/or offset is not available" in response.text.lower():
                return None
            logger.error(
                f"Bad request when querying Semantic Scholar API: {response.text}"
            )
            return []
        break
    response.raise_for_status()
    results = response.json()
    if results is None:
        return []
    results = results.get("data") or list()

    papers = [
        Paper(
            title=result.get("title") or "",
            authors=[
                Author(
                    first_name=author["name"].split(" ")[0],
                    last_name=author["name"].split(" ")[-1],
                )
                for author in result.get("authors") or list()
                if author is not None
            ],
            year=result.get("year") or -1,
            venue=(result.get("publicationVenue") or dict()).get("name") or "",
            url=(result.get("openAccessPdf") or dict()).get("url") or "",
            summary=result.get("abstract") or "",
        )
        for result in results
        if result is not None
    ]
    return papers
