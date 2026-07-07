# AGENTS.md

Real-time multilingual meeting translator with speaker diarization.

## Structure

* `backend/` - FastAPI backend responsible for APIs, WebSocket streaming, business logic, and meeting orchestration

  * `app/api/` - REST and WebSocket endpoints
  * `app/services/` - Business services (meeting management, auth, export, performance, etc.)
  * `app/adapters/` - Meeting platform adapters (Zoom, Teams, Google Meet, Discord, System Audio, Upload)
  * `app/models/` - Database models for meetings, speakers, transcripts
  * `app/core/` - Shared backend configuration and utilities

* `ai/` - AI platform and inference layer

  * `models/` - AI model wrappers (Whisper, pyannote, Gemma, etc.)
  * `pipelines/` - End-to-end AI pipelines (Transcription, Diarization, Translation, AI Analysis)
  * `loaders/` - Model loading, downloading, caching, and initialization
  * `preprocess/` - Audio preprocessing and feature extraction
  * `postprocess/` - Output formatting, entity preservation, confidence scoring
  * `inference/` - Realtime inference orchestration
  * `utils/` - Shared AI utilities

* `frontend/` - React + TypeScript frontend

* `docker/` - Docker configuration for backend, frontend, and AI services

* `models/` - Local AI model cache (mounted as Docker volume, not source code)

## Commands

```bash
# One-command setup (Windows)
setup.bat

# One-command setup (Unix)
./setup.sh

# One-command run (Windows)
start.bat

# One-command run (Unix)
./start.sh

# Docker deployment
cd docker
docker compose up --build
```

## Architecture

```
Meeting Provider
        │
        ▼
Meeting Adapter
        │
        ▼
Unified Audio Stream
        │
        ▼
Audio Preprocessing (FFmpeg)
        │
        ▼
Voice Activity Detection (VAD)
        │
        ▼
AI Pipeline
 ├── Whisper (Speech-to-Text)
 ├── pyannote (Speaker Diarization)
 ├── Translation Model
 └── AI Analysis
        │
        ▼
Backend Services
        │
        ▼
WebSocket Streaming
        │
        ▼
React UI
```

## Responsibilities

### Backend

* API and WebSocket communication
* Meeting lifecycle management
* Authentication and authorization
* Transcript persistence
* Export functionality
* Business rules
* Performance monitoring

### AI

* Speech recognition
* Speaker diarization
* Machine translation
* AI analysis
* Model loading and caching
* Inference optimization
* Audio preprocessing/postprocessing

### Frontend

* Realtime transcript display
* Multi-language translation panels
* Speaker visualization
* Meeting controls
* Export interface

## Notes

* Source language is automatically detected.
* Supported target languages: Vietnamese (`vi`), English (`en`), Japanese (`ja`), Chinese (`zh`).
* Preserve entities (names, URLs, email addresses, numbers) during translation.
* Maintain speaker identity throughout the entire pipeline.
* NEVER start recording automatically. Translation only begins after the user explicitly presses **Start Translation**.
* AI models must remain isolated from backend business logic.
* Backend should communicate with AI through well-defined interfaces or pipelines rather than directly manipulating model implementations.
* Keep AI components modular so additional models (OCR, embeddings, LLMs, summarization, sentiment analysis, etc.) can be added without changing backend business logic.
* Store downloaded model weights under the `models/` directory instead of inside source code directories.

## Performance Targets

| Component                | Target Latency |
| ------------------------ | -------------: |
| Voice Activity Detection |       < 100 ms |
| Speech-to-Text           |       < 500 ms |
| Speaker Diarization      |       < 500 ms |
| Translation              |       < 500 ms |
| End-to-End Processing    |     < 1 second |
