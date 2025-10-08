"""Data models used in the application."""

from pydantic import BaseModel


class Paper(BaseModel):
    """A research paper.

    Attributes:
        title:
            The title of the paper. Must be non-empty.
        authors:
            The authors of the paper. Must be a non-empty list.
        year:
            The year the paper was published. Must be between 1900 and the current year.
            Can be -1 if the year is unknown.
        venue:
            The venue where the paper was published, e.g., conference or journal name.
            Can be an empty string if the venue is unknown.
        url:
            The URL of the paper, preferably a DOI link. Must be a valid URL if
            provided. Can be an empty string if the URL is unknown.
        summary:
            The summary of the paper. Can be an empty string if it is unavailable.
    """

    title: str
    authors: list["Author"]
    year: int
    venue: str
    url: str
    summary: str

    def __eq__(self, other: object) -> bool:
        """Check if two Paper instances are equal based on their attributes.

        Args:
            other:
                The other Paper instance to compare with.

        Returns:
            True if the instances are equal, False otherwise.
        """
        if not isinstance(other, Paper):
            return False
        return (
            self.title == other.title
            and self.authors == other.authors
            and self.year == other.year
            and self.venue == other.venue
            and self.url == other.url
            and self.summary == other.summary
        )

    def __hash__(self) -> int:
        """Hash of the paper.

        Returns:
            The hash.
        """
        return hash(
            self.title
            + ",".join(author.first_name + author.last_name for author in self.authors)
            + str(self.year)
            + self.venue
            + self.url
            + self.summary
        )

    def __str__(self) -> str:
        """String representation of the paper.

        Returns:
            The string representation.
        """
        authors_str = ", ".join(
            f"{author.first_name} {author.last_name}".strip() for author in self.authors
        )
        year_str = str(self.year) if self.year != -1 else "Unknown Year"
        venue_str = self.venue if self.venue else "Unknown Venue"
        return f"""
            ## {self.title}

            **Authors:** {authors_str}
            **Year:** {year_str}
            **Venue:** {venue_str}
            **URL:** {self.url if self.url else "Unknown URL"}
            **Summary:** {self.summary if self.summary else "No summary available."}
        """.strip()


class Author(BaseModel):
    """An author of a research paper.

    Attributes:
        first_name:
            The author's first name. Can be an empty string if the first name is
            unknown.
        last_name:
            The author's last name. Can be an empty string if the last name is unknown.
    """

    first_name: str
    last_name: str

    def __eq__(self, other: object) -> bool:
        """Check if two Author instances are equal based on their attributes.

        Args:
            other:
                The other Author instance to compare with.

        Returns:
            True if the instances are equal, False otherwise.
        """
        if not isinstance(other, Author):
            return False
        return self.first_name == other.first_name and self.last_name == other.last_name


class Queries(BaseModel):
    """A list of queries to search for papers.

    Attributes:
        queries:
            A list of queries. Must be non-empty.
    """

    queries: list[str]

    def __post_init__(self) -> None:
        """Post-initialisation to make sure that the queries are correctly formatted."""
        # Remove empty queries and strip whitespace
        self.queries = [query.strip() for query in self.queries if query.strip()]

        # Split queries with "OR" statements into separate queries
        indices_with_or_statement = [
            i for i, query in enumerate(self.queries) if " OR " in query.lower()
        ]
        for i in indices_with_or_statement:
            or_query = self.queries.pop(i)
            subqueries = [subquery.strip() for subquery in or_query.split(" OR ")]
            self.queries.extend(subqueries)

        # Remove "AND" statements from queries
        self.queries = [query.replace(" AND ", " ") for query in self.queries]

        # Remove duplicate queries
        self.queries = list(set(self.queries))


class IsRelevant(BaseModel):
    """A response indicating whether a paper is relevant to a given topic.

    Attributes:
        is_relevant:
            True if the paper is relevant, False otherwise.
    """

    is_relevant: bool


class Summary(BaseModel):
    """A summary of a research paper.

    Attributes:
        summary:
            The summary text. Must be non-empty.
    """

    summary: str


class LiteLLMConfig(BaseModel):
    """Configuration for LiteLLM.

    Attributes:
        model:
            The model ID to use.
        base_url (optional):
            The API base URL for the model, if a custom inference server is used. Can be
            None if not needed. Defaults to None.
        api_key (optional):
            The environment variable name that contains the API key for the model. Can
            be None if not needed. Defaults to None.
    """

    model: str
    base_url: str | None = None
    api_key: str | None = None
