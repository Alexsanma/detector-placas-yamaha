from dataclasses import dataclass, field
from datetime import datetime
from typing import Optional

from src.domain.value_objects.tipo_vehiculo import TipoVehiculo


@dataclass
class Vehiculo:
    placa: str
    tipo: TipoVehiculo
    id: Optional[int] = None
    nombre: Optional[str] = None
    fecha_registro: datetime = field(default_factory=datetime.now)