from datetime import datetime
from typing import Optional

from pydantic import BaseModel, Field


class DeteccionResponseSchema(BaseModel):
    """Respuesta del endpoint de detección de placas."""

    evento_id: Optional[int] = Field(None, description="ID del evento registrado")
    placa: str = Field(..., description="Placa detectada y reconocida")
    tipo_evento: str = Field(..., description="Tipo de evento: ingreso o salida")
    tipo_vehiculo: str = Field(..., description="Tipo de vehículo: registrado o visitante")
    confianza_deteccion: float = Field(..., description="Confianza del detector YOLO (0-1)")
    confianza_ocr: float = Field(..., description="Confianza promedio del OCR (0-1)")
    fecha_hora: datetime = Field(..., description="Fecha y hora del evento")
    camera_id: Optional[int] = Field(None, description="ID de la cámara que capturó")


class ErrorResponseSchema(BaseModel):
    """Respuesta estándar de error."""
    detail: str