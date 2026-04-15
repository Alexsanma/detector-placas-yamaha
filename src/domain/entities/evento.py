from dataclasses import dataclass, field
from datetime import datetime
from typing import Optional

from src.domain.value_objects.tipo_evento import TipoEvento


@dataclass
class Evento:
    placa: str
    confianza: float
    tipo_evento: TipoEvento
    id: Optional[int] = None
    fecha_hora: datetime = field(default_factory=datetime.now)
    camera_id: Optional[int] = None