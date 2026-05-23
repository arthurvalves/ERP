from dataclasses import dataclass
from typing import Optional

@dataclass
class Sale:
    id: Optional[int]
    customer_id: Optional[int]
    total: float
    desconto_total: float = 0.0
    forma_pagamento: Optional[str] = None
    data: Optional[str] = None
