import pytest
from articles.models import Article
from django.contrib.auth import get_user_model
from rest_framework.test import APIClient
from satisfactions.models import Satisfaction
from satisfactions.serializers import SatisfactionSerializer

User = get_user_model()


@pytest.fixture
def user(db):
    """
    Fixture used to create and return a standard user.
    """
    return User.objects.create_user(
        email="john@example.com",
        password="pass12345",
        first_name="John",
        last_name="Doe",
    )


@pytest.fixture
def article(db, user):
    """
    Fixture used to create and return a standard article.
    """
    return Article.objects.create(
        title="Lorem ipsum dolor sit amet, consectetur adipiscing elit.",
        description="Quisque vitae felis vestibulum, auctor erat vitae, feugiat purus..",
        image="https://en.wikipedia.org/wiki/Lorem_ipsum#/media/File:Lorem_ipsum_design.svg",
        user=user,
    )


@pytest.fixture
def article2(db, user):
    """
    Fixture used to create and return a standard article different from the first one.
    """
    return Article.objects.create(
        title="Pellentesque blandit lacus eu porttitor euismod.",
        description="Etiam scelerisque ipsum sit amet consequat ornare.",
        image="https://en.wikipedia.org/wiki/Lorem_ipsum#/media/File:Lorem_ipsum_design.svg",
        user=user,
    )


@pytest.fixture
def satisfaction(db, user):
    """
    Fixture used to create and return a standard satisfaction.
    """
    return Satisfaction.objects.create(
        email="john@example.com",
        first_name="John",
        last_name="Doe",
        description="Great experience!",
        user=user,
        polarity=True,
    )


@pytest.fixture
def api_client():
    """
    Fixture used to create and return and instance of non auth Client
    """
    return APIClient()


@pytest.fixture
def authenticated_client(api_client, user):
    """
    Fixture using api_client() return a logged in user.
    """
    api_client.force_authenticate(user=user)
    return api_client


@pytest.fixture
def serializer():
    return SatisfactionSerializer(data={})
