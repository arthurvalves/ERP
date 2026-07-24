from dataclasses import dataclass
from typing import Optional

@dataclass
class Product:
    id: Optional[int]
    sku: str
    nome: str
    nome_normalizado: Optional[str] = None
    codigo_barras: Optional[str] = None
    ncm: Optional[str] = None
    referencia: Optional[str] = None
    fornecedor_id: Optional[int] = None
    categoria_id: Optional[int] = None
    custo: float = 0.0
    margem_padrao: float = 0.0
    preco_venda: float = 0.0
    estoque_atual: float = 0.0

    @classmethod
    def from_row(cls, row):
        data = dict(row)
        allowed = set(cls.__dataclass_fields__.keys())
        filtered = {key: value for key, value in data.items() if key in allowed}
        return cls(**filtered)
