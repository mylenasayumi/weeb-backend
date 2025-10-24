#!/bin/bash

# Create migrations
python manage.py makemigrations

# Apply migrations
python manage.py migrate

# Add fixtures
python manage.py loaddata users/fixtures/users_fixtures.json || true
python manage.py loaddata articles/fixtures/articles_fixtures.json || true


# Start server
python manage.py runserver 0.0.0.0:8000