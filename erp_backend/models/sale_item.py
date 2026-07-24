from dataclasses import dataclass
from typing import Optional

@dataclass
class SaleItem:
    id: Optional[int]
    sale_id: Optional[int]
    product_id: Optional[int]
    quantidade: float
    preco_unitario: float
    desconto_item: float = 0.0
