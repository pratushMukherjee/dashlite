.PHONY: dev backend frontend install seed test clean

# Run both backend and frontend
dev:
	@echo "Starting backend and frontend..."
	$(MAKE) -j2 backend frontend

backend:
	cd backend && uvicorn app.main:app --reload --host 0.0.0.0 --port 8000

frontend:
	cd frontend && npm run dev

install:
	cd backend && pip install -r requirements.txt
	cd frontend && npm install

seed:
	cd backend && python -m demo.seed_data

test:
	cd backend && pytest tests/ -v

migrate:
	cd backend && alembic upgrade head

clean:
	rm -rf data/
	rm -rf backend/__pycache__
	rm -rf frontend/dist
	rm -rf frontend/node_modules
