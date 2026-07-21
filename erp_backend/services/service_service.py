from ..utils.db import fetchall, execute
from typing import List, Optional

def get_all_services(search_term: str = "") -> List[dict]:
    """Busca todos os serviços, com filtro opcional por nome ou SKU."""
    sql = "SELECT * FROM services"
    params = ()
    if search_term:
        sql += " WHERE name LIKE ? OR sku LIKE ?"
        params = (f"%{search_term}%", f"%{search_term}%")
    sql += " ORDER BY name"
    return fetchall(sql, params)

def create_or_update_service(service_data: dict, service_id: Optional[int] = None):
    """Cria um novo serviço ou atualiza um existente."""
    if service_id:
        sql = "UPDATE services SET name=?, sku=?, description=?, standard_price=?, category=? WHERE id=?"
        params = (
            service_data['name'], service_data['sku'], service_data['description'],
            service_data['standard_price'], service_data['category'], service_id
        )
    else:
        sql = "INSERT INTO services (name, sku, description, standard_price, category) VALUES (?, ?, ?, ?, ?)"
        params = (
            service_data['name'], service_data['sku'], service_data['description'],
            service_data['standard_price'], service_data['category']
        )
    return execute(sql, params)

def delete_service(service_id: int):
    """Exclui um serviço do catálogo."""
    return execute("DELETE FROM services WHERE id = ?", (service_id,))