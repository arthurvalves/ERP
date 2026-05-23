import xml.etree.ElementTree as ET
from ..core.validators import validate_nfe_structure
from .events.event_bus import emit


def process_nfe_xml(xml_content: str):
    """Parseia a NF-e e emite evento `NFeImported` com os dados estruturados.

    Payload exemplo:
    {
      'chave': '...',
      'supplier_name': 'Fornecedor',
      'total': 123.0,
      'items': [ { 'cProd': 'SKU', 'xProd': 'Nome', 'qCom': 1, 'vUnCom': 10.0, 'NCM': '...' }, ... ]
    }
    """
    root = ET.fromstring(xml_content)
    validate_nfe_structure(root)
    chave = root.findtext('.//{*}chNFe') or None
    supplier_name = root.findtext('.//{*}emit/{*}xNome') or 'Fornecedor Desconhecido'
    total = float(root.findtext('.//{*}ICMSTot/{*}vNF') or 0)
    items = []
    for det in root.findall('.//{*}det'):
        prod = det.find('.//{*}prod')
        if prod is None:
            continue
        descricao = prod.findtext('{*}xProd') or ''
        q = float(prod.findtext('{*}qCom') or 0)
        v = float(prod.findtext('{*}vUnCom') or prod.findtext('{*}vProd') or 0)
        ncm = prod.findtext('{*}NCM') or prod.findtext('{*}cProd')
        cprod = prod.findtext('{*}cProd') or ''
        items.append({'cProd': cprod, 'xProd': descricao, 'qCom': q, 'vUnCom': v, 'NCM': ncm})

    payload = {'chave': chave, 'supplier_name': supplier_name, 'total': total, 'items': items, 'xml': xml_content}
    try:
        emit('NFeImported', payload)
    except Exception:
        pass
