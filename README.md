# ai-knowledge-assistant

Monorepo for an AI knowledge assistant: **Next.js** frontend, **FastAPI** backend, **PostgreSQL-oriented** SQL schema, **Terraform** for infrastructure, and **GitHub Actions** for CI.

## Structure

```
ai-knowledge-assistant/
├── frontend/          # Next.js (App Router), TypeScript, Tailwind CSS
├── backend/           # FastAPI
├── database/          # SQL schema
├── infra/             # Terraform
└── .github/workflows/ # CI/CD
```

## Prerequisites

- **Node.js** 20+ (CI uses 22)
- **Python** 3.12+
- **Terraform** 1.5+ (when you start defining cloud resources)

## Setup

### Frontend (port 3000)

```bash
cd frontend
npm install
npm run dev
```

Open [http://localhost:3000](http://localhost:3000).

### Backend (port 8000)

```bash
cd backend
python -m venv .venv
# Windows PowerShell:
.venv\Scripts\Activate.ps1
# macOS/Linux:
# source .venv/bin/activate

pip install -r requirements.txt
uvicorn main:app --reload --host 0.0.0.0 --port 8000
```

- API root: [http://localhost:8000](http://localhost:8000)
- Health: [http://localhost:8000/api/health](http://localhost:8000/api/health)
- OpenAPI docs: [http://localhost:8000/docs](http://localhost:8000/docs)

### Database

Apply `database/schema.sql` to your PostgreSQL instance when you connect the app (schema is a starting point only).

### Infrastructure

```bash
cd infra
terraform init
terraform plan
```

## CI

On push/PR to `main` or `master`, the workflow lints and builds the frontend and installs/compiles the backend.

## License

Private / unlicensed until you add one.
