from typing import Optional

from src.application.ports.output.vehiculo_repository_port import VehiculoRepositoryPort
from src.domain.entities.vehiculo import Vehiculo


class VehiculoInMemoryRepository(VehiculoRepositoryPort):
    """
    Implementación en memoria del repositorio de vehículos (Purto de salida).
    Los datos se pierden al reiniciar el proceso.
    """

    def __init__(self):
        self._vehiculos: dict[int, Vehiculo] = {}
        self._siguiente_id: int = 1

    def guardar(self, vehiculo: Vehiculo) -> Vehiculo:
        if vehiculo.id is None:
            vehiculo.id = self._siguiente_id
            self._siguiente_id += 1
        self._vehiculos[vehiculo.id] = vehiculo
        return vehiculo

    def buscar_por_placa(self, placa: str) -> Optional[Vehiculo]:
        for vehiculo in self._vehiculos.values():
            if vehiculo.placa == placa:
                return vehiculo
        return None

    def listar_todos(self) -> list[Vehiculo]:
        return list(self._vehiculos.values())