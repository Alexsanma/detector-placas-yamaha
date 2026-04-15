from typing import Optional

from src.application.ports.output.evento_repository_port import EventoRepositoryPort
from src.domain.entities.evento import Evento


class EventoInMemoryRepository(EventoRepositoryPort):
    """
    Implementación en memoria del repositorio de eventos (Puerto de salida).
    Los datos se pierden al reiniciar el proceso.
    """

    def __init__(self):
        self._eventos: dict[int, Evento] = {}
        self._siguiente_id: int = 1

    def guardar(self, evento: Evento) -> Evento:
        if evento.id is None:
            evento.id = self._siguiente_id
            self._siguiente_id += 1
        self._eventos[evento.id] = evento
        return evento

    def ultimo_evento_por_placa(self, placa: str) -> Optional[Evento]:
        eventos_placa = [e for e in self._eventos.values() if e.placa == placa]
        if not eventos_placa:
            return None
        return max(eventos_placa, key=lambda e: e.fecha_hora)

    def listar_todos(self) -> list[Evento]:
        # Orden descendente por fecha (más recientes primero)
        return sorted(
            self._eventos.values(),
            key=lambda e: e.fecha_hora,
            reverse=True,
        )