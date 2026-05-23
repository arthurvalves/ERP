from typing import Dict, List

def validate_nfe_structure(root) -> None:
    # minimal structural checks
    chave = root.findtext('.//chNFe')
    if not chave:
        raise ValueError('Chave de acesso ausente na NF-e')

def validate_sale_items(items: List[Dict]) -> None:
    if not items:
        raise ValueError('Carrinho vazio')
    for it in items:
        if it.get('quantidade', 0) <= 0:
            raise ValueError('Quantidade inválida em item')

def validate_product_data(data: Dict) -> None:
    if not data.get('sku'):
        raise ValueError('SKU obrigatório')
