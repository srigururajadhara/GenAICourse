.PHONY: api ui test compile docker-up docker-down

api:
	uvicorn app.api.main:app --reload --host 0.0.0.0 --port 8001

ui:
	streamlit run app/ui/streamlit_app.py --server.port 8502

test:
	pytest

compile:
	python -m compileall -q app tests

docker-up:
	docker compose up --build -d

docker-down:
	docker compose down
