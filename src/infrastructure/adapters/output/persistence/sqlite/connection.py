from sqlalchemy import create_engine
from sqlalchemy.orm import DeclarativeBase, sessionmaker


class Base(DeclarativeBase):
    """Base declarativa para todos los modelos ORM."""
    pass


def crear_engine(database_url: str = "sqlite:///./detector_placas.db"):
    """Crea el engine de SQLAlchemy para SQLite."""
    return create_engine(
        database_url,
        connect_args={"check_same_thread": False},  # necesario para SQLite en FastAPI ya que SQLite solo deja usar un hilo
        echo=False,  # No motrar SQL en consola
    )


def crear_session_factory(engine): # -> Crea una fabrica de sesiones
    """Crea el factory de sesiones para el engine dado."""
    return sessionmaker(bind=engine, autoflush=False, autocommit=False) # -> conversacion con la BD 


def inicializar_bd(engine):
    """Crea todas las tablas definidas en los modelos ORM si no existen."""
    # Import local para evitar dependencia circular
    from src.infrastructure.adapters.output.persistence.sqlite import orm_models  # noqa
    Base.metadata.create_all(bind=engine) #-> Busca modelos que heredan de Base y los crea como tablas en la BD si no existen