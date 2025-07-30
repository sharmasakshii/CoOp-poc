# Docker Setup Documentation

This document provides a comprehensive explanation of the Docker configuration for the Co-Optimal project, including Dockerfiles, Docker Compose files, and networking setup.

## 📁 Docker File Structure

```
co-optimal/
├── dockerfiles/
│   ├── Dockerfile.co_optimal          # Main application Dockerfile
│   └── docker-compose.co_optimal.yml  # FastAPI application service
├── co_optimal/
│   └── .env                           # Environment variables
└── Makefile                           # Build automation
```

## 🐳 Dockerfile.co_optimal

This is the main Dockerfile that builds the FastAPI application container.

### Base Image Selection
```dockerfile
FROM python:3.13.2-slim
```
**Why this choice:**
- **`python:3.13.2`**: Matches the project's Python requirement (`^3.13.2`)
- **`-slim`**: Smaller image size (~40MB vs ~300MB for full image)
- **Official image**: Maintained by Docker, includes security updates
- **Debian-based**: Good package availability and stability

### Working Directory
```dockerfile
WORKDIR /co_optimal
```
**Purpose:**
- Sets the default directory for all subsequent commands
- Organizes application files in a predictable location
- Matches the project structure

### System Dependencies Installation
```dockerfile
RUN apt-get update -y && \
    apt-get install -y --no-install-recommends \
        curl \
        build-essential \
        libpq-dev \
        postgresql-client && \
    rm -rf /var/lib/apt/lists/* && \
    apt-get clean
```

**Package breakdown:**
- **`curl`**: For downloading Poetry installer and making HTTP requests
- **`build-essential`**: GCC compiler and build tools for Python packages with C extensions
- **`libpq-dev`**: PostgreSQL development headers (required for psycopg2)
- **`postgresql-client`**: PostgreSQL client tools (psql, pg_dump, etc.)

**Optimization techniques:**
- **Single RUN command**: Reduces Docker layers
- **`--no-install-recommends`**: Installs only essential packages
- **Cache cleanup**: `rm -rf /var/lib/apt/lists/*` removes package cache
- **`apt-get clean`**: Additional cleanup for smaller image

### Poetry Installation
```dockerfile
RUN curl -sSL https://install.python-poetry.org | python3 - && \
    ln -s /root/.local/bin/poetry /usr/local/bin/poetry
```

**Why Poetry:**
- **Dependency management**: Handles package versions and conflicts
- **Lock files**: Ensures reproducible builds
- **Virtual environments**: Isolates project dependencies

**Installation method:**
- **Official installer**: More reliable than pip install
- **System-wide symlink**: Makes `poetry` command available globally
- **Version pinning**: Uses the latest stable version

### Dependency Installation (Layer Caching Strategy)
```dockerfile
COPY pyproject.toml poetry.lock ./
ENV POETRY_NO_INTERACTION=1
ENV POETRY_VENV_IN_PROJECT=1
RUN poetry config virtualenvs.create false && \
    poetry install --no-root --no-ansi
```

**Layer caching optimization:**
- **Copy dependencies first**: Changes to application code don't invalidate this layer
- **Separate from code**: Only rebuilds when dependencies change
- **Significant build time savings**: Dependencies are cached between builds

**Poetry configuration:**
- **`POETRY_NO_INTERACTION=1`**: Prevents interactive prompts
- **`POETRY_VENV_IN_PROJECT=1`**: Creates virtual environment in project directory
- **`virtualenvs.create false`**: Installs globally (no virtual env in container)
- **`--no-root`**: Doesn't install the project itself as a package
- **`--no-ansi`**: Cleaner build logs without color codes

### Application Code Copy
```dockerfile
COPY . .
```
**Strategy:**
- **Last step**: Maximizes cache utilization
- **Complete copy**: Includes all application files
- **Invalidates on any code change**: But dependencies remain cached

### Security Configuration
```dockerfile
RUN useradd -m -u 1000 appuser && chown -R appuser:appuser /co_optimal
USER appuser
```

**Security benefits:**
- **Non-root execution**: Reduces attack surface
- **Specific UID**: Consistent user ID across environments
- **Home directory**: `-m` flag creates /home/appuser
- **File ownership**: Ensures application can read/write its files

**Why UID 1000:**
- Common default user ID on Linux systems
- Avoids permission issues in development environments
- Consistent across container and host systems

### Environment Variables
```dockerfile
ENV PYTHONPATH=/co_optimal
ENV PYTHONUNBUFFERED=1
```

**Environment configuration:**
- **`PYTHONPATH=/co_optimal`**: Ensures Python can find the application modules
- **`PYTHONUNBUFFERED=1`**: Prevents Python from buffering output, ensuring logs appear immediately

