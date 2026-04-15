from abc import ABC, abstractmethod
from typing import Optional

from src.domain.entities.evento import Evento


class EventoRepositoryPort(ABC):
    """Contrato para persistir y consultar eventos de acceso."""

    @abstractmethod
    def guardar(self, evento: Evento) -> Evento:
        """Guarda (Persiste) un evento. Devuelve la entidad con el ID asignado."""
        pass

    @abstractmethod
    def ultimo_evento_por_placa(self, placa: str) -> Optional[Evento]:
        """
        Devuelve el evento más reciente de una placa.
        Se usa para determinar si el próximo evento es ingreso o salida (Intencion del Dominio).
        """
        pass

    @abstractmethod
    def listar_todos(self) -> list[Evento]:
        """Devuelve todos los eventos registrados, ordenados por fecha descendente."""
        pass