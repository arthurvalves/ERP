from dataclasses import dataclass
from typing import Optional

@dataclass
class StockMovement:
    id: Optional[int]
    product_id: int
    tipo: str
    quantidade: float
    custo_unitario: float
    origem: str
    referencia_id: Optional[int]
    data: Optional[str]
