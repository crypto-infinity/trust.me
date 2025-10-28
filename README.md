# Trust.me

People and organizations spend a significant amount of time and energy determining the trustworthiness of their relationships (personal and professional), sometimes without full visibility or understanding of the dynamics at play to properly manage this process: this leads to suboptimal decisions, failed partnerships, and important emotional and economic costs, resulting in quantifiable negative outcomes (for example, a company with low trust may underperform compared to others).

For more information, see https://github.com/crypto-infinity/trust.me/tree/main/docs.

Trust.me is a platform designed to evaluate, verify, and present reliable information through an automated scoring system and intelligent agents, supporting humans in the validation process while leaving them with full governance. The project consists of a Python backend (FastAPI) and a React frontend.

## Architecture

- **Backend**: Python, FastAPI, LangChain, modular agents for scraping, verification, scoring, and search.
- **Frontend**: React, Vite, modern interface for presenting results and authentication - *currently under development*.

## Main Features

- **Scraping and data collection**: Automatic extraction of information from web sources.
- **Verification and scoring**: Reliability assessment through agents and custom algorithms.
- **User interface**: Results visualization, login, and user management.

## Quick Start

### Backend

1. Go to the `backend` folder:
	```powershell
	cd backend
	```
2. Install dependencies:
	```powershell
	pip install -r requirements.txt
	```
3. Start the server:
	```powershell
	uvicorn main:app --reload
	```

### Frontend

1. Go to the `frontend` folder:
	```powershell
	cd frontend
	```
2. Install dependencies:
	```powershell
	npm install
	```
3. Start the application:
	```powershell
	npm run dev
	```

## Project Structure

- `backend/` — API, business logic, agents
- `frontend/` — React user interface
- `service/` — Dockerfile and auxiliary services
- `tests/` — Automated tests (unit, integration, e2e)
- `docs/` — Documentation, studies, and project materials

## Contributing - if you wish!

1. Fork the repository
2. Create a feature branch (`git checkout -b feature/FeatureName`)
3. Commit and push your changes
4. Open a Pull Request

## License

This project is distributed under the MIT license. See the LICENSE file for details.
