import pytest

pytestmark = pytest.mark.django_db


def test_satisfcation_str_success(satisfaction):
    """
    Should properly display satisfaction.__str__()
    """
    # ARRANGE
    expected_output = f"Satisfaction Form: {satisfaction.first_name} {satisfaction.last_name} sent a satisfaction comment on {satisfaction.created_at}."

    # ASSERT
    assert expected_output in satisfaction.__str__()
