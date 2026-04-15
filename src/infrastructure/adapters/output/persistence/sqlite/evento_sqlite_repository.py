from typing import Optional

from sqlalchemy.orm import Session

from src.application.ports.output.evento_repository_port import EventoRepositoryPort
from src.domain.entities.evento import Evento
from src.domain.value_objects.tipo_evento import TipoEvento
from src.infrastructure.adapters.output.persistence.sqlite.orm_models import EventoORM


class EventoSqliteRepository(EventoRepositoryPort):
    """Implementación SQLite del repositorio de eventos usando SQLAlchemy."""

    def __init__(self, session: Session):
        self._session = session

    def guardar(self, evento: Evento) -> Evento:
        orm = self._a_orm(evento)
        self._session.add(orm)
        self._session.commit()
        self._session.refresh(orm)
        return self._a_entidad(orm)

    def ultimo_evento_por_placa(self, placa: str) -> Optional[Evento]:
        orm = (
            self._session.query(EventoORM)
            .filter(EventoORM.placa == placa)
            .order_by(EventoORM.fecha_hora.desc())
            .first()
        )
        return self._a_entidad(orm) if orm else None

    def listar_todos(self) -> list[Evento]:
        registros = (
            self._session.query(EventoORM)
            .order_by(EventoORM.fecha_hora.desc())
            .all()
        )
        return [self._a_entidad(r) for r in registros]

    # ─── Mappers entre entidad de dominio y modelo ORM ───

    @staticmethod
    def _a_orm(evento: Evento) -> EventoORM:
        return EventoORM(
            id=evento.id,
            placa=evento.placa,
            tipo_evento=evento.tipo_evento.value,
            confianza=evento.confianza,
            fecha_hora=evento.fecha_hora,
            camera_id=evento.camera_id,
        )

    @staticmethod
    def _a_entidad(orm: EventoORM) -> Evento:
        return Evento(
            id=orm.id,
            placa=orm.placa,
            tipo_evento=TipoEvento(orm.tipo_evento),
            confianza=orm.confianza,
            fecha_hora=orm.fecha_hora,
            camera_id=orm.camera_id,
        )