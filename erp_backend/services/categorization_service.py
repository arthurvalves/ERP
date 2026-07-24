from typing import Optional, Dict
from ..utils.db import fetchone, execute, execute_with_conn
from ..core.normalizer import normalize
from . import category_service

# Dicionário de fallback para categorizar por palavras-chave no nome do produto.
# As chaves devem estar normalizadas (minúsculas, sem acentos).
KEYWORD_CATEGORY_MAP: Dict[str, str] = {
    "motor": "Motor",
    "oleo": "Lubrificação",
    "filtro de oleo": "Lubrificação",
    "lubrificante": "Lubrificação",
    "ignicao": "Ignição",
    "vela": "Ignição",
    "bomba de combustivel": "Alimentação",
    "bico injetor": "Alimentação",
    "radiador": "Arrefecimento",
    "mangueira": "Arrefecimento",
    "correia": "Transmissão",
    "tensor": "Transmissão",
    "polia": "Transmissão",
    "embreagem": "Transmissão",
    "freio": "Freios",
    "pastilha": "Freios",
    "disco de freio": "Freios",
    "amortecedor": "Suspensão",
    "pivo": "Suspensão",
    "bandeja": "Suspensão",
    "terminal de direcao": "Direção",
    "caixa de direcao": "Direção",
    "roda": "Rodas e Cubos",
    "rolamento": "Rodas e Cubos",
    "bateria": "Sistema Elétrico",
    "alternador": "Sistema Elétrico",
    "farol": "Iluminação",
    "lanterna": "Iluminação",
    "lampada": "Iluminação",
    "sensor": "Sensores e Eletrônica",
    "ar condicionado": "Climatização",
    "parachoque": "Carroceria",
    "parabrisa": "Vidros",
    "limpador": "Limpadores",
    "palheta": "Limpadores",
    "trava": "Fechaduras e Segurança",
    "borracha": "Borrachas e Vedação",
    "parafuso": "Fixação",
    "aditivo": "Fluidos e Produtos Químicos",
}

def guess_category_id(ncm: str, nome_produto: str, conn=None) -> Optional[int]:
    """Tenta adivinhar a categoria de um produto, primeiro por NCM, depois por palavras-chave."""
    # 1. Tenta por prefixo de NCM (do mais específico para o mais genérico)
    if ncm:
        for length in (8, 6, 4, 2):
            prefix = ncm[:length]
            row = fetchone("SELECT categoria_id FROM ncm_category_map WHERE ncm_prefix = ?", (prefix,), conn=conn)
            if row:
                return row['categoria_id']

    # 2. Fallback para palavras-chave no nome do produto
    nome_normalizado = normalize(nome_produto)
    for keyword, category_name in KEYWORD_CATEGORY_MAP.items():
        if keyword in nome_normalizado:
            category = category_service.get_category_by_name(category_name, conn=conn)
            if category:
                return category['id']

    return None

def learn_ncm_category(ncm: str, categoria_id: int, conn=None, prefix_length: int = 6):
    """
    Grava ou atualiza o mapeamento de um prefixo de NCM para uma categoria.
    Usa INSERT OR REPLACE para garantir que o prefixo seja único.
    """
    if not ncm or not categoria_id or len(ncm) < prefix_length:
        return

    ncm_prefix = ncm[:prefix_length]
    sql = "INSERT OR REPLACE INTO ncm_category_map (ncm_prefix, categoria_id) VALUES (?, ?)"
    execute(sql, (ncm_prefix, categoria_id), conn=conn)