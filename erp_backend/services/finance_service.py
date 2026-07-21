from datetime import datetime, timedelta
from ..utils.db import execute_with_conn, fetchall, fetchone, execute
from ..utils.audit import log
from erp_frontend.session import get_current_user_id
from .cash_service import get_open_session, add_cash_movement

def generate_installments_for_sale(
    sale_id: int, 
    customer_id: int, 
    total_amount: float, 
    installments_count: int, 
    conn
):
    """
    Gera as parcelas de uma venda no contas a receber.
    """
    if installments_count <= 0:
        installments_count = 1

    installment_amount = round(total_amount / installments_count, 2)
    # Corrige a última parcela para evitar diferenças de arredondamento
    last_installment_amount = total_amount - (installment_amount * (installments_count - 1))

    today = datetime.today()

    for i in range(installments_count):
        due_date = today + timedelta(days=30 * (i + 1))
        current_amount = last_installment_amount if (i + 1) == installments_count else installment_amount

        sql = """
            INSERT INTO accounts_receivable (sale_id, customer_id, installment_number, total_installments, amount, due_date, status)
            VALUES (?, ?, ?, ?, ?, ?, 'pending')
        """
        params = (sale_id, customer_id, i + 1, installments_count, current_amount, due_date.strftime('%Y-%m-%d'))
        execute_with_conn(conn, sql, params)

def get_receivables(search_term: str = ""):
    """Busca todas as parcelas a receber, com status 'pending' ou 'overdue'."""
    # Atualiza o status de parcelas vencidas
    execute("UPDATE accounts_receivable SET status = 'overdue' WHERE due_date < date('now') AND status = 'pending'")

    sql = """
        SELECT ar.*, c.nome_razao_social
        FROM accounts_receivable ar
        JOIN customers c ON ar.customer_id = c.id
        WHERE ar.status IN ('pending', 'overdue')
    """
    params = ()
    if search_term:
        sql += " AND (c.nome_razao_social LIKE ? OR ar.sale_id = ?)"
        params = (f"%{search_term}%", search_term)
    
    sql += " ORDER BY ar.due_date ASC"
    return fetchall(sql, params)

def get_installment_details_for_notification(installment_id: int):
    """Busca detalhes de uma parcela e do cliente para notificação."""
    return fetchone("""
        SELECT ar.*, c.nome_razao_social, c.telefone
        FROM accounts_receivable ar
        JOIN customers c ON ar.customer_id = c.id
        WHERE ar.id = ?
    """, (installment_id,))

def settle_installment(installment_id: int, payment_method: str):
    """Dá baixa em uma parcela e registra a entrada no caixa, se aplicável."""
    user_id = get_current_user_id()
    with transaction() as conn:
        execute_with_conn(conn, "UPDATE accounts_receivable SET status = 'paid', payment_date = date('now') WHERE id = ?", (installment_id,))
        
        open_session = get_open_session()
        if open_session:
            details = get_installment_details_for_notification(installment_id)
            add_cash_movement(open_session['id'], 'venda', details['amount'], f"Pagamento Parcela #{installment_id}", payment_method, installment_id, conn=conn)
        
        log('accounts_receivable', installment_id, 'SETTLE', {'payment_method': payment_method}, user_id=user_id, conn=conn)