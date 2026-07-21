from ..utils.db import fetchall
from datetime import datetime

def get_scheduled_orders_for_period(start_date: datetime, end_date: datetime):
    """
    Busca todas as Ordens de Serviço agendadas dentro de um período.
    """
    sql = """
        SELECT
            so.id, so.status, so.scheduled_start_time, so.scheduled_end_time,
            v.plate, v.model,
            c.nome_razao_social
        FROM service_orders so
        LEFT JOIN vehicles v ON so.vehicle_id = v.id
        LEFT JOIN customers c ON so.customer_id = c.id
        WHERE
            so.scheduled_start_time BETWEEN ? AND ?
        ORDER BY so.scheduled_start_time;
    """
    params = (start_date.strftime('%Y-%m-%d 00:00:00'), end_date.strftime('%Y-%m-%d 23:59:59'))
    return fetchall(sql, params)