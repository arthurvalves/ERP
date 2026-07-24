from ..utils.db import execute, fetchone, execute_with_conn
from ..services.stock_service import record_movement
from ..utils.audit import log
from ..core.events.event_bus import emit

def register_purchase(chave_acesso: str, supplier_id: int, valor_total: float, data_emissao: str = None, conn=None) -> int:
    # check existence
    existing = fetchone('SELECT id FROM purchases WHERE chave_acesso = ?', (chave_acesso,))
    if existing:
        raise ValueError('NF-e já processada')
    sql = 'INSERT INTO purchases (chave_acesso,supplier_id,valor_total,data_emissao) VALUES (?,?,?,?)'
    if conn is not None:
        purchase_id = execute_with_conn(conn, sql, (chave_acesso, supplier_id, valor_total, data_emissao))
    else:
        purchase_id = execute(sql, (chave_acesso, supplier_id, valor_total, data_emissao))
    log('purchase', purchase_id, 'CREATE', {'chave_acesso': chave_acesso, 'supplier_id': supplier_id}, conn=conn)
    try:
        emit('PurchaseCreated', {'purchase_id': purchase_id, 'chave': chave_acesso})
    except Exception:
        pass
    return purchase_id

def add_purchase_item(purchase_id: int, product_id: int, descricao_xml: str, quantidade: float, valor_unitario: float, ncm: str = None, conn=None):
    sql = "INSERT INTO purchase_items (purchase_id,product_id,descricao_xml,quantidade,valor_unitario,ncm) VALUES (?,?,?,?,?,?)"
    if conn is not None:
        item_id = execute_with_conn(conn, sql, (purchase_id, product_id, descricao_xml, quantidade, valor_unitario, ncm))
    else:
        item_id = execute(sql, (purchase_id, product_id, descricao_xml, quantidade, valor_unitario, ncm))
    # record stock movement using same conn when available
    record_movement(product_id, 'entrada', quantidade, valor_unitario, 'NF-e', purchase_id, conn=conn)
    log('purchase_item', item_id, 'CREATE', {'purchase_id': purchase_id, 'product_id': product_id, 'q': quantidade}, conn=conn)
    return item_id
