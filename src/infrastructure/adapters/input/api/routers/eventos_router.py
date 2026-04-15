from fastapi import APIRouter, Depends

from src.infrastructure.adapters.input.api.schemas.evento_schema import (
    EventoResponseSchema,
)
from src.infrastructure.config.container import Container

router = APIRouter(prefix="/eventos", tags=["Eventos"])


def get_container() -> Container:
    raise NotImplementedError("Container no inicializado")


@router.get(
    "",
    response_model=list[EventoResponseSchema],
    summary="Listar eventos de acceso",
    description="Devuelve el historial completo de eventos ordenados por fecha descendente.",
)
def listar_eventos(container: Container = Depends(get_container)):
    use_case = container.consultar_eventos_use_case()
    eventos = use_case.ejecutar()

    return [
        EventoResponseSchema(
            id=e.id,
            placa=e.placa,
            tipo_evento=e.tipo_evento.value,
            confianza=e.confianza,
            fecha_hora=e.fecha_hora,
            camera_id=e.camera_id,
        )
        for e in eventos
    ]