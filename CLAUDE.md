# CLAUDE.md

This file provides guidance to Claude Code (claude.ai/code) when working with code in this repository.

## Project

Strikely — an AI-powered boxing technique coach. Users upload training footage and receive a structured coaching report identifying technique issues and recommended drills.

Entry point: `main.py` (FastAPI app). Run with `uvicorn main:app --reload`.

## Architecture

```
Video upload → FastAPI → CV pipeline (OpenCV + MediaPipe) → SessionAnalysis
  → MCP server (in-process) → Claude agent (tool-use loop) → CoachReport → Next.js frontend
```

## Structure

- `main.py` — FastAPI app, CORS middleware (allows localhost:3000), mounts router from `app/api/routes`
- `app/schemas.py` — Pydantic models: `Strike`, `QualityFlag`, `SessionAnalysis`, `CoachReport`, `Issue`
- `app/cv/pipeline.py` — `analyze_video(video_path)`: OpenCV + MediaPipe PoseLandmarker, detects strikes via wrist velocity, classifies strike type, generates quality flags
- `app/cv/mock.py` — Hardcoded `SessionAnalysis` (25 strikes, 18 flags) — available for testing but not used by any active route
- `app/mcp/server.py` — `create_mcp_server(analysis)` factory and `get_tool_functions(analysis)` dict; 4 tools: `get_session_summary`, `get_strike_list`, `get_strike_detail`, `get_flag_list`
- `app/agent/coach.py` — `generate_report(analysis)`: async Claude tool-use loop (claude-sonnet-4-6, max 10 iterations), returns `CoachReport`
- `app/api/routes.py` — Two POST endpoints:
  - `POST /analyze` — runs CV pipeline + agent, returns `CoachReport`
  - `POST /debug/cv` — runs CV pipeline only, returns raw `SessionAnalysis` (for testing)
- `frontend/` — Next.js 16 + React 19 + Tailwind CSS v4 single-page app; upload form, analyze/debug buttons, report display

## Known Issues

- CV pipeline accuracy is poor — velocity thresholds and rule-based strike classifier are untuned for real footage
- No tests anywhere in the codebase

## Commands

```bash
uvicorn main:app --reload        # start backend
cd frontend && npm run dev       # start frontend (localhost:3000)
```

Requires `ANTHROPIC_API_KEY` in a `.env` file at the project root.
