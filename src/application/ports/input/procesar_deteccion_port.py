from abc import ABC, abstractmethod

from src.application.dtos.deteccion_dto import (
    ProcesarDeteccionInput,
    ProcesarDeteccionOutput,
)


class ProcesarDeteccionPort(ABC):
    """
    Contrato que ofrece la aplicación para procesar una detección de placa vehicular. 
    (representa una acción de negocio - detección + OCR + Clasificación + Persistencia) 

    """

    @abstractmethod
    def ejecutar(self, input_dto: ProcesarDeteccionInput) -> ProcesarDeteccionOutput:
        """
        Procesa una imagen completa:
        - detecta la placa, lee los caracteres, clasifica el evento (ingreso/salida, registrado/visitante) y persiste el resultado.

        Args -> input_dto: Imagen en bytes y opcionalmente el ID de la cámara.
        Devuelve: Resultado del procesamiento con toda la información del evento generado.
        Raises (Excepciones de negocio):
            PlacaNoDetectadaError: Si YOLO no detecta ninguna placa.
            ConfianzaBajaError: Si la confianza está por debajo del umbral configurado.
        """
        pass