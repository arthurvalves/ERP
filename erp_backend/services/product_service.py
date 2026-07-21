from ..models.product import Product
from ..utils.db import fetchone, fetchall, execute, execute_with_conn
from typing import Optional, List
from ..core.normalizer import normalize
from ..utils.audit import log
from ..core.events.event_bus import emit


def create_product(product: Product, conn=None) -> int:
    sql = """
    INSERT INTO products (sku,nome,nome_normalizado,codigo_barras,ncm,referencia,fornecedor_id,categoria_id,custo,margem_padrao,preco_venda,estoque_atual)
    VALUES (?,?,?,?,?,?,?,?,?,?,?,?)
    """
    nome_normalizado = product.nome_normalizado or normalize(product.nome)
    params = (product.sku, product.nome, nome_normalizado, product.codigo_barras, product.ncm, product.referencia, product.fornecedor_id, product.categoria_id, product.custo, product.margem_padrao, product.preco_venda, product.estoque_atual)
    existing = fetchone("SELECT id FROM products WHERE sku = ?", (product.sku,))
    if existing:
        pid = existing["id"]
        update_sql = """
        UPDATE products
           SET nome = ?, nome_normalizado = ?, codigo_barras = COALESCE(codigo_barras, ?),
               ncm = COALESCE(ncm, ?), referencia = COALESCE(referencia, ?),
               fornecedor_id = COALESCE(fornecedor_id, ?), categoria_id = COALESCE(categoria_id, ?),
               custo = CASE WHEN custo = 0 OR custo IS NULL THEN ? ELSE custo END,
               margem_padrao = COALESCE(margem_padrao, ?),
               preco_venda = CASE WHEN preco_venda = 0 OR preco_venda IS NULL THEN ? ELSE preco_venda END
         WHERE id = ?
        """
        update_params = (
            product.nome,
            nome_normalizado,
            product.codigo_barras,
            product.ncm,
            product.referencia,
            product.fornecedor_id,
            product.categoria_id,
            product.custo,
            product.margem_padrao,
            product.preco_venda,
            pid,
        )
        if conn is not None:
            execute_with_conn(conn, update_sql, update_params)
        else:
            execute(update_sql, update_params)
        log('product', pid, 'UPSERT', {'sku': product.sku, 'nome': product.nome}, conn=conn)
        return pid
    if conn is not None:
        pid = execute_with_conn(conn, sql, params)
    else:
        pid = execute(sql, params)
    log('product', pid, 'CREATE', {'sku': product.sku, 'nome': product.nome}, conn=conn)
    try:
        emit('ProductCreated', {'product_id': pid, 'sku': product.sku})
    except Exception:
        pass
    return pid

def get_by_sku(sku: str) -> Optional[Product]:
    row = fetchone("SELECT * FROM products WHERE sku = ?", (sku,))
    if not row:
        return None
    return Product.from_row(row)

def update_stock(product_id: int, delta: float):
    # Direct stock edits are not allowed. Stock is derived from stock_movements.
    raise RuntimeError('Direct stock update is not allowed; use stock movements')

def search_by_barcode(barcode: str) -> Optional[Product]:
    row = fetchone("SELECT * FROM products WHERE codigo_barras = ?", (barcode,))
    if not row:
        return None
    return Product.from_row(row)

def get_purchase_suggestions() -> List[dict]:
    """
    Retorna uma lista de produtos cujo estoque atual está abaixo do estoque mínimo.
    """
    sql = """
        SELECT id, nome, sku, estoque_atual, estoque_minimo, fornecedor_id
        FROM products
        WHERE estoque_minimo > 0 AND estoque_atual <= estoque_minimo
        ORDER BY nome;
    """
    return fetchall(sql)
