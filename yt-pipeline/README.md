# YouTube Content Intelligence Pipeline

A full-stack pipeline that takes a YouTube video URL, extracts its subtitles via yt-dlp, and uses Google Gemini to generate three short-form clip recommendations (with timestamps), a short LinkedIn post, a long LinkedIn post, and a Twitter/X post — all from a single AI call. Jobs are queued asynchronously via Celery and Redis, persisted in PostgreSQL, and surfaced through a React + Tailwind dashboard.

---

## Prerequisites

Before running anything, ensure the following are installed on your machine:

- **Python 3.11+**
- **Node 18+**
- **Docker** (for Postgres and Redis)
- **yt-dlp** — `pip install yt-dlp` or `brew install yt-dlp`
- **ffmpeg** — `brew install ffmpeg` (macOS) / `sudo apt install ffmpeg` (Linux) / `winget install ffmpeg` (Windows)

> ffmpeg must be available on the system PATH. Even though it is not called in V0, it is required at setup so later steps don't break.

---

## Setup

### 1. Configure environment variables

```bash
cp backend/.env.example backend/.env
```

Open `backend/.env` and fill in at minimum:

```
GEMINI_API_KEY=your_key_here
```

---

### 2. Start infrastructure (Postgres + Redis)

```bash
docker-compose up -d
```

---

### 3. Install Python dependencies

```bash
cd backend
pip install -r requirements.txt
```

---

### 4. Initialize the database

```bash
python db_init.py
```

---

### 5. Start the Celery worker

```bash
celery -A celery_app worker --loglevel=info
```

---

### 6. Start the FastAPI server

```bash
uvicorn app.main:app --reload --port 8000
```

API docs available at: `http://localhost:8000/docs`

---

### 7. Start the frontend

```bash
cd ../frontend
npm install
npm run dev
```

Frontend available at: `http://localhost:3000`

> Vite proxies all `/api` requests to FastAPI — no CORS configuration needed in dev.

---

## Verification

To verify the Step 0 scaffold is intact:

```bash
cd backend
python verify_step0.py
```

Expected output: `10/10 checks passed.`

---

## Project Structure

```
/yt-pipeline
  /backend
    /app
      /api          ← FastAPI route handlers
      /workers      ← Celery tasks
      /models       ← SQLAlchemy models
      /services     ← Business logic (extractor, parser, Gemini, job service)
      /schemas      ← Pydantic request/response schemas
      main.py       ← FastAPI entry point
      database.py   ← SQLAlchemy engine + session
    celery_app.py   ← Celery configuration
    db_init.py      ← Table creation script
    verify_step0.py ← Scaffold verification
    outputs/        ← Generated subtitle files (gitignored)
  /frontend
    /src
      /api          ← Axios API client
      /pages        ← SubmitPage, JobListPage, JobDetailPage
      /components   ← Shared UI components
      /hooks        ← Custom React hooks
    vite.config.js  ← Proxy + plugin config
  docker-compose.yml
```
