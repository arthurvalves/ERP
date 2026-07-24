from ..utils.db import transaction, fetchone, fetchall, execute_with_conn

def get_all_quotes(search_term: str = ""):
    """Busca todos os orçamentos, com filtro opcional."""
    sql = """
        SELECT q.*, c.nome_razao_social, v.plate, v.model
        FROM quotes q
        LEFT JOIN customers c ON q.customer_id = c.id
        LEFT JOIN vehicles v ON q.vehicle_id = v.id
    """
    params = ()
    if search_term:
        sql += " WHERE c.nome_razao_social LIKE ? OR v.plate LIKE ? OR q.status LIKE ?"
        params = (f"%{search_term}%", f"%{search_term}%", f"%{search_term}%")
    sql += " ORDER BY q.id DESC LIMIT 100"
    return fetchall(sql, params)

def get_quote_details(quote_id: int):
    """Busca os detalhes de um orçamento e seus itens."""
    quote_data = fetchone("SELECT * FROM quotes WHERE id = ?", (quote_id,))
    if not quote_data:
        return None, []

    items = fetchall("""
        SELECT i.*, p.nome, p.sku, p.codigo_barras, p.is_servico
        FROM quote_items i
        JOIN products p ON i.product_id = p.id
        WHERE i.quote_id = ?
    """, (quote_id,))
    
    return dict(quote_data), [dict(item) for item in items]

def convert_quote_to_os(quote_id: int) -> int:
    """
    Converte um orçamento em uma nova Ordem de Serviço.
    Copia cliente, veículo e todos os itens.
    """
    with transaction() as conn:
        try:
            # 1. Pega os dados do orçamento
            quote_data, items = get_quote_details(quote_id)
            quote = dict(quote_data) if quote_data else None
            if not quote:
                raise ValueError("Orçamento não encontrado.")
            if quote['status'] == 'Convertido':
                raise ValueError("Este orçamento já foi convertido em uma OS.")

            # 2. Cria a nova Ordem de Serviço
            total_pecas = sum(i['quantidade'] * i['preco_unitario'] for i in items if not i.get('is_servico'))
            total_servicos = sum(i['quantidade'] * i['preco_unitario'] for i in items if i.get('is_servico'))
            total_geral = total_pecas + total_servicos

            os_id = execute_with_conn(conn, """
                INSERT INTO service_orders (customer_id, vehicle_id, status, total_pecas, total_servicos, total_geral)
                VALUES (?, ?, 'Aberta', ?, ?, ?)
            """, (quote['customer_id'], quote['vehicle_id'], total_pecas, total_servicos, total_geral))

            # 3. Copia os itens do orçamento para a OS
            for item in items:
                tipo = 'servico' if item.get('is_servico') else 'peca'
                execute_with_conn(conn, """
                    INSERT INTO service_order_items (service_order_id, product_id, tipo, quantidade, preco_unitario)
                    VALUES (?, ?, ?, ?, ?)
                """, (os_id, item['product_id'], tipo, item['quantidade'], item['preco_unitario']))

            # 4. Atualiza o status do orçamento
            execute_with_conn(conn, "UPDATE quotes SET status='Convertido' WHERE id=?", (quote_id,))
            return os_id
        except (ValueError, Exception) as e:
            conn.rollback()
            # Re-raise the exception to be handled by the UI layer
            raise e
