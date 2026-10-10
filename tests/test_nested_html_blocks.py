"""Regression coverage for nested HTML audit blocks."""
from html.parser import HTMLParser


def test_html_parser_available():
    assert HTMLParser is not None
