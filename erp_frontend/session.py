_current_user = None

def set_current_user(user: dict):
    """Define o usuário atualmente logado na sessão."""
    global _current_user
    _current_user = user

def get_current_user():
    """Retorna o dicionário completo do usuário logado."""
    return _current_user

def get_current_user_id() -> int | None:
    """Retorna apenas o ID do usuário logado."""
    if _current_user:
        return _current_user.get('id')
    return None

def clear_session():
    """Limpa a sessão do usuário (logout)."""
    global _current_user
    _current_user = None