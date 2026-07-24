import xml.etree.ElementTree as ET
from typing import Dict, Any

def parse_nfe_xml(xml_content: str) -> Dict[str, Any]:
    """Lê uma string XML de NF-e e retorna um dicionário com os dados estruturados."""
    root = ET.fromstring(xml_content)
    
    # O uso de {*} ignora o namespace, o que torna o parser resiliente a diferentes versões de XML SEFAZ
    chave = root.findtext('.//{*}chNFe')
    numero = root.findtext('.//{*}nNF')
    serie = root.findtext('.//{*}serie')
    data_emissao = root.findtext('.//{*}dhEmi')
    valor_total = float(root.findtext('.//{*}vNF') or 0.0)
    natureza = root.findtext('.//{*}natOp')
    tipo = root.findtext('.//{*}tpNF')

    # Dados do Fornecedor (Emitente)
    supplier = {
        'cnpj': root.findtext('.//{*}emit/{*}CNPJ'),
        'razao_social': root.findtext('.//{*}emit/{*}xNome'),
        'nome_fantasia': root.findtext('.//{*}emit/{*}xFant'),
        'ie': root.findtext('.//{*}emit/{*}IE'),
        'rua': root.findtext('.//{*}emit/{*}enderEmit/{*}xLgr'),
        'numero': root.findtext('.//{*}emit/{*}enderEmit/{*}nro'),
        'bairro': root.findtext('.//{*}emit/{*}enderEmit/{*}xBairro'),
        'cidade': root.findtext('.//{*}emit/{*}enderEmit/{*}xMun'),
        'uf': root.findtext('.//{*}emit/{*}enderEmit/{*}UF'),
        'cep': root.findtext('.//{*}emit/{*}enderEmit/{*}CEP'),
    }

    # Itens da NF-e
    items = []
    for det in root.findall('.//{*}det'):
        prod = det.find('.//{*}prod')
        if prod is not None:
            items.append({
                'cProd': prod.findtext('.//{*}cProd'),
                'xProd': prod.findtext('.//{*}xProd'),
                'cEAN': prod.findtext('.//{*}cEAN'),
                'cEANTrib': prod.findtext('.//{*}cEANTrib'),
                'NCM': prod.findtext('.//{*}NCM'),
                'CFOP': prod.findtext('.//{*}CFOP'),
                'uCom': prod.findtext('.//{*}uCom'),
                'qCom': float(prod.findtext('.//{*}qCom') or 0.0),
                'vUnCom': float(prod.findtext('.//{*}vUnCom') or 0.0),
                'vProd': float(prod.findtext('.//{*}vProd') or 0.0),
            })

    return {
        'header': {'chave_acesso': chave, 'numero': numero, 'serie': serie, 'data_emissao': data_emissao, 'valor_total': valor_total, 'natureza_operacao': natureza, 'tipo': tipo},
        'supplier': supplier,
        'items': items
    }