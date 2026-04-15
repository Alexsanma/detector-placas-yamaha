from abc import ABC, abstractmethod
from dataclasses import dataclass


@dataclass
class LecturaOCR:
    """Resultado base despues de la lectura OCR del recorte de una placa"""
    texto: str
    confianza: float


class LectorOcrPort(ABC):
    """Contrato para leer caracteres de un recorte de placa."""

    @abstractmethod
    def leer(self, recorte_bytes: bytes) -> LecturaOCR:
        """
        Lee los caracteres alfanuméricos de un recorte de placa.
        Args: recorte_bytes: Imagen recortada de la placa en bytes.
        Devuelve: LecturaOCR (tecto reconocido), confianza Promedio y 
        Si no se pudo leer nada, devuelve texto vacío con confianza 0.0.
        """
        pass