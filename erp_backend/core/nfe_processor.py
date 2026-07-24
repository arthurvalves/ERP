import json
import sqlite3
from erp_backend.utils.db import get_connection
from erp_backend.core.nfe.nfe_xml_parser import parse_nfe_xml
from erp_backend.services.matching_service import find_product_match
from erp_backend.services import categorization_service
from erp_backend.services.stock_service import record_movement
from erp_backend.core.events.event_bus import emit

def normalize_string(s: str) -> str:
    """Normaliza strings para auxiliar no matching de produtos."""
    return s.strip().upper() if s else ""

def process_nfe_xml(xml_content: str):
    """Processa XML da NF-e com matching de produtos, movimentação de estoque, e auditoria completa."""
    nfe_data = parse_nfe_xml(xml_content)
    chave = nfe_data['header']['chave_acesso']
    
    if not chave:
        raise ValueError("XML inválido: Chave de acesso ausente.")

    conn = get_connection()
    # Garantir que os resultados permitam acesso como dicionário para o matching
    conn.row_factory = sqlite3.Row
    cur = conn.cursor()

    try:
        # 1. IDEMPOTÊNCIA: Verifica se a NF-e já foi importada
        cur.execute("SELECT id FROM purchases WHERE chave_acesso = ?", (chave,))
        if cur.fetchone():
            cur.execute("""
                INSERT INTO audit_log (entidade, acao, origem, payload)
                VALUES ('nfe', 'tentativa_duplicada', 'nfe_xml_import', ?)
            """, (json.dumps({"chave": chave}),))
            conn.commit()
            return {"status": "ignored", "reason": "duplicate", "chave": chave}

        # 2. FORNECEDOR (EMITENTE)
        cnpj = nfe_data['supplier']['cnpj']
        cur.execute("SELECT id FROM suppliers WHERE cnpj = ?", (cnpj,))
        sup = cur.fetchone()
        
        if sup:
            supplier_id = sup['id']
            cur.execute("""
                INSERT INTO audit_log (entidade, entidade_id, acao, origem, payload)
                VALUES ('supplier', ?, 'update', 'nfe_xml_import', ?)
            """, (supplier_id, json.dumps({"cnpj": cnpj})))
        else:
            addr = f"{nfe_data['supplier']['rua']}, {nfe_data['supplier']['numero']} - {nfe_data['supplier']['bairro']}"
            cur.execute("""
                INSERT INTO suppliers (razao_social, cnpj, ie, endereco, cidade, uf)
                VALUES (?, ?, ?, ?, ?, ?)
            """, (nfe_data['supplier']['razao_social'], cnpj, nfe_data['supplier']['ie'],
                  addr, nfe_data['supplier']['cidade'], nfe_data['supplier']['uf']))
            supplier_id = cur.lastrowid
            
            cur.execute("""
                INSERT INTO audit_log (entidade, entidade_id, acao, origem, payload)
                VALUES ('supplier', ?, 'create', 'nfe_xml_import', ?)
            """, (supplier_id, json.dumps({"cnpj": cnpj})))

        # 3. REGISTRO DE COMPRA (Criado antes para gerar ID de referência)
        cur.execute("""
            INSERT INTO purchases (chave_acesso, supplier_id, valor_total, data_emissao)
            VALUES (?, ?, ?, ?)
        """, (chave, supplier_id, nfe_data['header']['valor_total'], nfe_data['header']['data_emissao']))
        purchase_id = cur.lastrowid

        # 4. MATCHING DE PRODUTOS
        # Cache temporário para reduzir acessos sequenciais ao banco
        cur.execute("SELECT id, nome_normalizado, codigo_barras, ncm, referencia, fornecedor_id, custo, estoque_atual, categoria_id FROM products")
        all_products = [dict(row) for row in cur.fetchall()]

        for item in nfe_data['items']:
            match_result = find_product_match(item, all_products, supplier_id)
            matched_product = match_result['product'] if match_result['confidence'] >= 85 else None

            # 5. CRIAÇÃO OU ATUALIZAÇÃO DO PRODUTO
            if not matched_product:
                sku = f"SKU-{chave[-6:]}-{item['cProd']}"
                nome = item['xProd']
                nome_norm = normalize_string(nome)
                # CORREÇÃO: A variável 'ean' não estava definida neste escopo.
                ean = item.get('cEAN')
                if ean and 'SEM GTIN' in ean.upper(): ean = None
                
                # Tenta adivinhar a categoria antes de criar o produto
                categoria_id = categorization_service.guess_category_id(item['NCM'], item['xProd'], conn=conn)

                cur.execute("""
                    INSERT INTO products (sku, nome, nome_normalizado, codigo_barras, ncm, referencia, fornecedor_id, categoria_id, custo, estoque_atual, cfop_padrao)
                    VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, 0, ?)
                """, (sku, nome, nome_norm, ean, item['NCM'], item['cProd'], supplier_id, categoria_id, item['vUnCom'], item.get('CFOP', '')))
                product_id = cur.lastrowid
                old_stock = 0
                old_cost = 0.0

                audit_payload = {"sku": sku, "nome": nome, "categoria_id": categoria_id, "fonte_categoria": "auto"}
                cur.execute("""
                    INSERT INTO audit_log (entidade, entidade_id, acao, origem, payload)
                    VALUES ('product', ?, 'create', 'nfe_xml_import', ?)
                """, (product_id, json.dumps(audit_payload)))
            else:
                product_id = matched_product['id']
                old_cost = matched_product['custo']
                old_stock = matched_product['estoque_atual']
                new_cost = item['vUnCom']
                
                cur.execute("UPDATE products SET custo = ? WHERE id = ?", (new_cost, product_id))

                # NOVO: se o produto ainda não tem categoria, tenta adivinhar agora
                if not matched_product.get('categoria_id'):
                    categoria_guess = categorization_service.guess_category_id(item['NCM'], item['xProd'], conn=conn)
                    if categoria_guess:
                        cur.execute("UPDATE products SET categoria_id = ? WHERE id = ?", (categoria_guess, product_id))
                        cur.execute("""
                            INSERT INTO audit_log (entidade, entidade_id, acao, origem, payload)
                            VALUES ('product', ?, 'update_categoria', 'nfe_xml_import', ?)
                        """, (product_id, json.dumps({"categoria_id": categoria_guess, "fonte_categoria": "auto"})))
                
                cur.execute("""
                    INSERT INTO audit_log (entidade, entidade_id, acao, origem, before_payload, after_payload)
                    VALUES ('product', ?, 'update_cost', 'nfe_xml_import', ?, ?)
                """, (product_id, json.dumps({"custo": old_cost}), json.dumps({"custo": new_cost})))

                # Histórico de Custo
                if old_cost != new_cost:
                    cur.execute("""
                        INSERT INTO product_cost_history (product_id, old_cost, new_cost, supplier_id, nf_e_id)
                        VALUES (?, ?, ?, ?, ?)
                    """, (product_id, old_cost, new_cost, supplier_id, purchase_id))

            # 6. MOVIMENTAÇÃO DE ESTOQUE (Centralizada via stock_service)
            qtd = item['qCom']
            record_movement(product_id, 'entrada', qtd, item['vUnCom'], 'NF-e', purchase_id, conn=conn)

            cur.execute("""
                INSERT INTO audit_log (entidade, entidade_id, acao, origem, before_payload, after_payload)
                VALUES ('stock', ?, 'add', 'nfe_xml_import', ?, ?)
            """, (product_id, json.dumps({"estoque_atual": old_stock}), json.dumps({"estoque_atual": old_stock + qtd})))

            # 7. REGISTRO DOS ITENS DA COMPRA
            cur.execute("""
                INSERT INTO purchase_items (purchase_id, product_id, descricao_xml, quantidade, valor_unitario, ncm)
                VALUES (?, ?, ?, ?, ?, ?)
            """, (purchase_id, product_id, item['xProd'], qtd, item['vUnCom'], item['NCM']))

        conn.commit()
        
        # 8. DISPARO DE EVENTOS DESACOPLADOS
        # Notifica o sistema de que a nota foi importada com sucesso (útil para atualizar UI ou enviar e-mails)
        emit('NFeImported', {"chave_acesso": chave, "purchase_id": purchase_id})

        return {"status": "success", "chave": chave, "purchase_id": purchase_id}

    finally:
        if conn:
            conn.close()