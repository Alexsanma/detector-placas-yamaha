from typing import Optional

from sqlalchemy.orm import Session

from src.application.ports.output.vehiculo_repository_port import VehiculoRepositoryPort
from src.domain.entities.vehiculo import Vehiculo
from src.domain.value_objects.tipo_vehiculo import TipoVehiculo
from src.infrastructure.adapters.output.persistence.sqlite.orm_models import VehiculoORM


class VehiculoSqliteRepository(VehiculoRepositoryPort):
    """Implementación SQLite del repositorio de vehículos usando SQLAlchemy."""

    def __init__(self, session: Session):
        self._session = session

    def guardar(self, vehiculo: Vehiculo) -> Vehiculo:
        orm = self._a_orm(vehiculo)
        self._session.add(orm)
        self._session.commit()
        self._session.refresh(orm)
        return self._a_entidad(orm)

    def buscar_por_placa(self, placa: str) -> Optional[Vehiculo]:
        orm = self._session.query(VehiculoORM).filter(VehiculoORM.placa == placa).first()
        return self._a_entidad(orm) if orm else None

    def listar_todos(self) -> list[Vehiculo]:
        registros = self._session.query(VehiculoORM).all()
        return [self._a_entidad(r) for r in registros]

    # ─── Mappers entre entidad de dominio y modelo ORM ───

    @staticmethod
    def _a_orm(vehiculo: Vehiculo) -> VehiculoORM:
        return VehiculoORM(
            id=vehiculo.id,
            placa=vehiculo.placa,
            tipo=vehiculo.tipo.value,
            nombre=vehiculo.nombre,
            fecha_registro=vehiculo.fecha_registro,
        )

    @staticmethod
    def _a_entidad(orm: VehiculoORM) -> Vehiculo:
        return Vehiculo(
            id=orm.id,
            placa=orm.placa,
            tipo=TipoVehiculo(orm.tipo),
            nombre=orm.nombre,
            fecha_registro=orm.fecha_registro,
        )