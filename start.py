import sys
import os

# Força a raiz do projeto a ser o ponto de partida para as importações
sys.path.insert(0, os.path.abspath(os.path.dirname(__file__)))

from erp_backend.database.init_db import init_db
import erp_backend.core.events.handlers  # noqa: F401 - registra listeners por efeito colateral
from erp_backend.database.migrations_autocenter import run_autocenter_migrations

from erp_frontend.main_window import MainWindow

if __name__ == "__main__":
    init_db()
    run_autocenter_migrations()
    app = MainWindow()
    try:
        app.state('zoomed')
    except Exception:
        pass
    app.mainloop()