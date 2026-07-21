class Vehicle:
    def __init__(self, plate, brand, model, year, customer_id, id=None):
        self.id = id
        self.plate = plate.upper().strip()
        self.brand = brand
        self.model = model
        self.year = year
        self.customer_id = customer_id

    def to_dict(self):
        return {
            "id": self.id,
            "plate": self.plate,
            "brand": self.brand,
            "model": self.model,
            "year": self.year,
            "customer_id": self.customer_id
        }