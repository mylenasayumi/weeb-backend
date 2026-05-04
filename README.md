# Weeb Backend

A Django REST API backend with machine learning capabilities, providing user management, article handling, like system and satisfaction tracking.
It also send email after creating user or while reseting your password.

[![Coverage](https://img.shields.io/badge/coverage-100%25-brightgreen)](https://github.com/mylenasayumi/weeb-backend)


## 🛠 Tech Stack

- **Framework**: Django with Django REST Framework
- **Database**: MySQL
- **Cache**: Redis
- **Containerization**: Docker & Docker Compose
- **ML Libraries**: Integrated machine learning tools
- **CORS**: Django CORS Headers for cross-origin requests
- **Version Control**: Git with Git LFS for large files

## 📦 Prerequisites

Before you begin, ensure you have the following installed:

- [Docker](https://docs.docker.com/get-docker/) (20.10+)
- [Docker Compose](https://docs.docker.com/compose/install/) (2.0+)
- [Git](https://git-scm.com/downloads)
- [Git LFS](https://git-lfs.github.com/)

### Git LFS Setup

```bash
# Install Git LFS
sudo apt install git-lfs

# Initialize Git LFS
git lfs install

# Pull LFS files
git lfs pull
```

## 🚀 Installation

1. **Clone the repository**
   ```bash
   git clone https://github.com/mylenasayumi/weeb-backend.git weeb-backend
   cd weeb-backend
   ```

2. **Verify Docker Compose installation**
   ```bash
   docker compose version
   ```
   If not installed, follow the [official documentation](https://docs.docker.com/compose/install/).

3. **Configure environment variables**
   ```bash
   cp .env.example .env
   ```
   Edit `.env` with your preferred settings:
   ```env
   MYSQL_DATABASE=weeb_database
   MYSQL_USER=weeb_user
   MYSQL_PASSWORD=your_secure_password
   MYSQL_ROOT_PASSWORD=your_root_password
   DATA_PATH= If you do not want to move everything use => "./data/"
   DEBUG=True => for dev False => for prod
   SECRET_KEY=YOUR_SECRET_DJANGO_KEY
   GITHUB_CLIENT_ID='Enter_your_id'
   GITHUB_CLIENT_SECRET='Enter_your_secret'
   GITHUB_CALLBACK_URL='Enter_your_callback_url'
   CORS_ALLOWED_ORIGINS="enter_frontend_url"
   EMAIL_HOST_USER="Enter_your_stmp_gmail_user"
   EMAIL_HOST_PASSWORD="Enter_your_stmp_gmail_password"
   REDIS_URL="REDIS_CACHE"
   ```

4. **Build and start services**
   ```bash
   docker compose build
   docker compose up
   ```

5. **Access the application**
   - API: `http://localhost:8000`
   - Wait for all services to complete initialization

## ⚙️ Configuration

### Default Fixtures

On first startup, the application automatically creates:
- **5 test users**
  - 1 Admin user: `username: admin` | `password: admin`
  - 4 Regular users: `password: Password12345@`
- **10 sample articles**
- **Graphs fixtures for backend**

### Data Storage

CSV files are stored in the directory specified by `DATA_PATH` in your `.env` file (default: `./data/`).

## 🎯 Usage

### Clean Dataframes and create new one

```bash
docker compose exec api python manage.py create_dataframes
```

### Create models

```bash
docker compose exec api python manage.py create_models
```

### Try it?

```bash
docker compose exec api python manage.py try_models
```


### Run Management Commands

```bash
docker compose exec api python manage.py <command>
```

## 🧪 Testing

### Run Tests

```bash
docker compose exec api pytest
```

### Generate Coverage Report

**Terminal output:**
```bash
docker compose exec api pytest  --cov --cov-report=term-missing
```

**HTML report:**
```bash
docker compose exec api coverage html
```
The HTML report will be available in the `htmlcov/` directory.

## 👨‍💻 Development Workflow

### Pre-commit Hooks

Install and run pre-commit hooks to ensure code quality:

```bash
# Install hooks
pre-commit install

# Run on all files
pre-commit run --all-files
```

### Git Workflow

1. **Create an Issue**
   - Add a clear description
   - Include images or links if necessary
   - Use appropriate labels

2. **Branch Naming Convention**
   ```
   <type>/<app>/<module>/<function>
   ```
   
   **Examples:**
   - `fix/user/views/helloWorld`
   - `feat/articles/serializers`
   - `delete/satisfactions/models`
   
   **Types:**
   - `fix`: Bug fixes
   - `feat`: New features
   - `delete`: Removing code/features
   - `refactor`: Code refactoring
   - `docs`: Documentation updates

3. **Pull Request Guidelines**
   - Link related issue(s)
   - Provide clear description of changes
   - Include tests for new features/fixes
   - Ensure all tests pass
   - Require approval before merging

## 📁 Backend Project Structure

```
weeb-backend/
├── users/              # User management app
│   ├── tests/
│   ├── fixtures/
│   ├── migrations/
│   ├── models.py
│   ├── views.py
│   ├── serializers.py
│   ├── throttling.py
│   ├── admin.py
│   ├── apps.py
│   ├── backend.py
│   ├── managers.py
│   └── tests.py
├── articles/           # Article management app
│   ├── tests/
│   ├── fixtures/
│   ├── models.py
│   ├── views.py
│   ├── apps.py
│   ├── admin.py
│   ├── permissions.py
│   └── serializers.py
├── satisfactions/      # Satisfaction tracking app
│   ├── tests/
│   ├── management/
│   ├── models.py
│   ├── apps.py
│   ├── admin.py
│   ├── views.py
│   └── serializers.py
├── likes/      # Like management app
│   ├── tests/
│   ├── models.py
│   ├── apps.py
│   ├── admin.py
│   ├── views.py
│   └── serializers.py
├── backend/      # Backend management app
│   ├── tests/
│   ├── fixtures/
│   ├── settings/
│   ├── static/
│   ├── wshi.py
│   ├── asgi.py
│   ├── urls.py
│   └── views.py
├── data/               # CSV storage directory
├── manage.py
├── docker-compose.yml
├── Dockerfile
├── requirements.txt
└── .env.example
```


## 🤝 Contributing

Contributions are welcome! Please follow the development workflow outlined above.

1. Fork the repository
2. Create a feature branch
3. Commit your changes
4. Push to your branch
5. Open a Pull Request

## 📧 Contact

For questions or support, please open an issue on GitHub.

---

**Note**: Remember to keep your `.env` file secure and never commit it to version control.