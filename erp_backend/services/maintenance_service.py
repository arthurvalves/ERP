from ..utils.db import fetchall

def get_maintenance_alerts():
    """
    Busca veículos que precisam de manutenção preventiva.
    Regra de Exemplo: Alerta para troca de óleo a cada 10.000 km.
    """
    # Esta é uma consulta complexa que:
    # 1. Busca todos os veículos com KM registrado.
    # 2. Para cada veículo, encontra a última OS que continha o serviço "TROCA DE OLEO".
    # 3. Calcula a diferença de KM entre a KM atual e a KM da última troca.
    # 4. Retorna os veículos onde essa diferença é maior que 10.000 km.
    sql = """
        WITH LastOilChange AS (
            -- Encontra a KM da última troca de óleo para cada veículo
            SELECT
                so.vehicle_id,
                MAX(v.current_km) as km_at_last_change
            FROM service_order_items soi
            JOIN products p ON soi.product_id = p.id
            JOIN service_orders so ON soi.service_order_id = so.id
            JOIN vehicles v ON so.vehicle_id = v.id
            WHERE p.nome LIKE '%TROCA DE OLEO%'
            GROUP BY so.vehicle_id
        )
        SELECT
            v.id as vehicle_id,
            v.plate,
            v.model,
            v.current_km,
            loc.km_at_last_change,
            c.nome_razao_social as customer_name,
            c.telefone as customer_phone
        FROM vehicles v
        JOIN customers c ON v.customer_id = c.id
        LEFT JOIN LastOilChange loc ON v.id = loc.vehicle_id
        WHERE
            v.current_km IS NOT NULL AND v.current_km > 0
            AND (loc.km_at_last_change IS NULL OR (v.current_km - loc.km_at_last_change) >= 10000)
        ORDER BY (v.current_km - IFNULL(loc.km_at_last_change, 0)) DESC;
    """
    return fetchall(sql)