from pathlib import Path
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from fastapi.staticfiles import StaticFiles
from .config import settings
from .database import init_db
from .routes.api import router as api_router
from .routes.pages import router as pages_router
BASE_DIR=Path(__file__).resolve().parent
app=FastAPI(title=settings.app_name,version="1.0.0",description="Budget-aware multimodal recommendation assistant")
app.add_middleware(CORSMiddleware,allow_origins=["http://127.0.0.1:8000","http://localhost:8000"],allow_credentials=True,allow_methods=["*"],allow_headers=["*"])
app.mount("/static",StaticFiles(directory=str(BASE_DIR/"static")),name="static")
app.include_router(pages_router); app.include_router(api_router)
@app.on_event("startup")
def startup(): init_db()
