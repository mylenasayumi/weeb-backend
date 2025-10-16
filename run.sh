#!/bin/bash

# Activate virtual env
source env/bin/activate

# Move to backend project
cd backend || exit

# Create migrations
python manage.py makemigrations

# Apply migrations
python manage.py migrate

# Start server
python manage.py runserver