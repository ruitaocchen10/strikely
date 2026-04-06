# CLAUDE.md

This file provides guidance to Claude Code (claude.ai/code) when working with code in this repository.

## Project

Strikely — an AI-powered boxing technique coach. Users upload training footage and receive a structured coaching report identifying technique issues and recommended drills.

Entry point: `main.py` (FastAPI app). Run with `uvicorn main:app --reload`.

## Architecture

```
Video upload → FastAPI → CV pipeline → SessionAnalysis
  → MCP server (in-process) → Claude agent (tool-use loop) → CoachReport → frontend
```

## Structure

- `main.py` — FastAPI app, CORS middleware, router mount (router currently commented out)
- `app/schemas.py` — Pydantic models: `Strike`, `QualityFlag`, `SessionAnalysis`, `CoachReport`, `Issue`
- `app/cv/mock.py` — Hardcoded `SessionAnalysis` for development (CV pipeline not yet built)
- `app/mcp/server.py` — `create_mcp_server(analysis)` factory; exposes 4 tools: `get_session_summary`, `get_strike_list`, `get_strike_detail`, `get_flag_list`
- `app/agent/coach.py` — `generate_report(analysis)`: runs Claude tool-use loop against MCP tools, returns `CoachReport`

## What's not built yet

- `app/api/routes.py` — `POST /upload` endpoint (next step)
- `app/cv/pipeline.py` — real CV pipeline with OpenCV + MediaPipe (deferred, using mock data for now)
- `frontend/` — Next.js upload form + report display

## Commands

```bash
uvicorn main:app --reload   # start backend
```

Requires `ANTHROPIC_API_KEY` in a `.env` file at the project root.
