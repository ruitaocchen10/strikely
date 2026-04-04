# Initial Brainstorm

## Problem

I can't always figure out exactly what I'm doing wrong or what I need to work on when I'm training my striking abilities in mixed-martial arts. Coaches aren't always accessible, and when I'm watching my footage I'm certainly liable to missing things.

## Proposed Solution

AI Agent that can watch and review your training footage and identify mistakes you're making, opportunities to improve, and in general give you the ability to chat with someone about improving your striking abilities.

## Ideas

### Backend - FastAPI

User uploads whatever footage they want --> FastAPI receives and stores it
Computer vision pipeline (OpenCV + MediaPipe) --> Processes the video and extracts pose keypoints, tracking movement, counting strikes, etc. etc.
MCP Server (built with FastAPI or whatever stack would work best) --> exposes processed results as structured tools
AI agent calls these tools and synthesizes coach-style feedback
FastAPI gives feedback back to the frontend

### MVP

Let's keep it simple for the MVP and try to get the logic working first before we turn this into a fully fledged app. We can create a simple frontend with Next.js that can accept a video file and then display an AI Agent's feedback. The focus is to get the backend working, to get the computer vision pipeline and create the MCP server that can be used by the AI agent.

# Notes

For a general analysis, it might be easier to simply inject data into a prompt. However, MCP can become powerful when chatting with a user about specific details in the training, and can allow the agent to query specific data on demand.

# Claude Plan

## Scope (MVP)

- **Footage**: Solo drilling only (single person in frame)
- **Discipline**: Boxing first (jab, cross, hook, uppercut)
- **Feedback loop**: Upload → auto-report (no chat for MVP)
- MCP server included from the start to set up the tool interface that the future chat feature will reuse

## Architecture

```
Video Upload (Next.js)
  → POST /api/upload (FastAPI)
  → CV Pipeline (OpenCV + MediaPipe)
      - Extract pose landmarks per frame
      - Detect + classify strikes
      - Apply technique quality flags
  → SessionAnalysis (structured JSON)
  → MCP Server (in-process, mcp Python SDK)
      - Tools: get_session_summary, get_strike_list,
               get_strike_detail, get_flag_list
  → Coaching Agent (Claude API + tool_use)
  → CoachReport (JSON)
  → Return to Next.js frontend
```

## Project Structure

```
strikely/
├── main.py                      # FastAPI app entry point
├── requirements.txt
├── .env.example                 # ANTHROPIC_API_KEY placeholder
├── app/
│   ├── api/
│   │   └── routes.py            # POST /upload endpoint
│   ├── cv/
│   │   ├── pipeline.py          # Orchestrates full CV analysis
│   │   ├── pose.py              # MediaPipe landmark extraction per frame
│   │   ├── strikes.py           # Strike detection + classification
│   │   └── quality.py           # Rule-based technique flag checks
│   ├── mcp/
│   │   └── server.py            # MCP tool definitions (loaded with SessionAnalysis)
│   ├── agent/
│   │   └── coach.py             # Claude agent that calls MCP tools → report
│   └── schemas.py               # Pydantic models for all data types
└── frontend/
    └── app/
        └── page.tsx             # Upload form + formatted report display
```

## Data Schemas

- `Strike` — id, type (jab/cross/hook/uppercut), start_frame, peak_frame, end_frame, hand
- `QualityFlag` — strike_id, flag_type (GUARD_DROPPED / CHIN_EXPOSED / OVEREXTENDED / HIP_ROTATION_LIMITED), severity, description
- `SessionAnalysis` — fps, frame_count, duration_seconds, detected_strikes, quality_flags
- `CoachReport` — summary, strengths, issues, recommended_drills

## CV Pipeline Logic

**Strike detection** (`strikes.py`): Compute wrist velocity per frame; velocity spike = strike event. Classify by hand (lead/rear) and trajectory:

- Jab: lead hand, forward extension
- Cross: rear hand, hip rotation + forward extension
- Hook: lateral arc trajectory
- Uppercut: upward wrist trajectory

**Technique flags** (`quality.py`): At peak extension frame per strike:

- `GUARD_DROPPED`: non-striking wrist drops below chin
- `CHIN_EXPOSED`: nose rises above shoulder midpoint
- `OVEREXTENDED`: striking elbow angle exceeds threshold
- `HIP_ROTATION_LIMITED`: insufficient hip landmark rotation on cross

## MCP Tools

- `get_session_summary()` → duration, total strikes, strike type breakdown, flag frequencies
- `get_strike_list()` → all strikes with id, type, timestamp, flag count
- `get_strike_detail(strike_id)` → full strike data + associated quality flags
- `get_flag_list(flag_type?)` → all flags, optionally filtered by type

## Known Risks

- Strike detection velocity thresholds need empirical tuning against real footage
- MediaPipe accuracy on fast punching motion may require frame smoothing
- MCP in-process pattern may require using Claude API's native tool_use with MCP-compatible schemas instead of a true MCP transport — evaluate during implementation
