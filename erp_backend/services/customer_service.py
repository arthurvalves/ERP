from ..models.customer import Customer
from ..utils.db import fetchone, fetchall
from typing import List, Optional


def get_customer_by_id(customer_id: int, conn=None) -> Optional[Customer]:
    """Busca um cliente pelo seu ID."""
    if not customer_id: return None
    row = fetchone("SELECT * FROM customers WHERE id = ?", (customer_id,), conn=conn)
    return Customer.from_row(row) if row else None


def search_customers(search_term: str) -> List[Customer]:
    """Busca clientes por nome/razão social ou CPF/CNPJ."""
    query = "SELECT * FROM customers WHERE nome_razao_social LIKE ? OR cpf_cnpj LIKE ? ORDER BY nome_razao_social LIMIT 50"
    params = (f"%{search_term}%", f"%{search_term}%")
    rows = fetchall(query, params)
    return [Customer.from_row(row) for row in rows]