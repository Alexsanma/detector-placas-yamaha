from fastapi import APIRouter, Depends, File, HTTPException, UploadFile, status

from src.application.dtos.deteccion_dto import ProcesarDeteccionInput
from src.domain.exceptions import ConfianzaBajaError, PlacaNoDetectadaError
from src.infrastructure.adapters.input.api.schemas.deteccion_schema import (
    DeteccionResponseSchema,
)
from src.infrastructure.config.container import Container

router = APIRouter(prefix="/detectar", tags=["Detección"])


def get_container() -> Container:
    """Dependencia que provee el container (se sobrescribe en main.py)."""
    raise NotImplementedError("Container no inicializado")


@router.post(
    "",
    response_model=DeteccionResponseSchema,
    summary="Detectar placa en una imagen",
    description="Recibe una imagen, detecta la placa, la clasifica y registra el evento.",
)
async def detectar_placa(
    imagen: UploadFile = File(..., description="Imagen del vehículo"),
    camera_id: int | None = None,
    container: Container = Depends(get_container),
):
    # Validar tipo de archivo
    if not imagen.content_type or not imagen.content_type.startswith("image/"):
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="El archivo debe ser una imagen.",
        )

    # Leer bytes de la imagen
    imagen_bytes = await imagen.read()
    if not imagen_bytes:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="La imagen está vacía.",
        )

    # Obtener caso de uso y ejecutar
    use_case = container.procesar_deteccion_use_case()

    try:
        resultado = use_case.ejecutar(
            ProcesarDeteccionInput(imagen_bytes=imagen_bytes, camera_id=camera_id)
        )
    except PlacaNoDetectadaError as e:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail=str(e))
    except ConfianzaBajaError as e:
        raise HTTPException(status_code=status.HTTP_422_UNPROCESSABLE_ENTITY, detail=str(e))

    # Mapear output del caso de uso a schema de respuesta
    return DeteccionResponseSchema(
        evento_id=resultado.evento_id,
        placa=resultado.placa,
        tipo_evento=resultado.tipo_evento.value,
        tipo_vehiculo=resultado.tipo_vehiculo.value,
        confianza_deteccion=resultado.confianza_deteccion,
        confianza_ocr=resultado.confianza_ocr,
        fecha_hora=resultado.fecha_hora,
        camera_id=resultado.camera_id,
    )