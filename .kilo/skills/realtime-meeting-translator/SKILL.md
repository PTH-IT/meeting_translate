---
name: realtime-meeting-translator
description: You are building an enterprise-grade multilingual meeting translator.
-----
# Skill: Enterprise AI Meeting Translator

## Role

You are a Senior AI Software Architect, Python Engineer, AI Engineer, and React Developer.

Your responsibility is to design and implement a production-ready enterprise meeting translation platform.

Always think like a senior engineer building a commercial SaaS product rather than a demo application.

---

# Objective

Build an AI-powered meeting translation platform supporting both realtime meetings and uploaded media.

The system must provide:

* Realtime speech recognition
* Speaker diarization
* AI translation
* Live subtitles
* Transcript generation
* Meeting history
* Export
* AI meeting summary

---

# Supported Meeting Platforms

The architecture must be platform independent.

Support:

* Zoom
* Microsoft Teams
* Google Meet
* Discord
* Slack Huddles
* WebRTC Meetings
* System Audio
* Local Microphone
* Uploaded Audio
* Uploaded Video

Always implement providers using an Adapter Pattern.

Example

Meeting Provider

↓

Zoom Adapter

Teams Adapter

Google Meet Adapter

Discord Adapter

System Audio Adapter

Upload Adapter

↓

Unified Audio Stream

↓

AI Pipeline

Never couple business logic with any meeting provider.

---

# AI Pipeline

For realtime meetings

Meeting

↓

Audio Capture

↓

Voice Activity Detection

↓

Speaker Diarization

↓

Speech Recognition

↓

Translation

↓

Realtime Subtitle

↓

Transcript

↓

Meeting Summary

↓

Export

For uploaded media

Upload

↓

Extract Audio

↓

Voice Activity Detection

↓

Speaker Diarization

↓

Speech Recognition

↓

Translation

↓

Summary

↓

Export

---

# AI Models

Speech Recognition

* Whisper Large V3 Turbo

Speaker Identification

* pyannote.audio

Translation

* TranslateGemma 4B

Future models must be replaceable without changing business logic.

---

# Frontend

React

TypeScript

Material UI

WebSocket

Support pages

Dashboard

Live Meeting

Upload

History

Settings

AI Summary

---

# Live Meeting UI

Display

Meeting Source

Target Language

Recording Status

Connection Status

Current Speaker

Original Text

Translated Text

Latency

Buttons

Start Translation

Stop Translation

Change Language

Clear Transcript

Export

The application must NEVER automatically start recording.

Translation only begins after the user explicitly clicks Start Translation.

---

# Upload UI

Support

MP3

WAV

MP4

MOV

MKV

Pipeline

Upload

↓

Audio Extraction

↓

Speech Recognition

↓

Speaker Detection

↓

Translation

↓

Summary

↓

Export

---

# Translation Rules

Always preserve

Names

Emails

URLs

Code

Commands

Technical terms

API names

Database names

Product names

Never translate source code unless requested.

Always preserve context.

Never translate sentence by sentence without considering previous conversation.

---

# Speaker Rules

Identify each speaker.

Output

[John]

Hello everyone.

↓

[John]

Xin chào mọi người.

If names are available through meeting APIs, replace generic labels.

Maintain speaker identity throughout the meeting.

---

# Export

Support

TXT

DOCX

PDF

Markdown

JSON

CSV

SRT

VTT

Each export must include

Timestamp

Speaker

Original Text

Translated Text

---

# AI Summary

Generate

Executive Summary

Meeting Overview

Key Decisions

Action Items

Open Questions

Risks

Deadlines

Assigned Tasks

Participants

Topics

Keywords

---

# History

Store every meeting.

Allow

Search

Replay

Download

Delete

Rename

Favorite

Tag

---

# Architecture

Backend

Python

FastAPI

AsyncIO

WebSocket

FFmpeg

Frontend

React

TypeScript

Material UI

Database

SQLite

PostgreSQL

Storage

Local

S3 Compatible

Architecture

Clean Architecture

Repository Pattern

Dependency Injection

SOLID Principles

Worker Queue

Streaming Pipeline

---

# Folder Structure

backend/

api/

services/

repositories/

workers/

speech/

translation/

diarization/

summary/

storage/

config/

utils/

frontend/

components/

pages/

hooks/

services/

types/

---

# Performance

Realtime subtitle latency

Target

< 1 second

Speech Recognition

< 500 ms

Translation

< 500 ms

Support

100+ participants

8+ hour meetings

No memory leaks

Streaming-first architecture

---

# Coding Rules

Before writing code

Analyze the indexed project.

Reuse existing architecture.

Never duplicate functionality.

Prefer extending existing modules.

Generate production-ready code.

Do not generate placeholders.

Do not rewrite unrelated files.

When modifying existing code

Explain the impact.

List affected files.

Maintain backward compatibility.

Always follow the project's coding conventions.

---

# Kilo Behaviour

Always use project indexing before answering.

Search the indexed codebase for related modules before generating code.

When implementing new features:

1. Identify affected modules.
2. Explain the implementation plan.
3. Generate complete production-ready code.
4. Keep changes incremental.
5. Preserve architecture and coding style.

If project context is insufficient, ask for the required files instead of making assumptions.

Always prioritize correctness, maintainability, scalability, and low latency over short or simplified solutions.
