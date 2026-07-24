from typing import List, Optional
from ..utils.db import fetchall, fetchone, execute, execute_with_conn, transaction
from ..utils.audit import log
from erp_frontend.session import get_current_user_id

def get_all_categories(conn=None) -> List[dict]:
    """Retorna uma lista de todas as categorias de produtos."""
    return fetchall("SELECT * FROM categories ORDER BY nome ASC", conn=conn)

def get_category_by_name(nome: str, conn=None) -> Optional[dict]:
    """Busca uma categoria pelo nome."""
    row = fetchone("SELECT * FROM categories WHERE nome = ?", (nome,), conn=conn)
    return dict(row) if row else None

def create_or_update_category(nome: str, margem_padrao: float = 0.0, category_id: int = None) -> int:
    """
    Cria uma nova categoria ou atualiza uma existente.
    Retorna o ID da categoria.
    """
    if not nome:
        raise ValueError("O nome da categoria é obrigatório.")

    with transaction() as conn:
        # Verifica se já existe outra categoria com o mesmo nome
        existing = fetchone("SELECT id FROM categories WHERE nome = ? AND (? IS NULL OR id != ?)", (nome, category_id, category_id), conn=conn)
        if existing:
            raise ValueError(f"A categoria '{nome}' já existe.")

        if category_id:
            # Atualiza
            sql = "UPDATE categories SET nome = ?, margem_padrao = ? WHERE id = ?"
            execute_with_conn(conn, sql, (nome, margem_padrao, category_id))
            log('category', category_id, 'UPDATE', {'nome': nome, 'margem': margem_padrao}, user_id=get_current_user_id(), conn=conn)
            return category_id
        else:
            # Cria
            sql = "INSERT INTO categories (nome, margem_padrao) VALUES (?, ?)"
            new_id = execute_with_conn(conn, sql, (nome, margem_padrao))
            log('category', new_id, 'CREATE', {'nome': nome, 'margem': margem_padrao}, user_id=get_current_user_id(), conn=conn)
            return new_id