from abc import ABC, abstractmethod
from dataclasses import dataclass


@dataclass
class DeteccionPlaca:
    """Resultado base despues de la detección de una placa en la imagen"""
    x1: int
    y1: int
    x2: int
    y2: int
    confianza: float
    recorte_bytes: bytes


class DetectorPlacaPort(ABC):
    """Contrato para detectar placas en una imagen."""

    @abstractmethod
    def detectar(self, imagen_bytes: bytes) -> list[DeteccionPlaca]:
        """
        Detecta placas en la imagen suministrada .
        Args: imagen_bytes: Imagen en bytes (cualquier formato soportado por el adaptador).
        Devuelve:Lista de detecciones encontradas(Puede haber mas de una placa). Lista vacía si no se detectó nada.
        """
        pass