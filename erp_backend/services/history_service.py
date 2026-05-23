from ..utils.db import execute, execute_with_conn

def log_price_change(product_id: int, old_price: float, new_price: float, change_type: str = 'rule', conn=None):
    sql = 'INSERT INTO product_price_history (product_id, old_price, new_price, change_type) VALUES (?,?,?,?)'
    params = (product_id, old_price, new_price, change_type)
    if conn is not None:
        return execute_with_conn(conn, sql, params)
    return execute(sql, params)

def log_cost_change(product_id: int, old_cost: float, new_cost: float, supplier_id: int = None, nf_e_id: int = None, conn=None):
    sql = 'INSERT INTO product_cost_history (product_id, old_cost, new_cost, supplier_id, nf_e_id) VALUES (?,?,?,?,?)'
    params = (product_id, old_cost, new_cost, supplier_id, nf_e_id)
    if conn is not None:
        return execute_with_conn(conn, sql, params)
    return execute(sql, params)
