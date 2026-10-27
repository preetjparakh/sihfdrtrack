# AICTE FDR Portal Prototype

A synthetic FDR workflow prototype with a Next.js portal, FastAPI service, and mock bank-verification service.

## Deploy a public demo

[![Deploy to Render](https://render.com/images/deploy-to-render-button.svg)](https://render.com/deploy?repo=https://github.com/preetjparakh/sihfdrtrack)

Render reads `render.yaml` and creates the portal, API, mock-bank service, and PostgreSQL database. After the deployment finishes, open the `aicte-fdr-portal` service in Render and use its `onrender.com` URL to share the demo.

The blueprint uses free resources for a preview. Free web services can sleep when idle, uploaded files use ephemeral storage, and the free PostgreSQL database expires after 30 days. Demo seed data is initialized only when the database is empty.

## Demo safety

This is a public prototype, not a production system. The persona selector uses demo identities and does not provide real user authentication. Anyone with the public URL may act as a demo persona. Use synthetic data only; never upload real FDR documents, personal information, or financial records.

## Local development

Configure the backend from `.env.example`, install Python dependencies with `pip install -r requirements.txt`, and run `python backend/seed_db.py` plus `python mock_bank/seed_bank.py` for local seed data. Start the API with `uvicorn backend.app.main:app --reload --port 8000`, the mock bank with `uvicorn mock_bank.app.main:app --reload --port 8001`, and the frontend from `frontend` with `npm install` and `npm run dev`.
