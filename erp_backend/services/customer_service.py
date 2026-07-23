from ..models.customer import Customer
from ..utils.db import transaction, fetchone, fetchall, execute_with_conn
from ..utils.audit import log
from erp_frontend.session import get_current_user_id
from typing import List, Optional
import logging

def get_customer_by_id(customer_id: int, conn=None) -> Optional[Customer]:
    """Busca um cliente pelo seu ID."""
    if not customer_id: return None # Adiciona uma verificação para evitar erros com ID nulo
    row = fetchone("SELECT * FROM customers WHERE id = ?", (customer_id,), conn=conn)
    return Customer.from_row(row) if row else None

def search_customers(search_term: str) -> List[Customer]:
    """Busca clientes por nome/razão social ou CPF/CNPJ."""
    query = "SELECT * FROM customers WHERE nome_razao_social LIKE ? OR cpf_cnpj LIKE ? ORDER BY nome_razao_social LIMIT 50"
    params = (f"%{search_term}%", f"%{search_term}%")
    rows = fetchall(query, params)
    return [Customer.from_row(row) for row in rows]

def create_or_update_customer(data: dict) -> int:
    """
    Cria um novo cliente ou atualiza um existente.
    Retorna o ID do cliente.
    """
    customer_id = data.get("id")

    # Validação básica
    if not data.get('nome_razao_social') or not data.get('cpf_cnpj'):
        raise ValueError("Nome/Razão Social e CPF/CNPJ são obrigatórios.")

    with transaction() as conn:
        # Garante que o CPF/CNPJ é único, excluindo o próprio cliente (em caso de edição)
        # A query foi corrigida para usar o número correto de parâmetros.
        # A lógica é: "encontre um cliente com este CPF/CNPJ que NÃO SEJA o cliente que estou editando".
        query = "SELECT id FROM customers WHERE cpf_cnpj = ? AND (? IS NULL OR id != ?)" 
        params = (data['cpf_cnpj'], customer_id, customer_id)
        existing = fetchone(query, params, conn=conn)
        if existing:
            raise ValueError(f"O CPF/CNPJ {data['cpf_cnpj']} já está em uso por outro cliente.")

        if customer_id:
            # Atualiza cliente existente
            sql = """UPDATE customers SET nome_razao_social=:nome_razao_social, cpf_cnpj=:cpf_cnpj, telefone=:telefone, email=:email, endereco=:endereco WHERE id=:id"""
            execute_with_conn(conn, sql, data)
            log('customer', customer_id, 'UPDATE', data, user_id=get_current_user_id(), conn=conn)
            return customer_id
        else:
            # Cria novo cliente
            sql = """INSERT INTO customers (nome_razao_social, cpf_cnpj, telefone, email, endereco) VALUES (:nome_razao_social, :cpf_cnpj, :telefone, :email, :endereco)"""
            new_id = execute_with_conn(conn, sql, data)
            log('customer', new_id, 'CREATE', data, user_id=get_current_user_id(), conn=conn)
            return new_id

def delete_customer_by_id(customer_id: int) -> bool:
    """
    Deleta um cliente pelo seu ID.
    Verifica se o cliente possui veículos ou ordens de serviço associadas antes de deletar.
    """
    with transaction() as conn:
        # Verifica dependências
        has_vehicles = fetchone("SELECT 1 FROM vehicles WHERE customer_id = ?", (customer_id,), conn=conn)
        if has_vehicles:
            raise ValueError("Não é possível excluir: o cliente possui um ou mais veículos cadastrados.")

        has_os = fetchone("SELECT 1 FROM service_orders WHERE customer_id = ?", (customer_id,), conn=conn)
        if has_os:
            raise ValueError("Não é possível excluir: o cliente possui ordens de serviço associadas.")

        execute_with_conn(conn, "DELETE FROM customers WHERE id = ?", (customer_id,))
        log('customer', customer_id, 'DELETE', {'id': customer_id}, user_id=get_current_user_id(), conn=conn)
        logging.info(f"Cliente ID {customer_id} deletado com sucesso.")
        return True