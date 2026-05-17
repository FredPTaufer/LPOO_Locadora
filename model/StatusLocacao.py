from enum import Enum

class StatusLocacao(Enum):
    RESERVADO = "reservado"
    LOCADO    = "locado"
    DEVOLVIDO = "devolvido"
    CANCELADO = "cancelado"