# UK Wind Forecast Analytics

Full-stack starter project for the Full Stack SWE challenge.

- Frontend: React + TypeScript + Vite + Recharts
- Backend: Python + FastAPI + pandas + httpx
- Data: Elexon BMRS FUELHH (actual wind) and WINDFOR (wind forecasts)
- Containerization: Docker Compose

## What it does

- Provides an analytics dashboard for January 2026 delivery intervals.
- Retrieves actual wind generation and wind forecast records from Elexon.
- Selects the latest forecast published on or before a configurable decision cutoff.
- Matches forecasts and actuals by delivery `startTime`.
- Calculates MAE, RMSE, and bias.
- Includes graceful API errors and synthetic sample data fallback for local UI development.

**Important:** The Elexon dataset stream endpoints and query parameters may evolve. Verify the live response schema and filtering/query options against the official docs before relying on the results. This project deliberately reports the source mode and errors rather than claiming sample data is live data. It does not invent missing actuals.

## Run locally with Docker

```bash
docker compose up --build
```

Then open:
- Frontend: http://localhost:5173
- Backend health: http://localhost:8000/api/health
- API docs: http://localhost:8000/docs

## Run without Docker

Backend:

```bash
cd backend
python -m venv .venv
# Windows: .venv\Scripts\activate
# macOS/Linux: source .venv/bin/activate
pip install -r requirements.txt
uvicorn app.main:app --reload --port 8000
```

Frontend in another terminal:

```bash
cd frontend
npm install
npm run dev
```

The Vite dev server proxies `/api` to `http://localhost:8000`.

## Configuration

Copy `.env.example` to `.env` if you want to configure the service. Environment variables:

- `ELEXON_BASE_URL` default `https://data.elexon.co.uk/bmrs/api/v1`
- `ELEXON_TIMEOUT_SECONDS` default `20`
- `DECISION_CUTOFF_HOUR_UTC` default `10` (illustrative assumption; confirm the business cutoff with the client)
- `USE_SAMPLE_DATA` default `true` for a demo-friendly local start. Set `false` to require live Elexon data.
- `FRONTEND_ORIGIN` default `http://localhost:5173`

The exact Elexon parameters can vary by endpoint/version. The client sends `from` and `to` date parameters and handles common response shapes; adjust `backend/app/services/elexon.py` after checking the current endpoint documentation. For January 2026 delivery intervals, forecast retrieval starts in late December 2025 so forecasts published before delivery are not missed.

## API endpoints

- `GET /api/health`
- `GET /api/forecast/summary?start=2026-01-01&end=2026-01-31`
- `GET /api/forecast/series?start=2026-01-01&end=2026-01-31`
- `GET /api/forecast/history?start=2026-01-01&end=2026-01-31`
- `GET /api/forecast/accuracy?start=2026-01-01&end=2026-01-31`

Optional query parameters:
- `cutoff_hour_utc`: decision cutoff hour in UTC (0–23)
- `live`: request live data even when sample data is enabled (`true`/`false`)

## Metrics

For error `forecast - actual`:
- MAE = mean absolute error
- RMSE = square root of mean squared error
- Bias = mean signed error; positive means over-forecasting

MAPE is omitted because it is unstable when actual generation is zero or near zero.

## Testing

```bash
cd backend
pytest
```

## Deployment notes

Deploy the frontend and backend separately if needed:
1. Deploy backend to a Python-capable host and set `FRONTEND_ORIGIN` to the deployed frontend origin.
2. Deploy frontend to Vercel and set `VITE_API_BASE_URL` to the backend base URL, ending without a trailing slash.
3. Verify `/api/health`, `/docs`, charts, and browser network requests in an incognito window.

This repository is a starter implementation, not a claim that it has already been deployed. The challenge requires a public repository, deployed app, and unlisted YouTube demo; those steps still need to be completed by the owner.

## AI disclosure

AI assistance (ChatGPT) was used to scaffold and draft parts of this project. Review, test, and validate the code and live Elexon API behavior before submission.
