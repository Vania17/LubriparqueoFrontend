from enum import Enum
from typing import TypeVar


EnumType = TypeVar("EnumType", bound=Enum)


def enum_values(enum_class: type[EnumType]) -> list[str]:
    return [str(item.value) for item in enum_class]


class PlanPago(str, Enum):
    ANTICIPADO = "A"
    VENCIDO = "V"


class TipoCuentaCobro(str, Enum):
    INQUILINO = "inquilino"
    PARQUEO_MENSUAL = "parqueo_mensual"


class EstadoPago(str, Enum):
    COMPLETO = "completo"
    PARCIAL = "parcial"
    PENDIENTE = "pendiente"
    MOROSO = "moroso"


class TipoVehiculo(str, Enum):
    CARRO = "carro"
    BUS = "bus"
    CAMION = "camion"
    OTRO = "otro"


class TipoTarifa(str, Enum):
    POR_HORA = "por_hora"
    DIARIA = "diaria"
    ACORDADA = "acordada"
