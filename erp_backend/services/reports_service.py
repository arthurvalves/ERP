from ..utils.db import fetchall
from datetime import datetime

def get_technician_productivity(start_date: datetime, end_date: datetime):
    """
    Calcula a produtividade dos técnicos em um determinado período.
    Retorna o nome do técnico, a quantidade de serviços/itens e o valor total gerado.
    """
    sql = """
        SELECT
            u.username as technician_name,
            COUNT(soi.id) as total_items,
            SUM(soi.quantidade * soi.preco_unitario) as total_value
        FROM
            service_order_items soi
        JOIN
            users u ON soi.technician_id = u.id
        JOIN
            service_orders so ON soi.service_order_id = so.id
        WHERE
            soi.technician_id IS NOT NULL AND so.data_abertura BETWEEN ? AND ?
        GROUP BY
            u.id, u.username
        ORDER BY
            total_value DESC;
    """
    params = (start_date.strftime('%Y-%m-%d 00:00:00'), end_date.strftime('%Y-%m-%d 23:59:59'))
    return fetchall(sql, params)

def get_sales_by_period(start_date: datetime, end_date: datetime):
    """
    Busca e totaliza as vendas por forma de pagamento em um determinado período.
    """
    sql = """
        SELECT
            forma_pagamento,
            COUNT(id) as total_sales,
            SUM(total) as total_value
        FROM sales
        WHERE data BETWEEN ? AND ?
        GROUP BY forma_pagamento
        ORDER BY total_value DESC;
    """
    params = (start_date.strftime('%Y-%m-%d 00:00:00'), end_date.strftime('%Y-%m-%d 23:59:59'))
    return fetchall(sql, params)