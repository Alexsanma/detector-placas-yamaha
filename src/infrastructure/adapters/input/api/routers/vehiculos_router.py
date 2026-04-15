from fastapi import APIRouter, Depends, HTTPException, status

from src.application.dtos.vehiculo_dto import RegistrarVehiculoInput
from src.domain.value_objects.tipo_vehiculo import TipoVehiculo
from src.infrastructure.adapters.input.api.schemas.vehiculo_schema import (
    VehiculoRequestSchema,
    VehiculoResponseSchema,
)
from src.infrastructure.config.container import Container

router = APIRouter(prefix="/vehiculos", tags=["Vehículos"])


def get_container() -> Container:
    raise NotImplementedError("Container no inicializado")


@router.post(
    "",
    response_model=VehiculoResponseSchema,
    status_code=status.HTTP_201_CREATED,
    summary="Registrar un vehículo",
    description="Registra un nuevo vehículo autorizado o visitante en el sistema.",
)
def registrar_vehiculo(
    payload: VehiculoRequestSchema,
    container: Container = Depends(get_container),
):
    # Validar que el tipo sea uno de los enums permitidos
    try:
        tipo_enum = TipoVehiculo(payload.tipo.lower())
    except ValueError:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=f"Tipo inválido. Valores permitidos: {[t.value for t in TipoVehiculo]}",
        )

    use_case = container.registrar_vehiculo_use_case()

    try:
        resultado = use_case.ejecutar(
            RegistrarVehiculoInput(
                placa=payload.placa.upper(),
                tipo=tipo_enum,
                nombre=payload.nombre,
            )
        )
    except ValueError as e:
        # La placa ya existe (regla de negocio del caso de uso)
        raise HTTPException(status_code=status.HTTP_409_CONFLICT, detail=str(e))

    return VehiculoResponseSchema(
        id=resultado.id,
        placa=resultado.placa,
        tipo=resultado.tipo.value,
        nombre=resultado.nombre,
        fecha_registro=resultado.fecha_registro,
    )