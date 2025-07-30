# Co-Optimal Backend

A FastAPI-based backend application with PostgreSQL database integration, Docker support, and thread-safe connection pooling.

## 📋 Table of Contents

- [Project Overview](#-project-overview)
- [Architecture](#-architecture)
- [Project Structure](#-project-structure)
- [Prerequisites](#-prerequisites)
- [Project Setup](#-project-setup)
- [Docker Setup](#-docker-setup)
- [Running the Application](#-running-the-application)
- [Database Migrations](#-database-migrations)
- [API Documentation](#-api-documentation)
- [Development Workflow](#-development-workflow)
- [Configuration](#-configuration)
- [Troubleshooting](#-troubleshooting)
- [Contributing](#-contributing)

## 🎯 Project Overview

Co-Optimal Backend is a modern, production-ready FastAPI application designed for scalability and maintainability. It features:

- **FastAPI Framework**: High-performance, automatic API documentation
- **PostgreSQL Integration**: Robust database with connection pooling
- **Docker Containerization**: Consistent deployment across environments
- **Poetry Dependency Management**: Modern Python packaging and dependency resolution
- **Thread-Safe Architecture**: Handles concurrent requests efficiently
- **Environment-Based Configuration**: Flexible configuration management
- **Alembic Migrations**: Database schema version control
- **New Relic Monitoring**: Application performance monitoring

## 🏗️ Architecture

### System Architecture
```
┌─────────────────┐    ┌─────────────────┐    ┌─────────────────┐
│   Client Apps   │    │   Load Balancer │    │   Monitoring    │
│                 │    │   (Optional)    │    │   & Logging     │
└─────────┬───────┘    └─────────┬───────┘    └─────────────────┘
          │                      │                      ▲
          └──────────────────────┼──────────────────────┘
                                 │
                    ┌─────────────▼───────────────┐
                    │     FastAPI Application     │
                    │   ┌─────────────────────┐   │
                    │   │  Gunicorn Server    │   │
                    │   │  + Uvicorn Workers  │   │
                    │   └─────────────────────┘   │
                    │   ┌─────────────────────┐   │
                    │   │ Connection Pool     │   │
                    │   │ (Thread-Safe)       │   │
                    │   └─────────────────────┘   │
                    └─────────────┬───────────────┘
                                  │
                    ┌─────────────▼───────────────┐
                    │    PostgreSQL Database      │
                    │  ┌─────────────────────┐    │
                    │  │   Data Persistence  │    │
                    │  │   + Health Checks   │    │
                    │  └─────────────────────┘    │
                    └─────────────────────────────┘
```

### Component Architecture
```
FastAPI Application
├── API Layer (FastAPI Routes)
├── Business Logic Layer
├── Data Access Layer (SQLAlchemy/Raw SQL)
├── Configuration Management
└── Connection Pool Management

PostgreSQL Database
├── Connection Pool (1-10 connections)
├── Health Monitoring
└── Data Persistence
```

### Network Architecture
```
Docker Network: co_optimal
├── co-optimal-postgres:5432 (PostgreSQL)
└── co_optimal_api:8000 (FastAPI)

Host Machine
├── localhost:5432 → PostgreSQL
└── localhost:8000 → FastAPI API
```

## 📁 Project Structure

```
co-optimal/
├── 📁 co_optimal/                     # Main application package
│   ├── 📁 config/                     # Configuration management
│   │   ├── __init__.py                # Logging setup
│   │   └── 📁 v1/                     # Version 1 configurations
│   │       ├── __init__.py            # Base settings wrapper
│   │       ├── api_config.py          # FastAPI configuration
│   │       ├── database_config.py     # PostgreSQL configuration
│   │       ├── authentication_config.py # Auth settings
│   │       ├── llm_config.py          # LLM provider settings
│   │       └── logging.conf           # Logging configuration
│   │
│   ├── 📁 core/                       # Core application components
│   │   ├── __init__.py                # Core module initialization
│   │   └── fastapi_blueprints.py     # API route blueprints
│   │
│   ├── 📁 utils/                      # Utility modules
│   │   └── 📁 v1/                     # Version 1 utilities
│   │       ├── connections.py         # Database connection pool
│   │       └── generic_helper.py      # Singleton and helpers
│   │
│   ├── 📁 models/                     # Data models and schemas
│   │   └── (model files)             # Pydantic/SQLAlchemy models
│   │
│   ├── 📁 datafiles/                  # Application data storage
│   │   └── (uploaded files)          # File uploads, temp data
│   │
│   ├── 📁 scripts/                    # Utility scripts
│   │   └── (helper scripts)          # Database scripts, etc.
│   │
│   ├── 📁 test/                       # Test files
│   │   └── (test files)              # Unit and integration tests
│   │
│   ├── fastapi_application.py         # Main FastAPI application
│   ├── __init__.py                    # Package initialization
│   ├── .env.sample                    # Environment template
│   └── .env                           # Environment variables (local)
│
├── 📁 dockerfiles/                    # Docker configuration
│   ├── Dockerfile.co_optimal          # Application container
│   └── docker-compose.co_optimal.yml  # FastAPI service
│
├── 📁 alembic/                        # Database migrations
│   ├── versions/                      # Migration files
│   ├── env.py                         # Alembic environment
│   ├── script.py.mako                 # Migration template
│   └── alembic.ini                    # Alembic configuration
│
├── 📄 pyproject.toml                  # Poetry configuration
├── 📄 poetry.lock                     # Locked dependencies
├── 📄 Makefile                        # Build automation
├── 📄 .gitignore                      # Git ignore rules
│
├── 📚 Documentation/
│   ├── README.md                      # This file
│   ├── DOCKERFILE.md                  # Docker setup guide
│   ├── POETRY_SETUP.md               # Poetry setup guide
│   └── ALEMBIC_MIGRATIONS.md         # Database migration guide
│
└── 📁 .git/                          # Git repository
```

### Component Description

#### 🔧 **Core Components**
- **`fastapi_application.py`**: Main application entry point, FastAPI instance
- **`core/fastapi_blueprints.py`**: API route organization and blueprints
- **`utils/v1/connections.py`**: Thread-safe PostgreSQL connection pool

#### ⚙️ **Configuration System**
- **`config/v1/`**: Modular configuration system
  - `api_config.py`: FastAPI and server settings
  - `database_config.py`: PostgreSQL connection parameters
  - `authentication_config.py`: Authentication providers
  - `llm_config.py`: Language model configurations

#### 🐳 **Docker Infrastructure**
- **`Dockerfile.co_optimal`**: Multi-layer application container
- **`docker-compose.co_optimal.yml`**: FastAPI service definition

#### 📦 **Dependency Management**
- **`pyproject.toml`**: Poetry configuration, dependencies
- **`poetry.lock`**: Locked dependency versions for reproducibility

## 🔧 Prerequisites

### System Requirements
- **Python**: 3.13.2+ (as specified in pyproject.toml)
- **Docker**: Latest stable version
- **Docker Compose**: v2.0+
- **Poetry**: Latest version
- **Make**: For build automation (Windows: Git Bash or WSL)

### Recommended Tools
- **Database Client**: pgAdmin, DBeaver, or psql
- **API Testing**: Postman, Insomnia, or curl
- **Code Editor**: VS Code, PyCharm, or similar

## 🚀 Project Setup

### Method 1: Complete Setup (Recommended)

#### 1. **Clone and Navigate**
```bash
git clone <repository-url>
cd co-optimal
```

#### 2. **Install Poetry**
```powershell
# Windows PowerShell
(Invoke-WebRequest -Uri https://install.python-poetry.org -UseBasicParsing).Content | python -

# macOS/Linux
curl -sSL https://install.python-poetry.org | python3 -

# Verify installation
poetry --version
```

#### 3. **Setup Python Environment**
```bash
# Set Python version (3.13.2 as specified in pyproject.toml)
poetry env use 3.13.2

# Install dependencies
poetry install

# Activate environment
poetry shell
```

#### 4. **Configure Environment**
```bash
# Copy environment template
cp co_optimal/.env.sample co_optimal/.env

# Edit configuration (adjust as needed)
# co_optimal/.env
```

#### 5. **Start Services**
```bash
# Option A: Using Make (recommended)
make start-co_optimal

# Option B: Manual Docker commands
make build-co_optimal
```

### Method 2: Docker-Only Setup

If you prefer Docker-only development:

```bash
# Clone repository
git clone <repository-url>
cd co-optimal

# Setup environment
cp co_optimal/.env.sample co_optimal/.env

# Start everything
make start-co_optimal
```

### Method 3: Local Development Setup

For local development without Docker:

```bash
# Setup Poetry environment
poetry install
poetry shell

# Start local PostgreSQL (ensure it's running)
# Update co_optimal/.env with local database settings:
# POSTGRES_HOST=localhost

# Run application locally
poetry run python -m co_optimal.fastapi_application
```

## 🐳 Docker Setup

### Quick Start Commands
```bash
# Start the application
make start-co_optimal

# Build and start (if changes made)
make build-co_optimal

# Stop services
make stop-co_optimal

# View logs
make logs-co_optimal

# Restart application
make restart-co_optimal
```

### Manual Docker Commands
```bash
# Start API
docker-compose -f dockerfiles/docker-compose.co_optimal.yml --env-file ./co_optimal/.env up -d

# Build and start
docker-compose -f dockerfiles/docker-compose.co_optimal.yml --env-file ./co_optimal/.env up --build -d

# View logs
docker-compose -f dockerfiles/docker-compose.co_optimal.yml logs -f
```

For detailed Docker documentation, see [DOCKERFILE.md](DOCKERFILE.md).

## 🏃‍♂️ Running the Application

### Docker Deployment (Production-Ready)
```bash
# Start the application
make start-co_optimal

# Access the application
curl http://localhost:8000/health-check
```

### Local Development
```bash
# Activate Poetry environment
poetry shell

# Run with auto-reload
poetry run uvicorn co_optimal.fastapi_application:application --reload --host 0.0.0.0 --port 8000

# Or run with Gunicorn (production-like)
poetry run gunicorn -k uvicorn.workers.UvicornWorker co_optimal.fastapi_application:application --bind 0.0.0.0:8000
```

### Development with Hot Reload
```bash
# Poetry environment with file watching
poetry run uvicorn co_optimal.fastapi_application:application --reload

# Access at http://localhost:8000
```

## 🗃️ Database Migrations

The project uses Alembic for database schema management and migrations. All database changes are version-controlled and can be applied/rolled back safely.

### Quick Migration Commands

```bash
# Initialize database (first time setup)
make migrate-init

# Generate migration after model changes
make migrate-generate

# Apply all pending migrations
make migrate-up

# Rollback last migration
make migrate-down

# Check current migration status
make migrate-current

# View migration history
make migrate-history
```

### Database Models

The project includes SQLAlchemy models for structured data management:

```python
# Example: User model
from co_optimal.models import User

# Models are defined in co_optimal/models/
# - user.py: User authentication and profile data
# - base.py: Base model class with common functionality
```

### Migration Workflow

1. **Modify Models**: Update SQLAlchemy models in `co_optimal/models/`
2. **Generate Migration**: `make migrate-generate`
3. **Review Migration**: Check the generated file in `alembic/versions/`
4. **Apply Migration**: `make migrate-up`
5. **Verify**: `make migrate-current`

### Production Migrations

```bash
# Test migrations first
poetry run alembic upgrade head --sql  # Show SQL without executing

# Apply in production
make migrate-up

# Rollback if needed
make migrate-down
```

For detailed migration documentation, see [ALEMBIC_MIGRATIONS.md](ALEMBIC_MIGRATIONS.md).

## 📚 API Documentation

Once the application is running:

- **Swagger UI**: http://localhost:8000/docs
- **ReDoc**: http://localhost:8000/redoc
- **Health Check**: http://localhost:8000/health-check
- **OpenAPI JSON**: http://localhost:8000/openapi.json

### API Endpoints Structure
```
/api/v1/
├── /auth/          # Authentication endpoints
├── /users/         # User management
├── /data/          # Data processing
└── /health-check   # Health monitoring
```

## 🛠️ Development Workflow

### Adding Dependencies
```bash
# Production dependency
poetry add package-name

# Development dependency
poetry add --group dev package-name

# Update all dependencies
poetry update

# Export requirements (if needed)
poetry export -f requirements.txt --output requirements.txt
```

### Database Operations
```bash
# Connect to database (Docker)
docker exec -it co-optimal-postgres psql -U postgres -d co_optimal

# Backup database
docker exec co-optimal-postgres pg_dump -U postgres co_optimal > backup.sql

# Restore database
docker exec -i co-optimal-postgres psql -U postgres -d co_optimal < backup.sql
```

### Code Quality
```bash
# Format code
poetry run black co_optimal/

# Lint code
poetry run flake8 co_optimal/

# Type checking
poetry run mypy co_optimal/

# Run tests
poetry run pytest
```

### Testing Commands
```bash
# Build test image
make test-build

# Run test container
make test-run

# Clean up resources
make clean
```

## 🔧 Configuration

### Environment Variables
Copy `co_optimal/.env.sample` to `co_optimal/.env` and configure:

```env
# PostgreSQL Configuration
POSTGRES_DB_NAME=co_optimal
POSTGRES_HOST=postgres          # 'localhost' for local dev
POSTGRES_USERNAME=postgres
POSTGRES_PASSWORD=postgres
POSTGRES_PORT=5432
POSTGRES_EXTERNAL_PORT=5432

# Application Configuration
LOG_LEVEL=info
ENVIRONMENT=server

# FastAPI Configuration
FASTAPI_APPLICATION_PORT=8000
APPLICATION_WORKERS=1
APPLICATION_THREADS=4
```

### Database Connection Pool
The application uses a thread-safe connection pool:

```python
from co_optimal.utils.v1.connections import db_connection_context

# Safe database operations
with db_connection_context() as conn:
    with conn.cursor() as cursor:
        cursor.execute("SELECT * FROM your_table")
        results = cursor.fetchall()
```

## 🐛 Troubleshooting

### Common Issues

#### Poetry Environment Issues
```bash
# Check environment
poetry env info

# Recreate environment
poetry env remove python
poetry env use 3.13.2
poetry install
```

#### Docker Network Issues
```bash
# Check networks
docker network ls

# Recreate network
docker network rm co_optimal
make start-co_optimal
```

#### Database Connection Issues
```bash
# Check PostgreSQL logs
docker logs co-optimal-postgres

# Test connection
docker exec -it co-optimal-postgres pg_isready -U postgres
```

#### Build Issues
```bash
# Clean Docker cache
docker system prune -a

# Rebuild from scratch
docker-compose -f dockerfiles/docker-compose.co_optimal.yml build --no-cache
```

For detailed troubleshooting, see:
- [DOCKERFILE.md](DOCKERFILE.md) - Docker-specific issues
- [POETRY_SETUP.md](POETRY_SETUP.md) - Poetry-specific issues

## 🤝 Contributing

1. **Fork the repository**
2. **Create a feature branch**
   ```bash
   git checkout -b feature/amazing-feature
   ```
3. **Make your changes**
   - Follow existing code style
   - Add tests for new functionality
   - Update documentation as needed
4. **Run quality checks**
   ```bash
   poetry run black co_optimal/
   poetry run flake8 co_optimal/
   poetry run pytest
   ```
5. **Commit your changes**
   ```bash
   git commit -m "feat: add amazing feature"
   ```
6. **Push to your branch**
   ```bash
   git push origin feature/amazing-feature
   ```
7. **Submit a pull request**

### Development Standards
- **Code Style**: Black formatting, flake8 linting
- **Type Hints**: Use type annotations
- **Documentation**: Update docstrings and README
- **Testing**: Add tests for new features
- **Git**: Use conventional commit messages

## 📄 License

[Add your license information here]

---

## 📞 Support

For questions and support:
- Create an issue in the repository
- Check the troubleshooting guides
- Review the documentation files

**Happy coding! 🚀**
