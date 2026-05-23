def compute_stock_from_movements(movements):
    total = 0
    for m in movements:
        total += m.get('quantidade', 0)
    return total
