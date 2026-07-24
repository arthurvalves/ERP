from ..models.vehicle import Vehicle
from ..utils.db import execute, fetchone, fetchall
from typing import List, Optional


def create_or_update_vehicle(vehicle: Vehicle, conn=None) -> int:
    """Cria um novo veículo ou atualiza um existente pela placa."""
    existing = fetchone("SELECT id FROM vehicles WHERE plate = ?", (vehicle.plate,), conn=conn)
    if existing:
        vehicle.id = existing['id']
        sql = "UPDATE vehicles SET customer_id=?, brand=?, model=?, year=? WHERE id=?"
        params = (vehicle.customer_id, vehicle.brand, vehicle.model, vehicle.year, vehicle.id)
        execute(sql, params, conn=conn)
        return vehicle.id
    else:
        sql = "INSERT INTO vehicles (customer_id, plate, brand, model, year) VALUES (?, ?, ?, ?, ?)"
        params = (vehicle.customer_id, vehicle.plate, vehicle.brand, vehicle.model, vehicle.year)
        return execute(sql, params, conn=conn)


def get_vehicle_by_plate(plate: str, conn=None) -> Optional[Vehicle]:
    """Busca um veículo pela placa."""
    row = fetchone("SELECT * FROM vehicles WHERE plate = ?", (plate.upper().strip(),), conn=conn)
    return Vehicle.from_row(row) if row else None


def get_vehicles_by_customer(customer_id: int, conn=None) -> List[Vehicle]:
    """Busca todos os veículos associados a um cliente."""
    rows = fetchall("SELECT * FROM vehicles WHERE customer_id = ? ORDER BY model", (customer_id,), conn=conn)
    return [Vehicle.from_row(row) for row in rows]

def get_vehicle_by_id(vehicle_id: int, conn=None) -> Optional[Vehicle]:
    """Busca um veículo pelo seu ID."""
    row = fetchone("SELECT * FROM vehicles WHERE id = ?", (vehicle_id,), conn=conn)
    return Vehicle.from_row(row) if row else None