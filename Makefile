# Default target
target: | start-co_optimal

# Build and start the FastAPI application
build-co_optimal:
	docker compose -f ./dockerfiles/docker-compose.co_optimal.yml --env-file ./co_optimal/.env up --build -d

# Start the FastAPI application (without building)
start-co_optimal:
	docker compose -f ./dockerfiles/docker-compose.co_optimal.yml --env-file ./co_optimal/.env up -d

# Start all services (currently just the FastAPI app)
start-all: start-co_optimal

# Stop the FastAPI application
stop-co_optimal:
	docker compose -f ./dockerfiles/docker-compose.co_optimal.yml --env-file ./co_optimal/.env down

# Stop all services
stop-all: stop-co_optimal

# View logs
logs-co_optimal:
	docker compose -f ./dockerfiles/docker-compose.co_optimal.yml logs -f

# Restart the application
restart-co_optimal: stop-co_optimal start-co_optimal

# Clean up Docker resources
clean:
	docker system prune -f
	docker volume prune -f

# Database migration targets
migrate-generate:
	poetry run alembic revision --autogenerate -m "Auto migration"

migrate-up:
	poetry run alembic upgrade head

migrate-down:
	poetry run alembic downgrade -1

migrate-history:
	poetry run alembic history

migrate-current:
	poetry run alembic current

migrate-init:
	poetry run alembic upgrade head

# Development helpers
dev-setup:
	poetry install
	poetry run alembic upgrade head

# Quick test commands
test-build:
	docker build -f ./dockerfiles/Dockerfile.co_optimal -t co_optimal_api:test .

test-run:
	docker run --rm -p 8000:8000 --env-file ./co_optimal/.env co_optimal_api:test

# Help target
help:
	@echo "Available targets:"
	@echo "  build-co_optimal  - Build and start the FastAPI application"
	@echo "  start-co_optimal  - Start the FastAPI application"
	@echo "  stop-co_optimal   - Stop the FastAPI application"
	@echo "  restart-co_optimal - Restart the FastAPI application"
	@echo "  logs-co_optimal   - View application logs"
	@echo "  clean            - Clean up Docker resources"
	@echo "  migrate-*        - Database migration commands"
	@echo "  dev-setup        - Setup development environment"
	@echo "  test-build       - Build test image"
	@echo "  test-run         - Run test container"
	@echo "  help             - Show this help message"
