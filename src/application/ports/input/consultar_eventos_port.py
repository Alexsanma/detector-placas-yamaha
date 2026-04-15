from abc import ABC, abstractmethod

from src.application.dtos.evento_dto import EventoOutput


class ConsultarEventosPort(ABC):
    """
    Contrato que ofrece la aplicación para consultar el historial 
    de eventos de acceso registrado
    """

    @abstractmethod
    def ejecutar(self) -> list[EventoOutput]:
        """
        Retorna todos los eventos registrados en el sistema,
        ordenados por fecha descendente (más recientes primero).

        Devuelve:Lista de eventos en formato DTO.
        """
        pass