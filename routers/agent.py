import json
import asyncio
from fastapi import APIRouter, Depends, Query
from fastapi.responses import StreamingResponse
from sqlalchemy.ext.asyncio import AsyncSession
from models.database import get_db
from services.agent_service import run_agent

router = APIRouter(prefix="/agent", tags=["agent"])


@router.get("/research")
async def research(
    category: str = Query(default="genel", description="Kategori: elektronik, spor, ev, güzellik, evcil, genel"),
    db: AsyncSession = Depends(get_db),
):
    async def event_stream():
        try:
            async for step_data in run_agent(category, db):
                yield f"data: {json.dumps(step_data, ensure_ascii=False)}\n\n"
        except Exception as e:
            yield f"data: {json.dumps({'step': 'error', 'message': str(e)})}\n\n"
        yield "data: [DONE]\n\n"

    return StreamingResponse(
        event_stream(),
        media_type="text/event-stream",
        headers={
            "Cache-Control": "no-cache",
            "X-Accel-Buffering": "no",
            "Access-Control-Allow-Origin": "*",
        },
    )
