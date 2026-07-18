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


**How to deploy it **

step 1 — backend on render

go to render.com and sign in with github
click the New button top right, then pick Web Service
it shows your repos, click on Logistics-AI-System
now it asks for a bunch of fields, fill them like this:

Root Directory → type backend
Build Command → type pip install -r requirements.txt
Start Command → type uvicorn app.main:app --host 0.0.0.0 --port $PORT
Instance Type → pick Free


scroll down, there's a section to add environment variables, add these three, one at a time:

key: ENVIRONMENT value: production
key: ALLOWED_ORIGINS value: *
key: LOG_LEVEL value: INFO


click Create Web Service at the bottom
it'll take a min or two to build, you'll see logs scrolling, just wait till it says "Live" at the top
once live, there's a url right under your service name, something like https://logistics-ai-backend-xxxx.onrender.com — copy that somewhere, you need it later
open that url in a browser but add /health at the end, so like https://logistics-ai-backend-xxxx.onrender.com/health — if it shows {"status":"ok"} that means backend's working. if it shows an error, go back to render, click on your service, click Logs, and see what it's complaining about

step 2 — frontend on streamlit

go to share.streamlit.io and sign in with github again
click New app
pick your repo Logistics-AI-System, branch main
there's a field for main file path, type Frontend/app.py
before clicking deploy, click Advanced settings
inside advanced settings there's a Secrets box, paste this in (swap in your real render url from step 1):

  API_URL = "https://logistics-ai-backend-xxxx.onrender.com"

now click Deploy
wait a few minutes, it's installing stuff in the background
once it's done you get a link like https://your-app-name.streamlit.app — that's your live dashboard, open it and check it actually loads and shows data

step 3 — lock the backend so only your frontend can call it

this one's optional but takes 30 seconds so just do it
go back to render, click your backend service, click Environment on the left
find ALLOWED_ORIGINS, click edit, change the value from * to your streamlit link, like https://your-app-name.streamlit.app
save it, render will restart the service on its own

step 4 — fix the fallback url in your code

on your computer, open Frontend/config.py
find this line near the top:

python  API_BASE = os.getenv("API_URL", "https://logistics-backend-qwkm.onrender.com").rstrip("/")

change the url inside the quotes to your actual render url from step 1
save the file
open terminal in your project folder, run:

  git add Frontend/config.py
  git commit -m "update backend url"
  git push
one thing to know
render's free plan puts your backend to sleep if nobody uses it for a bit. so the first time someone opens your streamlit app after it's been idle, it might take 30-40 seconds to respond while render wakes the backend back up. not a bug, just how free hosting works.
