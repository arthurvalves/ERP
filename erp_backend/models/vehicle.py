from typing import Optional

class Vehicle:
    def __init__(self, id: Optional[int], customer_id: int, plate: str, brand: Optional[str], model: Optional[str], year: Optional[int], color: Optional[str], vin: Optional[str], current_km: Optional[int]):
        self.id = id
        self.customer_id = customer_id
        self.plate = plate
        self.brand = brand
        self.model = model
        self.year = year
        self.color = color
        self.vin = vin
        self.current_km = current_km

    @classmethod
    def from_row(cls, row) -> 'Vehicle':
        """Creates a Vehicle instance from a database row."""
        if row is None:
            return None
        return cls(
            id=row['id'], customer_id=row['customer_id'], plate=row['plate'],
            brand=row.get('brand'), model=row.get('model'), year=row.get('year'),
            color=row.get('color'), vin=row.get('vin'), current_km=row.get('current_km')
        )