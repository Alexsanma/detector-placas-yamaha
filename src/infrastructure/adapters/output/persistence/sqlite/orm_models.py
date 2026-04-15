from datetime import datetime

from sqlalchemy import DateTime, Float, ForeignKey, Integer, String
from sqlalchemy.orm import Mapped, mapped_column

from src.infrastructure.adapters.output.persistence.sqlite.connection import Base


class VehiculoORM(Base):
    """Modelo ORM de SQLAlchemy para la tabla de vehículos."""
    __tablename__ = "vehiculos"

    id: Mapped[int] = mapped_column(Integer, primary_key=True, autoincrement=True)
    placa: Mapped[str] = mapped_column(String(10), unique=True, nullable=False, index=True)
    tipo: Mapped[str] = mapped_column(String(20), nullable=False)  # "registrado" | "visitante"
    nombre: Mapped[str | None] = mapped_column(String(100), nullable=True)
    fecha_registro: Mapped[datetime] = mapped_column(DateTime, default=datetime.now)


class EventoORM(Base):
    """Modelo ORM de SQLAlchemy para la tabla de eventos de acceso."""
    __tablename__ = "eventos"

    id: Mapped[int] = mapped_column(Integer, primary_key=True, autoincrement=True)
    placa: Mapped[str] = mapped_column(String(10), nullable=False, index=True)
    tipo_evento: Mapped[str] = mapped_column(String(20), nullable=False)  # "ingreso" | "salida"
    confianza: Mapped[float] = mapped_column(Float, nullable=False)
    fecha_hora: Mapped[datetime] = mapped_column(DateTime, default=datetime.now, index=True)
    camera_id: Mapped[int | None] = mapped_column(Integer, nullable=True)