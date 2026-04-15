from datetime import datetime
from typing import Optional

from pydantic import BaseModel


class EventoResponseSchema(BaseModel):
    """Representación de un evento hacia el cliente."""

    id: int
    placa: str
    tipo_evento: str
    confianza: float
    fecha_hora: datetime
    camera_id: Optional[int] = None