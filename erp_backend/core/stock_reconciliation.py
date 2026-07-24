from ..utils.db import get_connection
from ..utils.audit import log

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
