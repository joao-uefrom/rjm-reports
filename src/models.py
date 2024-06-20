from dataclasses import dataclass
from datetime import datetime
from typing import List


@dataclass
class Item:
    codigo: int
    nome: str
    quantidade: int
    valor_unitario: float
    valor_cobrado: float
    valor_total: float

    def __eq__(self, other):
        if isinstance(other, Item):
            return self.codigo == other.codigo

        return False


@dataclass
class Pedido:
    codigo: int
    cliente: str
    atendente: str
    entregador: str
    tipo_atendimento: str
    data_abertura: datetime
    data_fechamento: datetime
    valor_entrega: float
    valor_total: float
    itens: List[Item]
    tempo_atendimento: int
    eh_fiado: bool

    @property
    def quantidade_itens(self) -> int:
        return sum(item.quantidade for item in self.itens)