### Port Exposure
```dockerfile
EXPOSE 8000
```
**Purpose:**
- **Documentation**: Indicates which port the application uses
- **Network configuration**: Helps with port mapping
- **Container networking**: Other containers can connect to this port

### Health Check
```dockerfile
HEALTHCHECK --interval=30s --timeout=10s --start-period=40s --retries=3 \
    CMD curl -f http://localhost:8000/health-check || exit 1
```

**Health monitoring:**
- **`curl -f`**: Fails silently on HTTP errors
- **`/health-check`**: Uses the application's health endpoint
- **Timing**: 30s intervals, 10s timeout, 40s startup grace period
- **Retries**: 3 attempts before marking unhealthy

## 🚀 docker-compose.co_optimal.yml

This file defines the FastAPI application service with Azure PostgreSQL integration.

### Build Configuration
```yaml
co_optimal_api:
  image: co_optimal_api:latest
  build:
    context: ../
    dockerfile: ./dockerfiles/Dockerfile.co_optimal
```

**Build strategy:**
- **Context**: Parent directory (where pyproject.toml lives)
- **Dockerfile location**: Specific path to Dockerfile
- **Image tagging**: Creates reusable image

**Context explanation:**
- **`../`**: Includes entire project in build context
- **File access**: Dockerfile can access all project files
- **Poetry files**: pyproject.toml and poetry.lock are accessible

### Application Command
```yaml
command: gunicorn -k uvicorn.workers.UvicornWorker --bind 0.0.0.0:8000 --workers ${APPLICATION_WORKERS:-1} --threads ${APPLICATION_THREADS:-4} co_optimal.fastapi_application:application --timeout 400 --log-level=${LOG_LEVEL:-info}
```

**Gunicorn configuration:**
- **`-k uvicorn.workers.UvicornWorker`**: ASGI worker for FastAPI
- **`--bind 0.0.0.0:8000`**: Listen on all interfaces, port 8000
- **Production ready**: Gunicorn is a production WSGI server

**Scaling configuration:**
- **Workers**: Process-level parallelism (default: 1)
- **Threads**: Thread-level parallelism per worker (default: 4)
- **Total capacity**: Workers × Threads concurrent requests

**Operational settings:**
- **Timeout**: 400 seconds for long-running requests
- **Log level**: Configurable logging verbosity
- **Module path**: Points to FastAPI application instance

### Environment Variables
```yaml
environment:
  - POSTGRES_DB_NAME=${POSTGRES_DB_NAME}
  - POSTGRES_HOST=${POSTGRES_HOST}
  - POSTGRES_USERNAME=${POSTGRES_USERNAME}
  - POSTGRES_PASSWORD=${POSTGRES_PASSWORD}
  - POSTGRES_PORT=${POSTGRES_PORT}
  - POSTGRES_EXTERNAL_PORT=${POSTGRES_EXTERNAL_PORT}
  - POSTGRES_SSLMODE=${POSTGRES_SSLMODE}
```

**Azure PostgreSQL configuration:**
- **Database connection**: Points to Azure PostgreSQL instance
- **SSL requirement**: `POSTGRES_SSLMODE=require` for Azure
- **External connection**: Uses Azure's managed PostgreSQL service
- **Security**: Credentials managed through environment variables

**Environment file integration:**
```yaml
env_file:
  - ../co_optimal/.env
```

**Benefits:**
- **Centralized configuration**: All environment variables in one file
- **Security**: Sensitive data not hardcoded in compose file
- **Flexibility**: Easy to switch between environments

### Health Check Configuration
```yaml
healthcheck:
  test: ["CMD", "curl", "-f", "http://localhost:8000/health-check"]
  interval: 30s
  timeout: 10s
  retries: 3
  start_period: 40s
```

**Health monitoring:**
- **Application endpoint**: Uses FastAPI's `/health-check` endpoint
- **Docker health**: Container marked as healthy/unhealthy
- **Orchestration**: Other services can depend on health status
- **Monitoring**: Easy to track application availability

### Network Configuration
```yaml
networks:
  - co_optimal

networks:
  co_optimal:
    name: co_optimal
    external: true
```

**External network:**
- **`external: true`**: Expects network to already exist
- **Shared communication**: Multiple services can use same network
- **Isolation**: Separate from default Docker networks

## 🔗 Azure PostgreSQL Integration

### Connection Configuration
The application connects to Azure PostgreSQL using the following configuration:

```env
# PostgreSQL Configuration - Azure Database
POSTGRES_DB_NAME=postgres
POSTGRES_HOST=co-pgs-postgres-dev-eastus-001.postgres.database.azure.com
POSTGRES_USERNAME=coop_psql_dbuser_dev_co_dev_appuser
POSTGRES_PASSWORD=2uEBXOg0yXWS16yD
POSTGRES_PORT=5432
POSTGRES_EXTERNAL_PORT=5432
POSTGRES_SSLMODE=require
```

