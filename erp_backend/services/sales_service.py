from ..utils.db import execute, transaction, execute_with_conn
from ..services.stock_service import record_movement
from ..utils.audit import log
from ..core.events.event_bus import emit
from erp_frontend.session import get_current_user_id
from .cash_service import get_open_session, add_cash_movement
from .finance_service import generate_installments_for_sale

def create_sale(customer_id: int, total: float, desconto_total: float, forma_pagamento: str, installments: int = 1, conn=None) -> int:
    # Modificação: O caixa se torna opcional. Se houver uma sessão aberta, a venda é vinculada.
    # Se não, a venda é criada sem o vínculo, permitindo a operação direta do PDV.
    open_session_data = get_open_session()
    session_id = open_session_data['id'] if open_session_data else None
    
    sql = "INSERT INTO sales (customer_id, total, desconto_total, forma_pagamento, session_id) VALUES (?,?,?,?,?)"
    user_id = get_current_user_id()
    if conn is not None:
        sid = execute_with_conn(conn, sql, (customer_id, total, desconto_total, forma_pagamento, session_id))
    else:
        sid = execute(sql, (customer_id, total, desconto_total, forma_pagamento, session_id))
    
    log('sale', sid, 'CREATE', {'customer_id': customer_id, 'total': total}, user_id=user_id, conn=conn)
    
    # Só registra a movimentação no caixa se houver uma sessão ativa
    if session_id and forma_pagamento != 'CREDIARIO':
        add_cash_movement(session_id, 'venda', total, f"Venda #{sid}", forma_pagamento, sid, conn=conn)

    # Se a venda for no crediário, gera as parcelas no contas a receber
    if forma_pagamento == 'CREDIARIO':
        if not customer_id:
            raise ValueError("Um cliente deve ser selecionado para vendas no crediário.")
        generate_installments_for_sale(sid, customer_id, total, installments, conn=conn)
    
    try:
        emit('SaleCreated', {'sale_id': sid, 'total': total})
    except Exception:
        pass
    return sid

def add_sale_item(sale_id: int, product_id: int, quantidade: float, preco_unitario: float, desconto_item: float = 0.0, conn=None):
    if conn is None:
        raise ValueError("Uma conexão (transação) é obrigatória para adicionar itens.")
    user_id = get_current_user_id()
        
    cur = conn.cursor()
        
    # 1. Verifica o stock atual
    cur.execute("SELECT estoque_atual, nome FROM products WHERE id = ?", (product_id,))
    prod = cur.fetchone()
        
    if not prod:
        raise ValueError("Produto não encontrado.")
            
    if prod['estoque_atual'] < quantidade:
        raise ValueError(
            f"Estoque insuficiente para '{prod['nome']}'. "
            f"Tentativa: {quantidade} | Disponível: {prod['estoque_atual']}"
        )
            
    # 2. Insere o item da venda na tabela correta (sales_items)
    cur.execute("""
        INSERT INTO sales_items (sale_id, product_id, quantidade, preco_unitario, desconto_item)
        VALUES (?, ?, ?, ?, ?)
    """, (sale_id, product_id, quantidade, preco_unitario, desconto_item))
    
    # Captura o ID da linha que acabou de ser inserida
    item_id = cur.lastrowid

    # 3. Regista o movimento de stock e o log de auditoria
    record_movement(product_id, 'saida', -abs(quantidade), preco_unitario, 'PDV', sale_id, conn=conn)
    log('sale_item', item_id, 'CREATE', {'sale_id': sale_id, 'product_id': product_id, 'q': quantidade}, user_id=user_id, conn=conn)
    
    return item_id

def process_sale_transaction(customer_id: int, items: list, forma_pagamento: str, desconto_total: float = 0.0, installments: int = 1):
    from ..core.validators import validate_sale_items
    validate_sale_items(items)
    total = sum((it['quantidade'] * it['preco_unitario'] - it.get('desconto_item', 0)) for it in items)
    total = max(0.0, total - desconto_total)
    with transaction() as conn:
        sale_id = create_sale(customer_id, total, desconto_total, forma_pagamento, installments, conn=conn)
        for it in items:
            add_sale_item(sale_id, it['product_id'], it['quantidade'], it['preco_unitario'], it.get('desconto_item', 0.0), conn=conn)
    return sale_id
