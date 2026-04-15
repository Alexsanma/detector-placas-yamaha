from typing import Optional

from src.domain.entities.evento import Evento
from src.domain.entities.vehiculo import Vehiculo
from src.domain.exceptions import ConfianzaBajaError
from src.domain.value_objects.tipo_evento import TipoEvento
from src.domain.value_objects.tipo_vehiculo import TipoVehiculo


def validar_confianza(confianza: float, umbral: float) -> bool:
    """Se valida que la confianza no sea menor al umbral mínimo"""
    if confianza < umbral:
        raise ConfianzaBajaError(
            f"Confianza {confianza:.2f} menor al umbral mínimo {umbral:.2f}"
        )
    return True


def determinar_tipo_vehiculo(placa: str, vehiculos: list[Vehiculo]) -> TipoVehiculo:
    """
    Determina si la placa esta en la lista de registrados, si no lo esta, es tipo visitante
    """
    for vehiculo in vehiculos:
        if placa == vehiculo.placa:
            return vehiculo.tipo
    return TipoVehiculo.VISITANTE


def determinar_tipo_evento(ultimo_evento: Optional[Evento]) -> TipoEvento:
    """
    Determina si el evento actual es ingreso o salida, solo teniendo en cuenta el Último evento
    - si no hay ningun evento, es ingreso 
    - si él ultimo evento fue ingreso entonces el actual es salida
    - y si el evento no es ingreso, es por que el ultimo fue salida, por ende el actual es ingreso
    """
    if ultimo_evento is None:
        return TipoEvento.INGRESO
    if ultimo_evento.tipo_evento == TipoEvento.INGRESO:
        return TipoEvento.SALIDA
    return TipoEvento.INGRESO