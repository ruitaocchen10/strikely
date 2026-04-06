from fastapi import APIRouter
from app.schemas import CoachReport
from app.cv.mock import MOCK_SESSION
from app.agent.coach import generate_report

router = APIRouter()

@router.post("/analyze", response_model=CoachReport)
async def analyze():
    return await generate_report(MOCK_SESSION)