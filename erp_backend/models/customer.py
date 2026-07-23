from typing import Optional

class Customer:
    """Representa a entidade Cliente no sistema."""

    def __init__(
        self,
        id: int,
        nome_razao_social: str,
        cpf_cnpj: str,
        telefone: Optional[str] = None,
        email: Optional[str] = None,
        endereco: Optional[str] = None,
    ):
        self.id = id
        self.nome_razao_social = nome_razao_social
        self.cpf_cnpj = cpf_cnpj
        self.telefone = telefone
        self.email = email
        self.endereco = endereco

    @classmethod
    def from_row(cls, row: dict) -> Optional['Customer']:
        """
        Cria uma instância de Customer a partir de uma linha do banco de dados (dicionário).
        """
        if not row:
            return None
        return cls(**row)