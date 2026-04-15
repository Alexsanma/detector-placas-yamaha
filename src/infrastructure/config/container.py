from src.application.ports.input.consultar_eventos_port import ConsultarEventosPort
from src.application.ports.input.procesar_deteccion_port import ProcesarDeteccionPort
from src.application.ports.input.registrar_vehiculo_port import RegistrarVehiculoPort
from src.application.ports.output.detector_placa_port import DetectorPlacaPort
from src.application.ports.output.evento_repository_port import EventoRepositoryPort
from src.application.ports.output.lector_ocr_port import LectorOcrPort
from src.application.ports.output.vehiculo_repository_port import VehiculoRepositoryPort
from src.application.use_cases.consultar_eventos_use_case import ConsultarEventosUseCase
from src.application.use_cases.procesar_deteccion_use_case import ProcesarDeteccionUseCase
from src.application.use_cases.registrar_vehiculo_use_case import RegistrarVehiculoUseCase
from src.infrastructure.adapters.output.persistence.in_memory.evento_in_memory_repository import (
    EventoInMemoryRepository,
)
from src.infrastructure.adapters.output.persistence.in_memory.vehiculo_in_memory_repository import (
    VehiculoInMemoryRepository,
)
from src.infrastructure.adapters.output.persistence.sqlite.connection import (
    crear_engine,
    crear_session_factory,
    inicializar_bd,
)
from src.infrastructure.adapters.output.persistence.sqlite.evento_sqlite_repository import (
    EventoSqliteRepository,
)
from src.infrastructure.adapters.output.persistence.sqlite.vehiculo_sqlite_repository import (
    VehiculoSqliteRepository,
)
from src.infrastructure.adapters.output.vision.easyocr_adapter import EasyOcrAdapter
from src.infrastructure.adapters.output.vision.yolo_detector_adapter import YoloDetectorAdapter
from src.infrastructure.config.settings import Settings, cargar_settings


class Container:
    """
    Composition root: ensambla todas las dependencias de la aplicación.

    Cambiar entre SQLite e in-memory se hace desde el .env (USAR_BASE_DATOS=true/false)
    o sobrescribiendo settings programáticamente.
    """

    def __init__(self, settings: Settings | None = None):
        self._settings = settings or cargar_settings()

        # Inicializar sesión de BD solo si se va a usar SQLite
        if self._settings.usar_base_datos:
            self._engine = crear_engine(self._settings.database_url)
            inicializar_bd(self._engine)
            self._session_factory = crear_session_factory(self._engine)
        else:
            self._engine = None
            self._session_factory = None

        # Construir adaptadores (singletons del ciclo de vida del container)
        self._detector = self._construir_detector()
        self._lector_ocr = self._construir_lector_ocr()
        self._vehiculo_repo = self._construir_vehiculo_repo()
        self._evento_repo = self._construir_evento_repo()

    # ─── Adaptadores de salida ───

    def _construir_detector(self) -> DetectorPlacaPort:
        return YoloDetectorAdapter(
            modelo_path=self._settings.modelo_yolo_path,
            umbral_confianza=self._settings.umbral_confianza_deteccion,
            recorte_superior_pct=self._settings.recorte_superior_pct,
            factor_escala=self._settings.factor_escala_ocr,
        )

    def _construir_lector_ocr(self) -> LectorOcrPort:
        return EasyOcrAdapter(
            idiomas=self._settings.idiomas_ocr,
            usar_gpu=self._settings.usar_gpu,
            umbral_confianza_lectura=self._settings.umbral_confianza_ocr,
        )

    def _construir_vehiculo_repo(self) -> VehiculoRepositoryPort:
        if self._settings.usar_base_datos:
            return VehiculoSqliteRepository(self._session_factory())
        return VehiculoInMemoryRepository()

    def _construir_evento_repo(self) -> EventoRepositoryPort:
        if self._settings.usar_base_datos:
            return EventoSqliteRepository(self._session_factory())
        return EventoInMemoryRepository()

    # ─── Casos de uso (implementan puertos de entrada) ───

    def procesar_deteccion_use_case(self) -> ProcesarDeteccionPort:
        return ProcesarDeteccionUseCase(
            detector=self._detector,
            lector_ocr=self._lector_ocr,
            vehiculo_repo=self._vehiculo_repo,
            evento_repo=self._evento_repo,
            umbral_confianza=self._settings.umbral_confianza_deteccion,
            camara_por_defecto=self._settings.camara_por_defecto,
        )

    def registrar_vehiculo_use_case(self) -> RegistrarVehiculoPort:
        return RegistrarVehiculoUseCase(vehiculo_repo=self._vehiculo_repo)

    def consultar_eventos_use_case(self) -> ConsultarEventosPort:
        return ConsultarEventosUseCase(evento_repo=self._evento_repo)