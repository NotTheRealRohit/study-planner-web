from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

from app.routers import calibration, progress, roadmap

app = FastAPI(
    title="Study Tracker Intelligence Service",
    description="Pillar A adaptation engines — calibration, progress, roadmap",
    version="0.1.0",
)

app.add_middleware(
    CORSMiddleware,
    allow_origins=["http://localhost:5173"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


@app.get("/health")
def health() -> dict[str, str]:
    return {"status": "ok"}


app.include_router(calibration.router, prefix="/v1")
app.include_router(progress.router, prefix="/v1")
app.include_router(roadmap.router, prefix="/v1")
