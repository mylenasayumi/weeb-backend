#!/usr/bin/env bash

# Delete \r for Windows error vs Linux
sed -i 's/\r$//' "$0" 2>/dev/null || true

# Wait database
echo "Waiting for database..."
while ! nc -z db 3306; do
  sleep 1 # wait 1 second before checking again
done
echo "Database is ready!"

# Create migrations
python manage.py makemigrations

# Apply migrations
python manage.py migrate

# Load fixtures
python manage.py loaddata users/fixtures/users_fixtures.json || true
python manage.py loaddata articles/fixtures/articles_fixtures.json || true

# Checking if dataframes are missing
missing_dataframes=()

# English file
if ! find . -name "dataframe_en.csv" | grep -q .; then
    missing_files+=("dataframe_en.csv")
fi

# French file
if ! find . -name "dataframe_fr.csv" | grep -q .; then
    missing_files+=("dataframe_en.csv")
fi

if [ ${#missing_files[@]} -eq 0 ]; then
    echo "All dataframes are present!"
else
    echo "Missing dataframes: ${missing_files[*]} , generating them, can take a long time..."
    python -u manage.py create_dataframes
fi

# Checking if models are missing
models_dataframes=()

# English file
if ! find . -name "model_ia_en.pkl" | grep -q .; then
    models_dataframes+=("model_ia_en.kl")
fi

# French file
if ! find . -name "model_ia_fr.pkl" | grep -q .; then
    models_dataframes+=("model_ia_fr.pkl")
fi

if [ ${#models_dataframes[@]} -eq 0 ]; then
    echo "All models are present!"
else
    echo "Missing models: ${models_dataframes[*]} , generating them, can take a long time..."
    python -u manage.py create_models
fi


# Start server
python manage.py runserver 0.0.0.0:8000
