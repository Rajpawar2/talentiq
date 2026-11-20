.PHONY: dev start run test docker clean help

help:
	@echo "TalentIQ - Available Commands:"
	@echo "  make dev      Start both Backend and Frontend concurrently (Single Command)"
	@echo "  make test     Run full automated test suite"
	@echo "  make docker   Start entire stack using Docker Compose"
	@echo "  make clean    Clean cache and build artifacts"

dev start run:
	@./start.sh

test:
	@echo "Running backend test suite..."
	cd backend && .venv/bin/pytest
	@echo "Running frontend typecheck & build..."
	cd frontend && npm run build

docker:
	docker compose up --build

clean:
	find . -type d -name "__pycache__" -exec rm -rf {} +
	find . -type d -name ".pytest_cache" -exec rm -rf {} +
	rm -rf frontend/dist
