from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from fastapi.staticfiles import StaticFiles
from fastapi.responses import FileResponse
from pathlib import Path

from .database import engine, Base
from .routers import auth, seeker, employer, admin

# Initialize Database (Ensures tables exist, though we have init_tables.py too)
Base.metadata.create_all(bind=engine)

app = FastAPI(title="Job Portal API")

# CORS Setup
origins = ["*"] # Allow all for simplicity in development

app.add_middleware(
    CORSMiddleware,
    allow_origins=origins,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Include Routers
app.include_router(auth.router)
app.include_router(seeker.router)
app.include_router(employer.router)
app.include_router(admin.router)

# Serve frontend static files (so visiting http://127.0.0.1:8000 loads the SPA)
BASE_DIR = Path(__file__).resolve().parent.parent
FRONTEND_DIR = BASE_DIR / "frontend"

# Mount static files at root as a fallback for any non-API path
app.mount("/", StaticFiles(directory=str(FRONTEND_DIR), html=True), name="frontend")

# Optional explicit root route that returns index.html (exact match takes precedence)
@app.get("/")
def read_root():
    index_path = FRONTEND_DIR / "index.html"
    if index_path.exists():
        return FileResponse(index_path)
    return {"message": "Welcome to Job Portal API"}
