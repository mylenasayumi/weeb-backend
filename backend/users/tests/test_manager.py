import pytest
from django.contrib.auth import get_user_model

User = get_user_model()
pytestmark = pytest.mark.django_db


def test_create_user_success(user):
    """
    Should return all informations used to create a user.
    """
    # ASSERT
    assert user.email == "john@example.com"
    assert user.check_password("pass12345") is True
    assert user.first_name == "John"
    assert user.last_name == "Doe"


def test_create_user_no_email_failure():
    """
    Should failed if email is missing.
    """
    # ASSERT
    expected_output = "Email is required"

    # ACT
    with pytest.raises(ValueError) as err:
        User.objects.create_user(
            email="", password="pass12345", first_name="John", last_name="Doe"
        )

    # ASSERT
    assert str(err.value) == expected_output


def test_create_user_no_pwd_failure():
    """
    Should failed if password is missing.
    """
    # ASSERT
    expected_output = "Password is required"

    # ACT
    with pytest.raises(ValueError) as err:
        User.objects.create_user(
            email="john@example.com",
            password="",
            first_name="John",
            last_name="Doe",
        )

    # ASSERT
    assert str(err.value) == expected_output


def test_create_user_no_first_name_failure():
    """
    Should failed if first name is missing.
    """
    # ASSERT
    expected_output = "First name is required"

    # ACT
    with pytest.raises(ValueError) as err:
        User.objects.create_user(
            email="john@example.com",
            password="pass12345",
            first_name="",
            last_name="Doe",
        )

    # ASSERT
    assert str(err.value) == expected_output


def test_create_user_no_last_name_failure():
    """
    Should failed if last name is missing.
    """
    # ASSERT
    expected_output = "Last name is required"

    # ACT
    with pytest.raises(ValueError) as err:
        User.objects.create_user(
            email="john@example.com",
            password="pass12345",
            first_name="John",
            last_name="",
        )

    # ASSERT
    assert str(err.value) == expected_output


def test_create_superuser_success():
    """
    Should create a superuser with the right permissions
    """
    # ACT
    superuser = User.objects.create_superuser(
        email="admin@example.com",
        password="pass12345",
        first_name="John",
        last_name="Doe",
    )

    # ASSERT
    assert superuser.is_staff is True
    assert superuser.is_superuser is True
    assert superuser.is_active is True
    assert superuser.email == "admin@example.com"


def test_create_superuser_not_staff_failure():
    """
    Should failed to create a superuser with bad permission.
    """
    # ARRANGE
    expected_output = "Superuser must have is_staff=True."

    # ACT
    with pytest.raises(ValueError) as err:
        User.objects.create_superuser(
            email="admin@example.com",
            password="adminpass",
            first_name="Admin",
            last_name="User",
            is_staff=False,
        )

    # ASSERT
    assert str(err.value) == expected_output


def test_create_superuser_not_super_failure():
    """
    Should failed to create a superuser with bad permission.
    """
    # ARRANGE
    expected_output = "Superuser must have is_superuser=True."

    # ACT
    with pytest.raises(ValueError) as err:
        User.objects.create_superuser(
            email="admin@example.com",
            password="adminpass",
            first_name="Admin",
            last_name="User",
            is_superuser=False,
        )

    # ASSERT
    assert str(err.value) == expected_output
