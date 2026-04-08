import os
import tempfile
from fastapi import APIRouter, UploadFile, File
from app.schemas import CoachReport, SessionAnalysis
from app.cv.pipeline import analyze_video
from app.agent.coach import generate_report

router = APIRouter()

async def _save_upload(video: UploadFile) -> str:
    suffix = os.path.splitext(video.filename)[1]
    with tempfile.NamedTemporaryFile(delete=False, suffix=suffix) as tmp:
        tmp.write(await video.read())
        return tmp.name

@router.post("/debug/cv", response_model=SessionAnalysis)
async def debug_cv(video: UploadFile = File(...)):
    """Returns raw CV pipeline output — strikes and flags — without running the agent."""
    tmp_path = await _save_upload(video)
    try:
        return analyze_video(tmp_path)
    finally:
        os.unlink(tmp_path)

@router.post("/analyze", response_model=CoachReport)
async def analyze(video: UploadFile = File(...)):
    tmp_path = await _save_upload(video)
    try:
        analysis = analyze_video(tmp_path)
        return await generate_report(analysis)
    finally:
        os.unlink(tmp_path)