import bcrypt
from ..utils.db import fetchone

def hash_password(password: str) -> str:
    """Gera um hash seguro para a senha."""
    salt = bcrypt.gensalt()
    hashed = bcrypt.hashpw(password.encode('utf-8'), salt)
    return hashed.decode('utf-8')

def check_password(password: str, hashed_password: str) -> bool:
    """Verifica se a senha fornecida corresponde ao hash."""
    return bcrypt.checkpw(password.encode('utf-8'), hashed_password.encode('utf-8'))

def authenticate_user(username: str, password: str) -> dict | None:
    """
    Autentica um usuário. Retorna os dados do usuário em caso de sucesso,
    ou None em caso de falha.
    """
    if not username or not password:
        return None

    user_data = fetchone("SELECT * FROM users WHERE username = ?", (username,))
    
    if not user_data:
        return None

    if check_password(password, user_data['password_hash']):
        return dict(user_data)
        
    return None