# Docker Setup

## 1) Configure Backend Environment

1. Copy `backend/.env.example` to `backend/.env`.
2. Fill in `DATABASE_URL`, `SECRET_KEY`, and optional Razorpay values.

## 2) Build and Run

From the project root:

```bash
docker compose up --build
```

## 3) Access Services

- Frontend: `http://localhost:5173`
- Backend API: `http://localhost:8000`
- Backend health: `http://localhost:8000/health`

## Notes

- Frontend Nginx proxies `/api/*` requests to the backend container.
- Uploaded resumes are persisted on host at `backend/uploads`.
- Stop containers with:

```bash
docker compose down
```
