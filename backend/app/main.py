"""FastAPI main application for real-time meeting translator."""
from fastapi import FastAPI, WebSocket
from fastapi.middleware.cors import CORSMiddleware
from fastapi.staticfiles import StaticFiles
from fastapi.responses import HTMLResponse
from app.api.routes import router
import os

app = FastAPI(
    title="Real-time Meeting Translator",
    description="Multilingual meeting translator with speaker diarization",
    version="1.0.0"
)

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

app.include_router(router, prefix="/api")

frontend_dist = os.path.join(os.path.dirname(os.path.dirname(os.path.dirname(__file__))), "frontend", "dist")
if os.path.exists(frontend_dist):
    app.mount("/", StaticFiles(directory=frontend_dist, html=True), name="static")

@app.get("/")
async def root():
    if os.path.exists(frontend_dist):
        with open(os.path.join(frontend_dist, "index.html")) as f:
            return HTMLResponse(f.read())
    return {"status": "ok", "service": "realtime-meeting-translator"}