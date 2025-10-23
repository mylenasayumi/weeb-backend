# Weeb Backend

*Readme in progress...*

coverage
![Coverage](https://img.shields.io/badge/coverage-100%25-brightgreen)

# GIT LFS
sudo apt install git-lfs

git lfs install

git lfs pull



## INSTALLATION
1. Clone the repo.
```bash
    git clone https://github.com/mylenasayumi/weeb-backend.git <NAME_FOLDER>
```

2. Go to your new folder
```bash
    cd <NAME_FOLDER>
```

3. Check docker compose installation
```bash
    docker compose version
```
    If no installation go to:  https://docs.docker.com/compose/install/

4. Copy .env.example to .env
```bash
    cp .env.example .env
```

5. Change variables in .env
```bash
    example: MYSQL_DATABASE="My-awesome-database" ...
```

6. Start services with Docker Compose
```bash
    docker compose build && docker compose up
```

7. Wait until everything is completed and enjoy.

## Use coverage
1. Run this command
```bash
    docker compose exec api coverage run manage.py test
```

2. Need a report?
```bash
    docker compose exec api coverage report

    or

    docker compose exec api coverage html

```

docker compose exec api python manage.py create_ia


###
precommit
pre-commit install
pre-commit run --all-files

## Technologies
    -   Docker Compose
    -   Mysql
    -   Django
    -   Django Rest Framework
    -   Django Cors Headers
    -   Librairies Machine Learning

## Rules to follow
    1. Create Issue
        Add description + image or link if need to
    
    2. PR must start by fix/feat/delete
        must follow path of app 
            fix/user/
        must follow the file
            fix/user/views
        must follow the function if needed it
            fix/user/views/helloWorld
    
    3. Every PR should be approuved

    4. Always add test to PR

## Structure
    3 apps
        1. users
        2. articles
        3. satisfactions
        