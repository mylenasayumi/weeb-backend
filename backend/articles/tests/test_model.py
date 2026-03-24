import pytest

pytestmark = pytest.mark.django_db


def test_article_str_success(article):
    """
    Should properly display article.__str__()
    """
    # ARRANGE
    expected_output = "title: Lorem ipsum dolor sit amet, consectetur adipiscing elit."

    # ASSERT
    assert expected_output in article.__str__()
