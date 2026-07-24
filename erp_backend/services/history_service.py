from ..utils.db import fetchall, fetchone

def get_vehicle_history_by_plate(plate: str):
    """
    Busca o histórico completo de um veículo pela placa.
    Retorna os dados do veículo e uma lista de suas ordens de serviço com itens.
    """
    plate = plate.strip().upper()
    if not plate:
        return None, []

    # 1. Busca o veículo e o cliente associado
    vehicle_data = fetchone("""
        SELECT v.*, c.nome_razao_social, c.telefone
        FROM vehicles v
        JOIN customers c ON v.customer_id = c.id
        WHERE v.plate = ?
    """, (plate,))

    if not vehicle_data:
        return None, []

    # 2. Busca todas as Ordens de Serviço para este veículo
    service_orders = fetchall("""
        SELECT * FROM service_orders
        WHERE vehicle_id = ?
        ORDER BY data_abertura DESC
    """, (vehicle_data['id'],))

    if not service_orders:
        return dict(vehicle_data), []

    # 3. Para cada OS, busca seus itens e os técnicos responsáveis
    history = []
    for so in service_orders:
        so_dict = dict(so)
        items = fetchall("""
            SELECT i.*, p.nome as product_name, u.username as technician_name
            FROM service_order_items i
            JOIN products p ON i.product_id = p.id
            LEFT JOIN users u ON i.technician_id = u.id
            WHERE i.service_order_id = ?
        """, (so['id'],))
        so_dict['items'] = [dict(item) for item in items]
        history.append(so_dict)

    return dict(vehicle_data), history
