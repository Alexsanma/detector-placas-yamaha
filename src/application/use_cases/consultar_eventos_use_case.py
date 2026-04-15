from src.application.dtos.evento_dto import EventoOutput
from src.application.ports.input.consultar_eventos_port import ConsultarEventosPort
from src.application.ports.output.evento_repository_port import EventoRepositoryPort
from src.domain.entities.evento import Evento


class ConsultarEventosUseCase(ConsultarEventosPort):
    """Devuelve el historial completo de eventos registrados."""

    def __init__(self, evento_repo: EventoRepositoryPort):
        self._evento_repo = evento_repo

    def ejecutar(self) -> list[EventoOutput]:
        eventos = self._evento_repo.listar_todos()
        return [self._a_output(e) for e in eventos]

    @staticmethod
    def _a_output(evento: Evento) -> EventoOutput:
        return EventoOutput(
            id=evento.id,
            placa=evento.placa,
            tipo_evento=evento.tipo_evento,
            confianza=evento.confianza,
            fecha_hora=evento.fecha_hora,
            camera_id=evento.camera_id,
        )