from dataclasses import dataclass
from typing import Optional

@dataclass
class Customer:
    id: Optional[int]
    nome_razao_social: str
    cpf_cnpj: Optional[str] = None
    telefone: Optional[str] = None
    email: Optional[str] = None
    endereco: Optional[str] = None
