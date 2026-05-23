from ..utils.db import execute, transaction, execute_with_conn
from ..services.stock_service import record_movement
from ..utils.audit import log
from ..core.events.event_bus import emit

def create_sale(customer_id: int, total: float, desconto_total: float, forma_pagamento: str, conn=None) -> int:
    sql = "INSERT INTO sales (customer_id,total,desconto_total,forma_pagamento) VALUES (?,?,?,?)"
    if conn is not None:
        sid = execute_with_conn(conn, sql, (customer_id, total, desconto_total, forma_pagamento))
    else:
        sid = execute(sql, (customer_id, total, desconto_total, forma_pagamento))
    log('sale', sid, 'CREATE', {'customer_id': customer_id, 'total': total}, conn=conn)
    try:
        emit('SaleCreated', {'sale_id': sid, 'total': total})
    except Exception:
        pass
    return sid

def add_sale_item(sale_id: int, product_id: int, quantidade: float, preco_unitario: float, desconto_item: float = 0.0, conn=None):
    sql = "INSERT INTO sales_items (sale_id,product_id,quantidade,preco_unitario,desconto_item) VALUES (?,?,?,?,?)"
    if conn is not None:
        item_id = execute_with_conn(conn, sql, (sale_id, product_id, quantidade, preco_unitario, desconto_item))
    else:
        item_id = execute(sql, (sale_id, product_id, quantidade, preco_unitario, desconto_item))
    # record stock movement (negative quantity for saída)
    record_movement(product_id, 'saida', -abs(quantidade), preco_unitario, 'PDV', sale_id, conn=conn)
    log('sale_item', item_id, 'CREATE', {'sale_id': sale_id, 'product_id': product_id, 'q': quantidade}, conn=conn)
    return item_id

def process_sale_transaction(customer_id: int, items: list, forma_pagamento: str):
    from ..core.validators import validate_sale_items
    validate_sale_items(items)
    total = sum((it['quantidade'] * it['preco_unitario'] - it.get('desconto_item', 0)) for it in items)
    with transaction() as conn:
        sale_id = create_sale(customer_id, total, 0.0, forma_pagamento, conn=conn)
        for it in items:
            add_sale_item(sale_id, it['product_id'], it['quantidade'], it['preco_unitario'], it.get('desconto_item', 0.0), conn=conn)
    return sale_id
