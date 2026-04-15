import logging

from contextlib import asynccontextmanager

from fastapi import FastAPI

from src.infrastructure.adapters.input.api.routers import (
    deteccion_router,
    eventos_router,
    vehiculos_router,
)
from src.infrastructure.config.container import Container

logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s [%(levelname)s] %(name)s: %(message)s",
)

logger = logging.getLogger(__name__)

@asynccontextmanager
async def lifespan(app: FastAPI):
    """
    Ciclo de vida de la aplicación.
    Inicializa el container al arrancar y lo expone a los routers.
    """
    container = Container()

    # Sobrescribir las dependencias get_container de cada router
    app.dependency_overrides[deteccion_router.get_container] = lambda: container
    app.dependency_overrides[vehiculos_router.get_container] = lambda: container
    app.dependency_overrides[eventos_router.get_container] = lambda: container

    logger.info("Container inicializado")
    yield
    logger.info("Cerrando aplicación")


app = FastAPI(
    title="Detector de Placas Vehiculares",
    description=(
        "Sistema de control de acceso vehicular con detección automática de placas. "
        "Implementado con arquitectura hexagonal: YOLO para detección, EasyOCR para lectura, "
        "y SQLite/memoria para persistencia de eventos."
    ),
    version="1.0.0",
    lifespan=lifespan,
)


# Montar los routers
app.include_router(deteccion_router.router)
app.include_router(vehiculos_router.router)
app.include_router(eventos_router.router)


@app.get("/", tags=["Health"])
def root():
    """Endpoint de salud para verificar que la API está viva."""
    return {
        "status": "ok",
        "mensaje": "API de detección de placas operativa",
        "docs": "/docs",
    }