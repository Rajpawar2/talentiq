from contextlib import asynccontextmanager
from fastapi import FastAPI, WebSocket, WebSocketDisconnect, Request, status
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import JSONResponse
from fastapi.exceptions import RequestValidationError

from app.config import settings
from app.database import init_db
from app.api import auth, resumes, jobs, matching, interviews, questions, evaluations, analytics, voice
from app.websocket.manager import ws_manager

@asynccontextmanager
async def lifespan(app: FastAPI):
    # Initialize database tables on startup
    init_db()
    yield

app = FastAPI(
    title=settings.PROJECT_NAME,
    version=settings.VERSION,
    description="AI-Powered Adaptive Interview & Talent Assessment Platform API",
    lifespan=lifespan,
    docs_url="/docs",
    redoc_url="/redoc"
)

# CORS Configuration
app.add_middleware(
    CORSMiddleware,
    allow_origins=settings.CORS_ORIGINS,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Global validation exception handler
@app.exception_handler(RequestValidationError)
async def validation_exception_handler(request: Request, exc: RequestValidationError):
    errors = []
    for err in exc.errors():
        loc = " -> ".join([str(l) for l in err.get("loc", [])])
        msg = err.get("msg", "Invalid value")
        errors.append(f"{loc}: {msg}")
    return JSONResponse(
        status_code=status.HTTP_422_UNPROCESSABLE_ENTITY,
        content={"detail": "Validation error", "errors": errors}
    )

# Include API Routers under /api
app.include_router(auth.router, prefix="/api")
app.include_router(resumes.router, prefix="/api")
app.include_router(jobs.router, prefix="/api")
app.include_router(matching.router, prefix="/api")
app.include_router(interviews.router, prefix="/api")
app.include_router(questions.router, prefix="/api")
app.include_router(evaluations.router, prefix="/api")
app.include_router(analytics.router, prefix="/api")
app.include_router(voice.router, prefix="/api")

@app.get("/api/health")
def health_check():
    """Health check endpoint displaying system and AI provider configuration."""
    return {
        "status": "healthy",
        "service": settings.PROJECT_NAME,
        "version": settings.VERSION,
        "ai_mock_mode": settings.AI_MOCK_MODE,
        "ai_provider": settings.AI_PROVIDER,
        "stt_provider": settings.STT_PROVIDER
    }

# Real-time interview room WebSocket
@app.websocket("/ws/interview/{interview_id}")
async def interview_websocket_endpoint(websocket: WebSocket, interview_id: str):
    await ws_manager.connect(interview_id, websocket)
    try:
        while True:
            data = await websocket.receive_text()
            # Echo or broadcast heartbeats / typing events
            await ws_manager.broadcast_to_room(interview_id, {
                "event": "client_message",
                "content": data
            })
    except WebSocketDisconnect:
        ws_manager.disconnect(interview_id, websocket)
    except Exception:
        ws_manager.disconnect(interview_id, websocket)
