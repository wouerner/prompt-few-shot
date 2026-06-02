# Agent Instructions

This document provides essential, high-signal information for an AI agent working in this repository.

## Core Principles

- **Docker is mandatory:** This project is designed to run exclusively in a Dockerized environment. Do not attempt to run services or tests on the host machine.
- **Single source of truth:** The `README.md` and `docker-compose.yml` are the primary sources of truth for commands and environment setup.

## Development Workflow

### Setup and Teardown

- **Start all services:** `docker compose up --build`
  - This launches the FastAPI backend, the frontend, and the Allure dashboard.
  - The application will be available at `http://localhost:8080`.
  - The backend runs with hot-reloading enabled (`--reload`).
- **Stop all services:** `docker compose down`

### Testing

All tests must be run inside the `app` container. The app container already has all test dependencies installed (pytest, behave, allure adapters).

- **Run all pytest tests:**
  ```bash
  docker compose exec app pytest --alluredir=allure-results
  ```
- **Run a single pytest file:**
  ```bash
  docker compose exec app pytest tests/unit/test_main.py --alluredir=allure-results
  ```
- **Run a single pytest test:**
  ```bash
  docker compose exec app pytest tests/unit/test_main.py::test_function_name --alluredir=allure-results
  ```
- **Run BDD tests (behave):**
  ```bash
  docker compose exec app behave -f allure_behave.formatter:AllureFormatter -o allure-results tests/bdd
  ```
- **Run a single Behave feature:**
  ```bash
  docker compose exec app behave -f allure_behave.formatter:AllureFormatter -o allure-results tests/bdd/vacation_approval.feature
  ```

### Test Reports

- **View Allure reports:** After running tests, view the interactive reports in your browser:
  - **Dashboard UI:** `http://localhost:5252/allure-docker-service-ui/`
  - The Allure service polls `allure-results/` every 3 seconds and rebuilds automatically.

## Project Structure

- `app/main.py`: The main FastAPI application file. Single-file backend (no module splitting).
- `app/static/`: Contains the vanilla JavaScript frontend (SPA: `index.html`, `app.js`, `styles.css`).
- `tests/unit/`: Pytest unit and integration tests (`test_main.py`).
- `tests/bdd/`: Behave BDD tests (feature files in Portuguese, step definitions in `steps/`).
- `requirements.txt`: Python dependencies for the application and tests.

## Architecture Notes

### In-Memory Database

The application uses Python dicts as an in-memory database (`employees_db`, `vacation_requests_db`) with global integer counters (`employee_id_counter`, `vacation_id_counter`). Every test fixture must reset **both the dicts and the counters** to the original seed state, otherwise tests will leak IDs across runs.

### Volume Mount

The `app` container mounts the project root as a volume (`.:/app`). Code changes made locally are reflected immediately inside the container without a rebuild. The `Dockerfile` COPY step is only used for the initial image build; the volume mount overrides it at runtime.
