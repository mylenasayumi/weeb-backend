import pytest
from users.backend import EmailBackend

pytestmark = pytest.mark.django_db


def test_authenticate_no_email():
    """
    Should returns None when no email is provided.
    """
    # ARRANGE
    backend = EmailBackend()

    # ACT
    user = backend.authenticate(request=None, username=None, password="test")

    # ASSERT
    assert None == user


def test_authenticate_wrong_password_failure(user):
    """
    Should return None when password is incorrect.
    """
    # ARRANGE
    backend = EmailBackend()

    # ACT
    result = backend.authenticate(
        request=None,
        email="john@example.com",
        password="wrongpassword",
    )

    # ASSERT
    assert result is None