**Azure-specific considerations:**
- **SSL requirement**: Azure PostgreSQL requires SSL connections
- **Hostname**: Uses Azure's managed PostgreSQL endpoint
- **Authentication**: Uses Azure AD or database user authentication
- **Network security**: Configured through Azure firewall rules

### Application Settings
```env
# Application settings
APPLICATION_WORKERS=1
APPLICATION_THREADS=4
LOG_LEVEL=info
FASTAPI_APPLICATION_PORT=8000
```

**Performance tuning:**
- **Workers**: Adjust based on CPU cores and memory
- **Threads**: Per-worker thread count for I/O bound operations
- **Logging**: Configurable verbosity for different environments

## 🛠️ Build and Deployment Process

### Local Development
```bash
# Build and start the application
docker-compose -f dockerfiles/docker-compose.co_optimal.yml up --build -d

# View logs
docker logs co_optimal_api

# Stop the application
docker-compose -f dockerfiles/docker-compose.co_optimal.yml down
```

### Production Deployment
```bash
# Build production image
docker build -f dockerfiles/Dockerfile.co_optimal -t co_optimal_api:latest .

# Run with production environment
docker run -d \
  --name co_optimal_api \
  --network co_optimal \
  -p 8000:8000 \
  --env-file co_optimal/.env \
  co_optimal_api:latest
```

## 🐛 Troubleshooting

### Common Issues

#### 1. Azure PostgreSQL Connection Failed
**Error**: `could not connect to server: Connection refused`

**Solutions:**
- Verify Azure PostgreSQL firewall rules allow your IP
- Check SSL mode is set to `require`
- Ensure credentials are correct
- Test connection with `psql` client

#### 2. Health Check Failing
**Error**: Container marked as unhealthy

**Solutions:**
- Check application logs: `docker logs co_optimal_api`
- Verify health endpoint is accessible
- Increase `start_period` if application needs more startup time
- Check if curl is available in container

#### 3. Environment Variables Not Loading
**Error**: Application can't find database credentials

**Solutions:**
- Verify `.env` file exists and has correct format
- Check environment variable names match application expectations
- Use `docker exec` to inspect container environment
- Ensure `env_file` path is correct in docker-compose

#### 4. Build Failures
**Error**: Poetry installation or dependency issues

**Solutions:**
- Clear Docker cache: `docker system prune`
- Update poetry.lock: `poetry lock`
- Check internet connection for package downloads
- Verify Python version compatibility

### Verification Commands

#### Check Running Containers
```bash
docker ps
```

#### Check Container Health
```bash
docker inspect co_optimal_api | grep -A 10 Health
```

#### Check Logs
```bash
docker logs co_optimal_api
```

#### Test Database Connection
```bash
docker exec -it co_optimal_api psql -h $POSTGRES_HOST -U $POSTGRES_USERNAME -d $POSTGRES_DB_NAME
```

#### Test API Health
```bash
curl http://localhost:8000/health-check
```

#### Inspect Environment Variables
```bash
docker exec -it co_optimal_api env | grep POSTGRES
```

## 🚀 Production Considerations

### Security Enhancements
- **Secrets management**: Use Docker secrets or external secret managers
- **Network security**: Implement proper firewall rules
- **SSL/TLS**: Ensure all connections use encryption
- **Regular updates**: Keep base images and dependencies updated

### Performance Optimization
- **Worker tuning**: Adjust based on server CPU cores and memory
- **Database connection pooling**: Configure appropriate pool sizes
- **Caching**: Implement Redis or similar for session/data caching
- **Load balancing**: Use multiple API instances behind a load balancer

### Monitoring and Logging
- **Structured logging**: Implement JSON logging for better parsing
- **Metrics collection**: Add Prometheus metrics endpoints
- **Health monitoring**: Set up external health checks
- **Alerting**: Configure alerts for critical failures

### Scalability
- **Horizontal scaling**: Run multiple API containers
- **Database scaling**: Consider read replicas for Azure PostgreSQL
- **Container orchestration**: Use Kubernetes or Docker Swarm
- **Auto-scaling**: Implement based on CPU/memory usage

## 📚 Additional Resources

- [Docker Compose Documentation](https://docs.docker.com/compose/)
- [Azure Database for PostgreSQL](https://docs.microsoft.com/en-us/azure/postgresql/)
- [Python Docker Hub](https://hub.docker.com/_/python)
- [FastAPI Deployment Guide](https://fastapi.tiangolo.com/deployment/)
- [Gunicorn Configuration](https://docs.gunicorn.org/en/stable/configure.html)
- [Poetry Documentation](https://python-poetry.org/docs/) 