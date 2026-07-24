from dataclasses import dataclass
from typing import Optional

@dataclass
class Supplier:
    id: Optional[int]
    razao_social: str
    cnpj: Optional[str] = None
    ie: Optional[str] = None
    endereco: Optional[str] = None
    cidade: Optional[str] = None
    uf: Optional[str] = None
