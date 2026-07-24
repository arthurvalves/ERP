from dataclasses import dataclass
from typing import Optional

@dataclass
class PurchaseItem:
    id: Optional[int]
    purchase_id: Optional[int]
    product_id: Optional[int]
    descricao_xml: Optional[str]
    quantidade: float
    valor_unitario: float
    ncm: Optional[str]
