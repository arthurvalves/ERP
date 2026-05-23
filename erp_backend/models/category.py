from dataclasses import dataclass
from typing import Optional

@dataclass
class Category:
    id: Optional[int]
    nome: str
    margem_padrao: float = 0.0
