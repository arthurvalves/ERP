import os

BASE_DIR = os.path.dirname(os.path.dirname(__file__))
DB_PATH = os.environ.get("ERP_DB_PATH") or os.path.join(BASE_DIR, "erp.db")

DEFAULTS = {
    "DB_PATH": DB_PATH,
}
