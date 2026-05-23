"""Script para inicializar o DB e executar um demo de importação NF-e e venda PDV."""
from erp_backend.database.init_db import init_db
from erp_backend.core.nfe_processor import process_nfe_xml
from erp_backend.utils.db import get_connection, fetchone
from erp_backend.services.sales_service import process_sale_transaction
# import handlers to register event subscriptions
import erp_backend.core.events.handlers

SAMPLE_NFE = '''<?xml version="1.0" encoding="UTF-8"?>
<NFe>
  <infNFe>
    <chNFe>12345678901234567890123456789012345678901234</chNFe>
    <emit>
      <xNome>Fornecedor Exemplo LTDA</xNome>
    </emit>
    <det>
      <prod>
        <cProd>SKU123</cProd>
        <xProd>Produto Exemplo A</xProd>
        <NCM>01010101</NCM>
        <qCom>10</qCom>
        <vUnCom>5.5</vUnCom>
      </prod>
    </det>
    <ICMSTot>
      <vNF>55.0</vNF>
    </ICMSTot>
  </infNFe>
</NFe>
'''

def demo():
    db = init_db()
    print('DB inicializado em', db)
    print('Processando NF-e demo...')
    try:
      process_nfe_xml(SAMPLE_NFE)
    except Exception as e:
      print('Processamento NF-e:', e)
    # list products
    conn = get_connection()
    cur = conn.cursor()
    cur.execute('SELECT id, sku, nome, estoque_atual FROM products')
    for row in cur.fetchall():
        print('Produto:', dict(row))
    # create a sale for the product (transactional)
    cur.execute('SELECT id FROM products LIMIT 1')
    r = cur.fetchone()
    if r:
      prod_id = r['id']
      sale_id = process_sale_transaction(None, [{'product_id': prod_id, 'quantidade': 2, 'preco_unitario': 5.5}], 'DINHEIRO')
      print('Venda criada, id=', sale_id)
    conn.close()

if __name__ == '__main__':
    demo()
