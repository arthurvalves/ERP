import sys
import os

# Força a raiz do projeto a ser o ponto de partida para as importações
sys.path.insert(0, os.path.abspath(os.path.dirname(__file__)))

from erp_backend.database.init_db import init_db
import erp_backend.core.events.handlers  # noqa: F401 - registra listeners por efeito colateral
from erp_backend.database.migrations_autocenter import run_autocenter_migrations
from erp_frontend.session import set_current_user
from erp_backend.utils.db import fetchone

from erp_frontend.main_window import MainWindow

def auto_login_admin():
    """Busca o usuário 'admin' e o define na sessão global."""
    admin_user = fetchone("SELECT * FROM users WHERE username = 'admin'")
    if admin_user:
        set_current_user(dict(admin_user))
    else:
        # Isso não deve acontecer se as migrações rodaram corretamente
        print("AVISO: Usuário 'admin' padrão não encontrado. Algumas funções podem falhar.")

if __name__ == "__main__":
    init_db()
    run_autocenter_migrations()
    auto_login_admin()  # Inicia a sessão do admin automaticamente
    app = MainWindow()

    # A forma mais robusta de maximizar: espera a janela ser "mapeada" na tela
    # e então aplica o estado 'zoomed'. Isso evita problemas de timing.
    def maximize_on_map(event):
        app.state('zoomed')
    app.bind("<Map>", maximize_on_map)

    app.mainloop()