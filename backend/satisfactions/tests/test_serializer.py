import pytest
from rest_framework.exceptions import ValidationError


def test_validate_email_empty_failure(serializer):
    """
    Should raise ValidationError when email is empty.
    """
    with pytest.raises(ValidationError):
        serializer.validate_email("   ")


def test_validate_email_valid_failure(serializer):
    """
    Should return email when valid.
    """
    result = serializer.validate_email("test@example.com")
    assert result == "test@example.com"


def test_validate_description_empty_failure(serializer):
    """
    Should raise ValidationError when description is empty.
    """
    with pytest.raises(ValidationError):
        serializer.validate_description("   ")


def test_validate_description_too_small_failure(serializer):
    """
    Should raise ValidationError when description is too small.
    """
    with pytest.raises(ValidationError):
        serializer.validate_description("small")


def test_validate_bad_language(serializer):
    """
    Should raise ValidationError when description language is not supported.
    """
    with pytest.raises(ValidationError):
        serializer.validate({"description": "ich spreche deutch"})
