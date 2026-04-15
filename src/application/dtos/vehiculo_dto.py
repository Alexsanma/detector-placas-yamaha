from dataclasses import dataclass
from datetime import datetime
from typing import Optional

from src.domain.value_objects.tipo_vehiculo import TipoVehiculo


@dataclass
class RegistrarVehiculoInput:
    """Datos que necesita para registrar un vehículo"""
    placa: str
    tipo: TipoVehiculo
    nombre: Optional[str] = None


@dataclass
class VehiculoOutput:
    """Datos que se necesitan mostrar en una consulta de vehiculos"""
    id: int
    placa: str
    tipo: TipoVehiculo
    nombre: Optional[str]
    fecha_registro: datetime