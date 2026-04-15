from dataclasses import dataclass
from datetime import datetime
from typing import Optional

from src.domain.value_objects.tipo_evento import TipoEvento


@dataclass
class EventoOutput:
    """Datos que se necesitan mostrar en una consulta de eventos"""
    id: int
    placa: str
    tipo_evento: TipoEvento
    confianza: float
    fecha_hora: datetime
    camera_id: Optional[int] = None