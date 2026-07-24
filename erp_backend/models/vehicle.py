from typing import Optional

class Vehicle:
    def __init__(
        self, 
        id: Optional[int], 
        customer_id: int, 
        plate: str, 
        brand: Optional[str] = None, 
        model: Optional[str] = None, 
        year: Optional[int] = None, 
        color: Optional[str] = None, 
        vin: Optional[str] = None, 
        current_km: Optional[int] = None
    ):
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
            brand=row['brand'], model=row['model'], year=row['year'],
            color=row['color'], vin=row['vin'], current_km=row['current_km']
        )