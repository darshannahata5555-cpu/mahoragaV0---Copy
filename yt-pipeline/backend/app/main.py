from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

from app.api.jobs import router as jobs_router

app = FastAPI(
    title="YouTube Content Intelligence Pipeline",
    version="1.0.0",
    description="Extracts subtitles from YouTube videos and generates short clips, LinkedIn posts, and Twitter posts via Gemini AI.",
)

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # Restrict to FRONTEND_URL in production
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# TODO: Replace polling with Server-Sent Events (SSE) for production

app.include_router(jobs_router)


@app.get("/health", tags=["health"])
def health_check():
    return {"status": "ok", "version": "1.0.0"}
