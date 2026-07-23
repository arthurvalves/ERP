from ..utils.db import transaction, fetchone, fetchall, execute_with_conn
from ..utils.audit import log
from erp_frontend.session import get_current_user_id

def get_all_customers(search_term: str = ""):
    """Busca todos os clientes, com filtro opcional por nome ou documento."""
    sql = "SELECT id, nome_razao_social, cpf_cnpj, telefone, email FROM customers"
    params = ()
    if search_term:
        sql += " WHERE nome_razao_social LIKE ? OR cpf_cnpj LIKE ?"
        params = (f"%{search_term}%", f"%{search_term}%")
    sql += " ORDER BY nome_razao_social ASC LIMIT 100"
    return fetchall(sql, params)

def get_customer_by_id(customer_id: int):
    """Busca um cliente específico pelo seu ID."""
    return fetchone("SELECT * FROM customers WHERE id = ?", (customer_id,))

def create_customer(data: dict) -> int:
    """
    Cria um novo cliente no banco de dados.
    Retorna o ID do novo cliente.
    """
    # Validação básica
    if not data.get('nome_razao_social') or not data.get('cpf_cnpj'):
        raise ValueError("Nome/Razão Social e CPF/CNPJ são obrigatórios.")

    with transaction() as conn:
        # Verificar se cliente com mesmo CPF/CNPJ já existe
        existing = fetchone("SELECT id FROM customers WHERE cpf_cnpj = ?", (data['cpf_cnpj'],), conn=conn)
        if existing:
            raise ValueError(f"Já existe um cliente com o CPF/CNPJ {data['cpf_cnpj']}.")

        sql = """
            INSERT INTO customers (nome_razao_social, cpf_cnpj, telefone, email, endereco)
            VALUES (:nome_razao_social, :cpf_cnpj, :telefone, :email, :endereco)
        """
        customer_id = execute_with_conn(conn, sql, data)
        log('customer', customer_id, 'CREATE', data, user_id=get_current_user_id(), conn=conn)
        return customer_id