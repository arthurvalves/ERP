from ..models.product import Product
from ..utils.db import fetchone, fetchall, execute
from typing import Optional, List
from ..core.normalizer import normalize
from ..utils.audit import log
from ..core.events.event_bus import emit


def create_product(product: Product) -> int:
    sql = """
    INSERT INTO products (sku,nome,nome_normalizado,codigo_barras,ncm,referencia,fornecedor_id,categoria_id,custo,margem_padrao,preco_venda,estoque_atual)
    VALUES (?,?,?,?,?,?,?,?,?,?,?,?)
    """
    nome_normalizado = product.nome_normalizado or normalize(product.nome)
    params = (product.sku, product.nome, nome_normalizado, product.codigo_barras, product.ncm, product.referencia, product.fornecedor_id, product.categoria_id, product.custo, product.margem_padrao, product.preco_venda, product.estoque_atual)
    pid = execute(sql, params)
    log('product', pid, 'CREATE', {'sku': product.sku, 'nome': product.nome})
    try:
        emit('ProductCreated', {'product_id': pid, 'sku': product.sku})
    except Exception:
        pass
    return pid

def get_by_sku(sku: str) -> Optional[Product]:
    row = fetchone("SELECT * FROM products WHERE sku = ?", (sku,))
    if not row:
        return None
    return Product(**row)

def update_stock(product_id: int, delta: float):
    # Direct stock edits are not allowed. Stock is derived from stock_movements.
    raise RuntimeError('Direct stock update is not allowed; use stock movements')

def search_by_barcode(barcode: str) -> Optional[Product]:
    row = fetchone("SELECT * FROM products WHERE codigo_barras = ?", (barcode,))
    if not row:
        return None
    return Product(**row)
