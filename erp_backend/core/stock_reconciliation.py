from .domain.stock_rules import compute_stock_from_movements
from ..utils.db import get_connection
from ..utils.audit import log

def recompute_stock(product_id: int):
    conn = get_connection()
    cur = conn.cursor()
    cur.execute('SELECT quantidade FROM stock_movements WHERE product_id = ?', (product_id,))
    rows = cur.fetchall()
    movements = [{'quantidade': r[0]} for r in rows]
    total = compute_stock_from_movements(movements)
    # before
    cur.execute('SELECT estoque_atual FROM products WHERE id = ?', (product_id,))
    before = cur.fetchone()[0]
    cur.execute('UPDATE products SET estoque_atual = ? WHERE id = ?', (total, product_id))
    conn.commit()
    # audit if mismatch
    if before != total:
        log('stock_reconciliation', product_id, 'RECONCILE', {'before': before}, conn=conn)
    conn.close()

def detect_stock_inconsistencies():
    conn = get_connection()
    cur = conn.cursor()
    cur.execute('SELECT id FROM products')
    products = [r[0] for r in cur.fetchall()]
    anomalies = []
    for pid in products:
        cur.execute('SELECT estoque_atual FROM products WHERE id = ?', (pid,))
        atual = cur.fetchone()[0]
        cur.execute('SELECT SUM(quantidade) FROM stock_movements WHERE product_id = ?', (pid,))
        total = cur.fetchone()[0] or 0
        if atual != total:
            anomalies.append({'product_id': pid, 'estoque_atual': atual, 'movements_total': total})
            log('anomaly', pid, 'STOCK_MISMATCH', {'atual': atual, 'total': total}, conn=conn)
    conn.close()
    return anomalies
