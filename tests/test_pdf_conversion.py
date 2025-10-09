"""Tests for the `pdf_conversion` module."""

import tempfile
from pathlib import Path

import pytest

from auto_survey.pdf_conversion import convert_markdown_file_to_pdf


@pytest.mark.parametrize(
    argnames=["markdown_content"],
    argvalues=[
        (
            "# Sample Document\n\n"
            "This is a sample document to test PDF conversion.\n\n"
            "## Section 1\n\n"
            "This is the first section.\n\n"
            "## Section 2\n\n"
            "This is the second section.",
        ),
        (
            "# 非ASCII字符测试\n\n"
            "这是一段包含非ASCII字符的文本，用于测试PDF转换功能。\n\n"
            "## 第一部分\n\n"
            "这是第一部分的内容。\n\n"
            "## 第二部分\n\n"
            "这是第二部分的内容。",
        ),
        ("",),
    ],
    ids=["basic_markdown", "markdown_with_non_ascii_characters", "empty_markdown"],
)
def test_convert_markdown_file_to_pdf(markdown_content: str) -> None:
    """Test the `convert_markdown_file_to_pdf` function."""
    with tempfile.TemporaryDirectory() as tmpdirname:
        markdown_path = Path(tmpdirname) / "test.md"
        markdown_path.write_text(markdown_content)

        success = convert_markdown_file_to_pdf(
            markdown_path=markdown_path, verbose=False
        )
        assert success, "PDF conversion failed"

        pdf_path = markdown_path.with_suffix(".pdf")
        assert pdf_path.exists(), "PDF file was not created"
        assert pdf_path.stat().st_size > 0, "PDF file is empty"
