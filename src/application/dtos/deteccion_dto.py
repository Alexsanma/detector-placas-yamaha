from dataclasses import dataclass
from datetime import datetime
from typing import Optional

from src.domain.value_objects.tipo_evento import TipoEvento
from src.domain.value_objects.tipo_vehiculo import TipoVehiculo


@dataclass
class ProcesarDeteccionInput:
    """Datos que necesita el caso de uso ProcesarDeteccion"""
    imagen_bytes: bytes
    camera_id: Optional[int] = None


@dataclass
class ProcesarDeteccionOutput:
    """Resultado y Datos que se envian del procesamiento completado de una detección"""
    placa: str
    tipo_evento: TipoEvento
    tipo_vehiculo: TipoVehiculo
    confianza_deteccion: float
    confianza_ocr: float
    fecha_hora: datetime
    evento_id: Optional[int] = None
    camera_id: Optional[int] = None