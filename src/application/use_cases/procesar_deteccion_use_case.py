from src.application.dtos.deteccion_dto import (
    ProcesarDeteccionInput,
    ProcesarDeteccionOutput,
)
from src.application.ports.input.procesar_deteccion_port import ProcesarDeteccionPort
from src.application.ports.output.detector_placa_port import DetectorPlacaPort
from src.application.ports.output.evento_repository_port import EventoRepositoryPort
from src.application.ports.output.lector_ocr_port import LectorOcrPort
from src.application.ports.output.vehiculo_repository_port import VehiculoRepositoryPort
from src.domain.entities.evento import Evento
from src.domain.exceptions import PlacaNoDetectadaError
from src.domain.services.access_rules import (
    determinar_tipo_evento,
    determinar_tipo_vehiculo,
    validar_confianza,
)


class ProcesarDeteccionUseCase(ProcesarDeteccionPort):
    """
    Orquesta el procesamiento completo de una detección de placa:
    1. Detecta la placa con el detector (YOLO).
    2. Valida la confianza de detección.
    3. Recorta la placa y la pasa al OCR.
    4. Clasifica el evento (ingreso/salida) y el tipo de vehículo (registrado/visitante).
    5. Guarda (Persiste) el evento generado.
    """

    def __init__(
        self,
        detector: DetectorPlacaPort,
        lector_ocr: LectorOcrPort,
        vehiculo_repo: VehiculoRepositoryPort,
        evento_repo: EventoRepositoryPort,
        umbral_confianza: float = 0.5,
        camara_por_defecto: int = 1,
    ):
        self._detector = detector
        self._lector_ocr = lector_ocr
        self._vehiculo_repo = vehiculo_repo
        self._evento_repo = evento_repo
        self._umbral_confianza = umbral_confianza
        self._camara_por_defecto = camara_por_defecto

    def ejecutar(self, input_dto: ProcesarDeteccionInput) -> ProcesarDeteccionOutput:
        # 1. Detectar placas en la imagen
        detecciones = self._detector.detectar(input_dto.imagen_bytes)
        if not detecciones:
            raise PlacaNoDetectadaError("No se detectó ninguna placa en la imagen.")

        # Tomar la detección con mayor confianza
        mejor_deteccion = max(detecciones, key=lambda d: d.confianza)

        # 2. Validar que supere el umbral de confianza (lógica de dominio)
        validar_confianza(mejor_deteccion.confianza, self._umbral_confianza)

        # 3. Recortar la placa y leer con OCR
        lectura = self._lector_ocr.leer(mejor_deteccion.recorte_bytes)
        # Texto leido en la placa 
        placa_leida = lectura.texto

        # 4. Clasificar tipo de vehículo y tipo de evento (lógica de dominio)
        vehiculos_registrados = self._vehiculo_repo.listar_todos()
        # Buscamos si el vehiculo ya esta registrado o es visitante
        tipo_vehiculo = determinar_tipo_vehiculo(placa_leida, vehiculos_registrados)
        # Buscamos el ultimo evento del vehiculo
        ultimo_evento = self._evento_repo.ultimo_evento_por_placa(placa_leida)
        # Lógica del dominio 
        tipo_evento = determinar_tipo_evento(ultimo_evento)

        # 5. Crear la entidad de dominio y persistirla
        evento = Evento(
            placa=placa_leida,
            confianza=mejor_deteccion.confianza,
            tipo_evento=tipo_evento,
            camera_id=input_dto.camera_id if input_dto.camera_id is not None else self._camara_por_defecto,
        )
        evento_guardado = self._evento_repo.guardar(evento)

        # 6. Construir y devolver el DTO de salida
        return ProcesarDeteccionOutput(
            evento_id=evento_guardado.id, #-> El repositorio devuelve la entidad con el ID asignado 
            placa=evento_guardado.placa,
            tipo_evento=evento_guardado.tipo_evento,
            tipo_vehiculo=tipo_vehiculo,
            confianza_deteccion=mejor_deteccion.confianza,
            confianza_ocr=lectura.confianza,
            fecha_hora=evento_guardado.fecha_hora,
            camera_id=evento_guardado.camera_id,
        )