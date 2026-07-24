from ..utils.db import fetchall
from datetime import datetime
import pytz # Recommended to install: pip install pytz
try:
    import pytz # Recommended to install: pip install pytz
except ImportError:
    pytz = None

def _get_utc_date_range(start_date: datetime, end_date: datetime) -> tuple:
    """Converte datas locais para um intervalo de strings em UTC para queries SQL."""
    if pytz:
        try:
            local_tz = pytz.timezone("America/Sao_Paulo") # Ou seu fuso horário local
            start_utc = local_tz.localize(start_date.replace(hour=0, minute=0, second=0)).astimezone(pytz.utc)
            end_utc = local_tz.localize(end_date.replace(hour=23, minute=59, second=59)).astimezone(pytz.utc)
            return (start_utc.strftime('%Y-%m-%d %H:%M:%S'), end_utc.strftime('%Y-%m-%d %H:%M:%S'))
        except pytz.UnknownTimeZoneError: pass
    return (start_date.strftime('%Y-%m-%d 00:00:00'), end_date.strftime('%Y-%m-%d 23:59:59'))

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
    params = _get_utc_date_range(start_date, end_date)
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
    params = _get_utc_date_range(start_date, end_date)
    return fetchall(sql, params)