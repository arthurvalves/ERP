from .stock_reconciliation import detect_stock_inconsistencies

def run_all_checks():
    anomalies = detect_stock_inconsistencies()
    # placeholder for more checks (price outliers etc.)
    return anomalies
