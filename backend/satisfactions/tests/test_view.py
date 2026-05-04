import os
from unittest.mock import patch

import pytest
from django.urls import reverse
from rest_framework import status
from satisfactions.models import Satisfaction

pytestmark = pytest.mark.django_db


@pytest.mark.skipif(
    os.getenv("CI") == "true", reason="Skip test because no pkl files are pushed"
)
@patch("satisfactions.serializers.detect", return_value="fr")
def test_create_satisfaction_fr_success(mock_detect, authenticated_client):
    """
    Should create a new satisfaction form when valid data is provided.
    """
    # ARRANGE
    data = {
        "description": "je parle français et ça marche",
        "email": "user@user.com",
        "first_name": "user",
        "last_name": "user",
    }
    list_url = reverse("satisfactions_create")

    # ACT
    response = authenticated_client.post(list_url, data=data, format="json")

    # ASSERT
    assert response.status_code == status.HTTP_201_CREATED
    assert Satisfaction.objects.count() == 1


@pytest.mark.skipif(
    os.getenv("CI") == "true", reason="Skip test because no pkl files are pushed"
)
@patch("satisfactions.serializers.detect", return_value="en")
def test_create_satisfaction_en_success(mock_detect, authenticated_client):
    """
    Should create a new satisfaction form when valid data is provided.
    """
    # ARRANGE
    data = {
        "description": "I love you, you are so beautiful",
        "email": "user@user.com",
        "first_name": "user",
        "last_name": "user",
    }
    list_url = reverse("satisfactions_create")

    # ACT
    response = authenticated_client.post(list_url, data=data, format="json")

    # ASSERT
    assert response.status_code == status.HTTP_201_CREATED
    assert Satisfaction.objects.count() == 1


@pytest.mark.skipif(
    os.getenv("CI") == "true", reason="Skip test because no pkl files are pushed"
)
@patch("satisfactions.serializers.detect", return_value="fr")
@patch("satisfactions.serializers.os.path.isfile", return_value=False)
def test_create_satisfaction_missing_model_fr_failure(
    mock_isfile, mock_detect, authenticated_client
):
    """
    Should return 400 if the model file is missing for French language.
    """
    # ARRANGE
    data = {
        "description": "je parle français et ça marche",
        "email": "user@user.com",
        "first_name": "user",
        "last_name": "user",
    }
    list_url = reverse("satisfactions_create")

    # ACT
    response = authenticated_client.post(list_url, data=data, format="json")

    # ASSERT
    assert response.status_code == status.HTTP_400_BAD_REQUEST
    assert "Sorry we can not know" in str(response.data)


@pytest.mark.django_db
@pytest.mark.skipif(
    os.getenv("CI") == "true", reason="Skip test because no pkl files are pushed"
)
@patch("satisfactions.serializers.detect", return_value="en")
@patch("satisfactions.serializers.os.path.isfile", return_value=False)
def test_create_satisfaction_missing_model_en_failure(
    mock_isfile, mock_detect, authenticated_client
):
    """
    Should return 400 if the model file is missing for English language.
    """
    # ARRANGE
    data = {
        "description": "Bryan is in the kitchen",
        "email": "user@user.com",
        "first_name": "user",
        "last_name": "user",
    }
    list_url = reverse("satisfactions_create")

    # ACT
    response = authenticated_client.post(list_url, data=data, format="json")

    # ASSERT
    assert response.status_code == status.HTTP_400_BAD_REQUEST
    assert "Sorry we can not know" in str(response.data)
