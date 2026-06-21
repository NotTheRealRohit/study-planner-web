import os

from fastapi import Depends, FastAPI
from fastapi.middleware.cors import CORSMiddleware

from app.routers import calibration, progress, roadmap
from app.security import require_user

DEFAULT_CORS_ORIGINS = ["http://localhost:5173"]


def parse_cors_origins(value: str | None) -> list[str]:
    if value is None or value.strip() == "":
        return DEFAULT_CORS_ORIGINS

    origins = [origin.strip() for origin in value.split(",") if origin.strip()]
    return origins or DEFAULT_CORS_ORIGINS


app = FastAPI(
    title="Study Tracker Intelligence Service",
    description="Pillar A adaptation engines — calibration, progress, roadmap",
    version="0.1.0",
)

app.add_middleware(
    CORSMiddleware,
    allow_origins=parse_cors_origins(os.getenv("CORS_ORIGINS")),
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


@app.get("/health")
def health() -> dict[str, str]:
    return {"status": "ok"}


app.include_router(calibration.router, prefix="/v1", dependencies=[Depends(require_user)])
app.include_router(progress.router, prefix="/v1", dependencies=[Depends(require_user)])
app.include_router(roadmap.router, prefix="/v1", dependencies=[Depends(require_user)])
