"""Tools to use during agent execution."""

import logging

from scholarly import ProxyGenerator, scholarly
from smolagents import Tool, tool

logger = logging.getLogger("auto_survey")


def get_search_google_scholar_tool() -> Tool:
    """Get the Google Scholar search tool.

    Returns:
        The Google Scholar search tool.
    """
    # Set up a free proxy to avoid rate limiting
    logger.info("Setting up a proxy for searching Google Scholar...")
    proxy_generator = ProxyGenerator()
    proxy_generator.FreeProxies(timeout=1, wait_time=120)
    scholarly.use_proxy(proxy_generator=proxy_generator)
    logger.info("Proxy set up successfully.")

    @tool
    def search_google_scholar(
        query: str, year_low: int | None, year_high: int | None, num_results: int
    ) -> list[dict]:
        """Search Google Scholar for academic papers.

        Args:
            query:
                The search query.
            year_low:
                The lower bound of the publication year. Can be None to not have any
                lower bound.
            year_high:
                The upper bound of the publication year. Can be None to not have any
                upper bound.
            num_results:
                The number of results to return.

        Returns:
            A list of dictionaries containing the search results.
        """
        search_result_iterator = scholarly.search_pubs(
            query=query,
            year_low=year_low,  #  type: ignore
            year_high=year_high,  # type: ignore
        )
        search_results = [
            dict(next(search_result_iterator)) for _ in range(num_results)
        ]
        return search_results

    return search_google_scholar
