## PROD ONLY

# Create migrations && Apply migrations
python manage.py makemigrations
python manage.py migrate

# Load fixtures
python manage.py loaddata users/fixtures/users_fixtures.json || true
python manage.py loaddata articles/fixtures/articles_fixtures.json || true


### Checking if dataframes are missing
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


### Checking if models are missing
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

# Start server -- STIL TESTING
echo "Starting Gunicorn..."
exec gunicorn backend.wsgi:application -b 0.0.0.0:10000
# exec gunicorn backend:app -k uvicorn.workers.UvicornWorker --bind 0.0.0.0:${PORT:-8000} --workers 4 --timeout 120
