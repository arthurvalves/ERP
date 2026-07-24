def calculate_price(custo: float, margem: float) -> float:
    return round(custo * (1 + margem / 100.0), 4)
