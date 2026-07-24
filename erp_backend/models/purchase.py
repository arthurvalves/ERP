from dataclasses import dataclass
from typing import Optional

@dataclass
class Purchase:
    id: Optional[int]
    chave_acesso: Optional[str]
    supplier_id: Optional[int]
    valor_total: float
    data_emissao: Optional[str] = None
