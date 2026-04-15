from abc import ABC, abstractmethod
from typing import Optional

from src.domain.entities.vehiculo import Vehiculo


class VehiculoRepositoryPort(ABC):
    """Contrato para persistir y consultar vehículos."""

    @abstractmethod
    def guardar(self, vehiculo: Vehiculo) -> Vehiculo:
        """Guarda(persiste) un vehículo. Devuelve la entidad con el ID asignado."""
        pass

    @abstractmethod
    def buscar_por_placa(self, placa: str) -> Optional[Vehiculo]:
        """Busca un vehículo por su placa. Devuelve None si no existe."""
        pass

    @abstractmethod
    def listar_todos(self) -> list[Vehiculo]:
        """Devuelve todos los vehículos registrados."""
        pass