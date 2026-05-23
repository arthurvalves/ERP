from dataclasses import dataclass
from typing import List, Optional
from datetime import datetime

@dataclass
class QuoteItem:
    product_id: int
    quantidade: float
    preco_unitario: float
    desconto_item: float = 0.0

@dataclass
class Quote:
    id: Optional[int]
    customer_id: Optional[int]
    placa: str
    total: float
    status: str
    items: List[QuoteItem]
    data_criacao: Optional[datetime] = None

@dataclass
class ServiceOrderItem:
    product_id: int
    tipo: str # 'peca' ou 'servico'
    quantidade: float
    preco_unitario: float
    desconto_item: float = 0.0

@dataclass
class ServiceOrder:
    id: Optional[int]
    customer_id: Optional[int]
    veiculo: str
    placa: str
    descricao_problema: str
    status: str
    total_pecas: float
    total_servicos: float
    total_geral: float
    items: List[ServiceOrderItem]
    data_abertura: Optional[datetime] = None
    data_fechamento: Optional[datetime] = None