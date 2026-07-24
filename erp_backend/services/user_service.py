from ..utils.db import fetchall

def get_technicians():
    """Retorna uma lista de todos os usuários com o perfil 'mecanico'."""
    sql = "SELECT id, username FROM users WHERE profile = 'mecanico' ORDER BY username"
    return fetchall(sql)