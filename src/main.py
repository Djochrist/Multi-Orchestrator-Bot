"""
Point d'entrée principal pour Multi-Orchestrator-Bot
"""

import logging
import os
from contextlib import asynccontextmanager
from typing import AsyncGenerator

from fastapi import FastAPI, Request, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import JSONResponse, FileResponse
from fastapi.staticfiles import StaticFiles
import uvicorn

from .api import router
from .storage import initialize_sample_data

# Logging (safe avec Uvicorn / Gunicorn)

logger = logging.getLogger("multi_orchestrator")
logger.setLevel(logging.INFO)

# Lifespan
@asynccontextmanager
async def lifespan(app: FastAPI) -> AsyncGenerator[None, None]:
    """Gestionnaire du cycle de vie de l'application"""
    logger.info("Démarrage de Multi-Orchestrator-Bot...")

    try:
        initialize_sample_data()
        logger.info("Données d'exemple initialisées")
    except Exception:
        logger.exception("Erreur lors de l'initialisation des données")

    yield

    logger.info("Arrêt de Multi-Orchestrator-Bot...")

def create_application() -> FastAPI:
    """Crée et configure l'application FastAPI"""

    app = FastAPI(
        title="Multi-Orchestrator-Bot",
        description="Plateforme de trading algorithmique",
        version="1.0.0",
        docs_url="/docs",
        redoc_url="/redoc",
        lifespan=lifespan,
    )

    allowed_origins = os.getenv("ALLOWED_ORIGINS", "*").split(",")

    app.add_middleware(
        CORSMiddleware,
        allow_origins=allowed_origins,
        allow_credentials=True,
        allow_methods=["*"],
        allow_headers=["*"],
    )


    @app.exception_handler(HTTPException)
    async def http_exception_handler(request: Request, exc: HTTPException):
        return JSONResponse(
            status_code=exc.status_code,
            content={"detail": exc.detail},
        )

    @app.exception_handler(Exception)
    async def global_exception_handler(request: Request, exc: Exception):
        logger.error("Exception globale", exc_info=True)
        return JSONResponse(
            status_code=500,
            content={"detail": "Erreur interne du serveur"},
        )


    if os.path.isdir("static"):
        app.mount("/static", StaticFiles(directory="static"), name="static")

    async def read_root() -> FileResponse:
        index_path = os.path.join("static", "index.html")
        if not os.path.exists(index_path):
            raise HTTPException(status_code=404, detail="Page non disponible")
        return FileResponse(index_path, media_type="text/html")

    app.include_router(router, prefix="/api")

    return app

app = create_application()

if __name__ == "__main__":
    uvicorn.run(
        "src.main:app",
        host="0.0.0.0",
        port=8000,
        reload=os.getenv("ENV", "dev") == "dev",
        log_level="info",
        access_log=True,
    )

