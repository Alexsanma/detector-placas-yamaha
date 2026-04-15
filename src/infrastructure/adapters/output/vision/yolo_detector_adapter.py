import cv2
import numpy as np
from ultralytics import YOLO

from src.application.ports.output.detector_placa_port import (
    DeteccionPlaca,
    DetectorPlacaPort,
)


class YoloDetectorAdapter(DetectorPlacaPort):
    """
    Adaptador de detección de placas usando YOLO (Ultralytics).

    Responsabilidades:
    1. Detectar placas en la imagen.
    2. Recortar la zona superior (70%) donde viven los caracteres.
    3. Escalar el recorte 3x para mejor lectura posterior del OCR.
    4. Devolver los recortes listos para OCR junto con coordenadas y confianza.
    """

    def __init__(
        self,
        modelo_path: str,
        umbral_confianza: float = 0.5,
        recorte_superior_pct: float = 0.70,
        factor_escala: float = 3.0,
    ):
        self._model = YOLO(modelo_path)
        self._umbral_confianza = umbral_confianza
        self._recorte_superior_pct = recorte_superior_pct
        self._factor_escala = factor_escala

    def detectar(self, imagen_bytes: bytes) -> list[DeteccionPlaca]:
        # Decodificar los bytes a imagen OpenCV (BGR)
        nparr = np.frombuffer(imagen_bytes, np.uint8)
        imagen = cv2.imdecode(nparr, cv2.IMREAD_COLOR)
        if imagen is None:
            return []

        # Correr detección con YOLO
        resultados = self._model(imagen, verbose=False)

        detecciones: list[DeteccionPlaca] = []
        for box in resultados[0].boxes:
            confianza = float(box.conf[0])
            if confianza < self._umbral_confianza:
                continue

            x1, y1, x2, y2 = map(int, box.xyxy[0])

            # Recortar el 70% superior (zona de caracteres de la placa)
            altura_recorte = int((y2 - y1) * self._recorte_superior_pct)
            recorte = imagen[y1:y1 + altura_recorte, x1:x2]
            if recorte.size == 0:
                continue

            # Escalar 3x para mejorar lectura del OCR
            recorte_escalado = cv2.resize(
                recorte,
                None,
                fx=self._factor_escala,
                fy=self._factor_escala,
                interpolation=cv2.INTER_CUBIC,
            )

            # Convertir el recorte procesado a bytes (formato PNG)
            exito, buffer = cv2.imencode(".png", recorte_escalado)
            if not exito:
                continue
            recorte_bytes = buffer.tobytes()

            detecciones.append(
                DeteccionPlaca(
                    x1=x1,
                    y1=y1,
                    x2=x2,
                    y2=y2,
                    confianza=confianza,
                    recorte_bytes=recorte_bytes,
                )
            )

        return detecciones