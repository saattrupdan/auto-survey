"""Tests for the `writing` module."""

import pytest

from auto_survey.data_models import Author, Paper
from auto_survey.writing import correct_references


@pytest.mark.parametrize(
    argnames=["literature_survey", "papers", "expected_literature_survey"],
    argvalues=[
        (
            "# Literature Survey on Test-Driven Development\n\n"
            "This is a dummy literature survey that cites some papers.\n\n"
            "There is Author1 (2020) and also the other one (Author2 et al., 2021).\n\n"
            "## References\n\n"
            "Just a silly reference section with nothing in it.",
            [
                Paper(
                    title="Test-Driven Development",
                    authors=[Author(first_name="First", last_name="Author1")],
                    year=2020,
                    venue="Journal of Testing",
                    url="http://example.com/tdd",
                    summary="A paper about TDD.",
                ),
                Paper(
                    title="Another Paper",
                    authors=[
                        Author(first_name="Second", last_name="Author2"),
                        Author(first_name="Third", last_name="Author3"),
                        Author(first_name="Fourth", last_name="Author4"),
                    ],
                    year=2021,
                    venue="Conference on Testing",
                    url="http://example.com/another",
                    summary="Another relevant paper.",
                ),
                Paper(
                    title="Unused Paper",
                    authors=[Author(first_name="Fifth", last_name="Author5")],
                    year=2019,
                    venue="Old Journal",
                    url="http://example.com/unused",
                    summary="An unused paper.",
                ),
            ],
            "# Literature Survey on Test-Driven Development\n\n"
            "This is a dummy literature survey that cites some papers.\n\n"
            "There is Author1 (2020) and also the other one (Author2 et al., 2021).\n\n"
            "## References\n\n"
            "Author1, First (2020). Test-Driven Development. _Journal Of Testing_.\n\n"
            "Author2, Second and Author3, Third and Author4, Fourth (2021). Another "
            "Paper. _Conference On Testing_.",
        )
    ],
    ids=["basic_test_case"],
)
def test_correct_references(
    literature_survey: str, papers: list[Paper], expected_literature_survey: str
) -> None:
    """Test the `correct_references` function."""
    corrected_survey = correct_references(
        literature_survey=literature_survey, papers=papers
    )
    assert corrected_survey == expected_literature_survey
