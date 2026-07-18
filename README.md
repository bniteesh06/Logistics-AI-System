# CognixOps

An AI-assisted logistics and supply chain optimization tool. It forecasts demand, picks routes around disruptions, and simulates "what if" scenarios (port closures, supplier delays, bad weather, demand spikes) across a small European network — 2 warehouses, 2 plants, and a customer hub in Munich.

Backend is FastAPI, frontend is Streamlit. Built as a portfolio project to show off a properly layered backend, not just a script that returns JSON.

## Why it's structured this way

Most small FastAPI projects I've seen dump everything into `main.py`. This one splits things into layers on purpose:

```
backend/app/
  core/       config, logging, exception handlers, middleware
  routes/     just HTTP in/out, no business logic
  services/   the actual logic — forecasting, optimization, simulation, anomalies
  models/     Pydantic schemas + enums
  utils/      data generation and caching
```

A few things worth pointing out if you're reading the code:

- Every route returns the same response shape: `{"status": "success", ...}` on the happy path, `{"status": "error", "code": ..., "message": ..., "details": {...}}` when something goes wrong. No guessing which endpoints return what on failure.
- Config is entirely env-var driven — see `backend/.env.example`. Nothing is hardcoded, and there's nothing sensitive in there since this is demo data.
- Data is generated once at startup and cached in memory instead of being re-read on every request.
- Requests get an `X-Request-ID` and `X-Response-Time-Ms` header for basic traceability.

On the frontend side, `Frontend/theme.py` is a small shared design system so the KPI cards, charts, and map all look consistent instead of each component styling itself. Streamlit ships with a dark theme by default, which is why `.streamlit/config.toml` pins it to light — otherwise half the custom colors become unreadable.

**Being upfront about a limitation:** Streamlit is server-rendered and reruns the whole script on every interaction. It doesn't do real client-side routing or modals the way React does. I pushed it about as far as it goes (toasts, skeleton loaders, a proper error state when the backend's down), but if this needed a pixel-perfect production UI, I'd rebuild the frontend in React and keep this same FastAPI backend underneath.

## Running it locally

You need two terminals — one for the API, one for the dashboard.

**Backend**
```bash
cd backend
python -m venv venv && source venv/bin/activate   # Windows: venv\Scripts\activate
pip install -r requirements.txt
uvicorn app.main:app --reload --port 8000
```
There's a `.env.example` in `backend/` if you want to override anything (CORS origins, log level, etc.) — copy it to `.env`, then run with `uvicorn --env-file .env` (or export the vars yourself; uvicorn doesn't load `.env` automatically).

**Frontend**
```bash
cd Frontend
python -m venv venv && source venv/bin/activate
pip install -r requirements.txt
export API_URL=http://127.0.0.1:8000   # PowerShell: $env:API_URL = "http://127.0.0.1:8000"
streamlit run app.py
```

Open the URL Streamlit prints, pick a SKU / disruption / forecast horizon in the sidebar, and hit **Run Analysis**.

## API reference

| Method | Path | What it does |
|---|---|---|
| GET | `/health` | Liveness check |
| GET | `/forecast?sku=&horizon=` | Demand forecast with confidence band and history |
| GET | `/kpi` | Service level, cost, CO₂, on-time %, inventory turnover |
| POST | `/optimize` | Takes `{disruption_type}`, returns the chosen route + cost/CO₂ |
| POST | `/simulate` | Takes `{disruption_type}`, returns before/after KPIs and a response playbook |
| POST | `/anomaly` | Takes `{product_id, sensitivity}`, returns flagged demand points |
| GET | `/coordination/network` | Supplier → factory → customer network graph |
| GET | `/coordination/feed` | Live-ish coordination event feed |

Full interactive docs live at `http://127.0.0.1:8000/docs` while the backend is running (turned off automatically when `ENVIRONMENT=production`).

## Stack

FastAPI, Pydantic, pandas/numpy on the backend. Streamlit, Plotly, and Folium on the frontend. No database — everything runs off generated CSVs (`backend/app/data/`) since the point here is the architecture and the optimization logic, not persistence.
