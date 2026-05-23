from .event_bus import subscribe
from ..stock_reconciliation import recompute_stock
from ...services.purchase_service import register_purchase, add_purchase_item
from ...services.product_service import create_product, get_by_sku
from ...services.matching_service import fuzzy_match_by_name, match_product_by_barcode
from ...core.normalizer import normalize
from ...utils.db import transaction
from ...utils.audit import log
from ...services.history_service import log_cost_change, log_price_change
from ...services.pricing_service import calculate_price
from ...core.events.event_bus import emit


def _handle_nfe_imported(payload: dict):
    # payload contains chave, supplier_name, total, items, xml
    chave = payload.get('chave')
    supplier_name = payload.get('supplier_name')
    total = payload.get('total')
    items = payload.get('items', [])

    with transaction() as conn:
        # supplier
        cur = conn.cursor()
        cur.execute('SELECT id FROM suppliers WHERE razao_social = ?', (supplier_name,))
        row = cur.fetchone()
        if row:
            supplier_id = row[0]
        else:
            supplier_id = conn.execute('INSERT INTO suppliers (razao_social) VALUES (?)', (supplier_name,)).lastrowid

        # idempotency
        existing = conn.execute('SELECT id FROM purchases WHERE chave_acesso = ?', (chave,)).fetchone()
        if existing:
            raise ValueError('NF-e já processada (handler)')

        purchase_id = register_purchase(chave, supplier_id, total, conn=conn)

        for it in items:
            sku = (it.get('cProd') or it.get('xProd'))[:40]
            prod = get_by_sku(sku)
            # try barcode match first
            if not prod and it.get('codigo_barras'):
                prod = match_product_by_barcode(it.get('codigo_barras'))
            if not prod:
                prod = fuzzy_match_by_name(it.get('xProd'))
            if prod:
                prod_id = prod.id
                # update cost history if cost changes
                old_cost_row = conn.execute('SELECT custo FROM products WHERE id = ?', (prod_id,)).fetchone()
                old_cost = old_cost_row[0] if old_cost_row else None
                if old_cost is None or old_cost != it.get('vUnCom'):
                    log_cost_change(prod_id, old_cost, it.get('vUnCom'), supplier_id, purchase_id, conn=conn)
                    # update cost
                    conn.execute('UPDATE products SET custo = ? WHERE id = ?', (it.get('vUnCom'), prod_id))
                    # recalculate price using existing margem_padrao
                    row = conn.execute('SELECT margem_padrao, custo, preco_venda FROM products WHERE id = ?', (prod_id,)).fetchone()
                    margem = row[0] or 0
                    new_price = calculate_price(it.get('vUnCom') or 0, margem)
                    old_price = row[2]
                    if old_price != new_price:
                        conn.execute('UPDATE products SET preco_venda = ? WHERE id = ?', (new_price, prod_id))
                        log_price_change(prod_id, old_price, new_price, 'nf-e', conn=conn)
                        try:
                            emit('PriceUpdated', {'product_id': prod_id, 'old_price': old_price, 'new_price': new_price})
                        except Exception:
                            pass
            else:
                # create new product
                nome = it.get('xProd')
                nome_norm = normalize(nome)
                from ...models.product import Product
                p = Product(id=None, sku=sku, nome=nome, nome_normalizado=nome_norm, codigo_barras=None, ncm=it.get('NCM'), referencia=None, fornecedor_id=supplier_id, categoria_id=None, custo=it.get('vUnCom') or 0, margem_padrao=0, preco_venda=it.get('vUnCom') or 0, estoque_atual=0)
                prod_id = create_product(p, conn=conn)
                log_price_change(prod_id, None, p.preco_venda, 'nf-e', conn=conn)
                try:
                    emit('PriceUpdated', {'product_id': prod_id, 'old_price': None, 'new_price': p.preco_venda})
                except Exception:
                    pass

            add_purchase_item(purchase_id, prod_id, it.get('xProd'), it.get('qCom'), it.get('vUnCom'), it.get('NCM'), conn=conn)
        # recompute stock for affected products
        for it in items:
            # best-effort get product id
            sku = (it.get('cProd') or it.get('xProd'))[:40]
            row = conn.execute('SELECT id FROM products WHERE sku = ?', (sku,)).fetchone()
            if row:
                recompute_stock(row[0], conn=conn)

        log('nfe_event_handler', purchase_id, 'PROCESS', {'chave': chave}, origem='NFeImported', conn=conn)


subscribe('NFeImported', _handle_nfe_imported)
