import pytest

pytestmark = pytest.mark.django_db


def test_get_str_success(user):
    """
    Test __str__ method returns correct string.
    """
    expected_output = f"User email: {user.email}, created at: {user.created_at}"

    assert expected_output in user.__str__()
    assert "john@example.com" in expected_output
