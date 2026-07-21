from ..utils.db import transaction, fetchone, execute, execute_with_conn
from ..utils.audit import log
from erp_frontend.session import get_current_user_id, get_current_user

def get_open_session():
    """Verifica se existe uma sessão de caixa aberta e a retorna."""
    return fetchone("SELECT * FROM cash_sessions WHERE status = 'open'")

def open_session(initial_balance: float) -> int:
    """Abre uma nova sessão de caixa para o usuário logado."""
    user = get_current_user()
    if not user:
        raise PermissionError("Nenhum usuário está logado para abrir o caixa.")

    if get_open_session():
        raise ValueError("Já existe uma sessão de caixa aberta.")

    with transaction() as conn:
        session_id = execute_with_conn(conn, """
            INSERT INTO cash_sessions (user_id, initial_balance, status)
            VALUES (?, ?, 'open')
        """, (user['id'], initial_balance))

        execute_with_conn(conn, """
            INSERT INTO cash_movements (session_id, user_id, type, amount, notes)
            VALUES (?, ?, 'abertura', ?, 'Abertura de caixa')
        """, (session_id, user['id'], initial_balance))

        log('cash_session', session_id, 'OPEN', {'initial_balance': initial_balance}, user_id=user['id'], conn=conn)
        return session_id

def add_cash_movement(session_id: int, type: str, amount: float, notes: str, payment_method: str = None, reference_id: int = None, conn=None):
    """Adiciona uma movimentação de caixa (sangria, suprimento ou venda)."""
    user_id = get_current_user_id()
    if not user_id:
        raise PermissionError("Nenhum usuário está logado.")

    # Garante que sangrias sejam negativas
    if type == 'sangria':
        amount = -abs(amount)
    # Garante que suprimentos e vendas sejam positivos
    elif type in ['suprimento', 'venda']:
        amount = abs(amount)

    sql = """
        INSERT INTO cash_movements (session_id, user_id, type, amount, notes, payment_method, reference_id)
        VALUES (?, ?, ?, ?, ?, ?, ?)
    """
    params = (session_id, user_id, type, amount, notes, payment_method, reference_id)
    execute_with_conn(conn, sql, params) if conn else execute(sql, params)