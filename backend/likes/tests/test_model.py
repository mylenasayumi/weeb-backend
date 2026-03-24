import pytest

pytestmark = pytest.mark.django_db


def test_like_str_success(article, user, like):
    """
    Should properly display like.__str__()
    """
    # ARRANGE
    expected_output = f"Like from: {user.email} on article: {article.title}"

    # ASSERT
    assert expected_output in like.__str__()
