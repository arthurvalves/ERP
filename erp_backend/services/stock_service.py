from ..utils.db import execute, execute_with_conn, fetchall
from ..utils.audit import log
from ..core.events.event_bus import emit
from erp_frontend.session import get_current_user_id

def record_movement(product_id: int, tipo: str, quantidade: float, custo_unitario: float, origem: str, referencia_id: int = None, conn=None):
    sql = """
    INSERT INTO stock_movements (product_id,tipo,quantidade,custo_unitario,origem,referencia_id)
    VALUES (?,?,?,?,?,?)
    """
    params = (product_id, tipo, quantidade, custo_unitario, origem, referencia_id)
    user_id = get_current_user_id()
    if conn is not None:
        mov_id = execute_with_conn(conn, sql, params)
    else:
        mov_id = execute(sql, params)
    # recompute product stock from movements
    recompute_stock(product_id, conn=conn)
    log('stock_movement', mov_id, 'CREATE', {'product_id': product_id, 'q': quantidade, 'origem': origem}, user_id=user_id, conn=conn)
    try:
        emit('StockUpdated', {'product_id': product_id, 'movement_id': mov_id, 'quantidade': quantidade})
    except Exception:
        pass
    return mov_id

def recompute_stock(product_id: int, conn=None):
    qsql = 'SELECT SUM(quantidade) as total FROM stock_movements WHERE product_id = ?'
    if conn is not None:
        cur = conn.cursor()
        cur.execute(qsql, (product_id,))
        row = cur.fetchone()
        total = row[0] if row and row[0] is not None else 0
        conn.execute('UPDATE products SET estoque_atual = ? WHERE id = ?', (total, product_id))
    else:
        rows = fetchall(qsql, (product_id,))
        total = rows[0]['total'] if rows and rows[0]['total'] is not None else 0
        from ..utils.db import execute
        execute('UPDATE products SET estoque_atual = ? WHERE id = ?', (total, product_id))
