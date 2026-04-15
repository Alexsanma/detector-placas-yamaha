from src.application.dtos.vehiculo_dto import RegistrarVehiculoInput, VehiculoOutput
from src.application.ports.input.registrar_vehiculo_port import RegistrarVehiculoPort
from src.application.ports.output.vehiculo_repository_port import VehiculoRepositoryPort
from src.domain.entities.vehiculo import Vehiculo


class RegistrarVehiculoUseCase(RegistrarVehiculoPort):
    """Registra un nuevo vehículo en el sistema, validando que la placa no exista previamente."""

    def __init__(self, vehiculo_repo: VehiculoRepositoryPort):
        self._vehiculo_repo = vehiculo_repo

    def ejecutar(self, input_dto: RegistrarVehiculoInput) -> VehiculoOutput:
        # Validar que la placa no esté ya registrada
        existente = self._vehiculo_repo.buscar_por_placa(input_dto.placa)
        if existente is not None:
            raise ValueError(f"La placa {input_dto.placa} ya está registrada.")

        # Crear y persistir el vehículo
        vehiculo = Vehiculo(
            placa=input_dto.placa,
            tipo=input_dto.tipo,
            nombre=input_dto.nombre,
        )
        vehiculo_guardado = self._vehiculo_repo.guardar(vehiculo)

        # Mapear a DTO de salida
        return VehiculoOutput(
            id=vehiculo_guardado.id,
            placa=vehiculo_guardado.placa,
            tipo=vehiculo_guardado.tipo,
            nombre=vehiculo_guardado.nombre,
            fecha_registro=vehiculo_guardado.fecha_registro,
        )