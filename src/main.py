"""
Point d'entrée principal pour Multi-Orchestrator-Bot
"""

import logging
from contextlib import asynccontextmanager
from typing import AsyncGenerator

from fastapi import FastAPI, Request
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import JSONResponse, FileResponse
from fastapi.staticfiles import StaticFiles
import uvicorn

from .api import router
from .storage import initialize_sample_data

# Configuration du logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)


@asynccontextmanager
async def lifespan(app: FastAPI) -> AsyncGenerator[None, None]:
    """Gestionnaire du cycle de vie de l'application"""
    logger.info("Démarrage de Multi-Orchestrator-Bot...")

    # Initialisation des données d'exemple
    initialize_sample_data()
    logger.info("Données d'exemple initialisées")

    yield

    logger.info("Arrêt de Multi-Orchestrator-Bot...")


def create_application() -> FastAPI:
    """Crée et configure l'application FastAPI"""

    # Crée une nouvelle app au lieu d'utiliser celle déjà créée
    app = FastAPI(
        title="Multi-Orchestrator-Bot",
        description="Plateforme de trading algorithmique",
        version="1.0.0",
        docs_url="/docs",
        redoc_url="/redoc",
        lifespan=lifespan,
    )

    # Middleware CORS
    app.add_middleware(
        CORSMiddleware,
        allow_origins=["*"],  # À restreindre en production
        allow_credentials=True,
        allow_methods=["*"],
        allow_headers=["*"],
    )

    # Gestionnaire d'exceptions global
    @app.exception_handler(Exception)
    async def global_exception_handler(request: Request, exc: Exception):
        logger.error(f"Exception globale: {exc}", exc_info=True)
        return JSONResponse(
            status_code=500,
            content={"detail": "Erreur interne du serveur"},
        )

    # Servir les fichiers statiques
    app.mount("/static", StaticFiles(directory="static"), name="static")

    # Route pour la page principale
    @app.get("/")
    async def read_root():
        return FileResponse("static/index.html", media_type="text/html")

    # Inclure les routes API
    app.include_router(router, prefix="/api")

    return app


# Instance globale de l'application
app = create_application()


if __name__ == "__main__":
    uvicorn.run(
        "src.main:app",
        host="0.0.0.0",
        port=8000,
        reload=True,
        log_level="info",
        access_log=True,
    )
