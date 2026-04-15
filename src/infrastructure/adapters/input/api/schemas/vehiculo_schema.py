from datetime import datetime
from typing import Optional

from pydantic import BaseModel, Field


class VehiculoRequestSchema(BaseModel):
    """Datos de entrada para registrar un vehículo."""

    placa: str = Field(..., min_length=5, max_length=10, description="Placa del vehículo")
    tipo: str = Field(..., description="Tipo de vehículo: 'registrado' o 'visitante'")
    nombre: Optional[str] = Field(None, max_length=100, description="Nombre del propietario")


class VehiculoResponseSchema(BaseModel):
    """Representación de un vehículo hacia el cliente."""

    id: int
    placa: str
    tipo: str
    nombre: Optional[str]
    fecha_registro: datetime