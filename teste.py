import os
from erp_backend.core.nfe_processor import process_nfe_xml
from erp_backend.utils.db import get_connection

def run_test():
    # Caminho para o ficheiro XML existente no projeto
    xml_path = "27260542580092007502551100000421951686523560-nfe.xml"
    
    if not os.path.exists(xml_path):
        print(f"Erro: Ficheiro {xml_path} não encontrado.")
        return

    print("1. A ler o ficheiro XML...")
    with open(xml_path, 'r', encoding='utf-8') as f:
        xml_content = f.read()

    print("2. A processar a NF-e através do novo pipeline unificado...")
    try:
        resultado = process_nfe_xml(xml_content)
        print(f"✅ Sucesso! Resultado retornado: {resultado}")
    except Exception as e:
        print(f"❌ Erro durante o processamento: {e}")
        return

    print("\n3. A verificar a Base de Dados...")
    conn = get_connection()
    # Usa dicionários para facilitar a leitura dos resultados
    conn.row_factory = lambda c, r: dict(zip([col[0] for col in c.description], r))
    cur = conn.cursor()

    chave = resultado.get('chave')
    
    # Verificar Compra
    compra = cur.execute("SELECT * FROM purchases WHERE chave_acesso = ?", (chave,)).fetchone()
    print(f"\n--- Tabela PURCHASES ---")
    print(compra)

    if compra:
        # Verificar Itens da Compra
        itens = cur.execute("SELECT product_id, quantidade, valor_unitario FROM purchase_items WHERE purchase_id = ?", (compra['id'],)).fetchall()
        print(f"\n--- Tabela PURCHASE_ITEMS ({len(itens)} itens inseridos) ---")
        for item in itens:
            print(item)

        # Verificar Stock (Apenas a última movimentação)
        stock = cur.execute("SELECT * FROM stock_movements WHERE referencia_id = ? ORDER BY id DESC LIMIT 1", (compra['id'],)).fetchone()
        print(f"\n--- Tabela STOCK_MOVEMENTS (Amostra) ---")
        print(stock)

    conn.close()

if __name__ == "__main__":
    run_test()