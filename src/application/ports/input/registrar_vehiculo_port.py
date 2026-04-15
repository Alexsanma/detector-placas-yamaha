from abc import ABC, abstractmethod

from src.application.dtos.vehiculo_dto import RegistrarVehiculoInput, VehiculoOutput


class RegistrarVehiculoPort(ABC):
    """
    Contrato que ofrece la aplicación para registrar
    un nuevo vehículo en el sistema.
    """

    @abstractmethod
    def ejecutar(self, input_dto: RegistrarVehiculoInput) -> VehiculoOutput:
        """
        Registra un nuevo vehículo en el sistema.

        Args -> input_dto: Datos del vehículo a registrar (placa, tipo, nombre opcional).
        Devuelve: Vehículo registrado con su ID asignado.
        Raises:
            ValueError: Si la placa ya está registrada en el sistema.
        """
        pass