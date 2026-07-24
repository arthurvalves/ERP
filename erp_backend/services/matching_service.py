from ..models.product import Product
from ..services.product_service import search_by_barcode
from ..core.normalizer import normalize
from typing import Optional, List, Dict, Any
import difflib
from ..utils.db import fetchall

# simple in-memory cache for normalized product names -> list of products
_product_cache = []

def match_product_by_barcode(barcode: str) -> Optional[Product]:
    return search_by_barcode(barcode)

def _load_candidates():
    rows = fetchall('SELECT * FROM products')
    return [dict(r) for r in rows]

def fuzzy_match_by_name(name: str, min_score: float = 0.85) -> Optional[Product]:
    global _product_cache
    target = normalize(name)
    if not _product_cache:
        candidates = _load_candidates()
        _product_cache = candidates
    else:
        candidates = _product_cache

    best = None
    best_score = 0.0
    for c in candidates:
        cand_name = (c.get('nome_normalizado') or '').lower()
        score = difflib.SequenceMatcher(None, target, cand_name).ratio()
        if score > best_score:
            best_score = score
            best = c
    if best and best_score >= min_score:
        return Product.from_row(best)
    return None

def find_product_match(item_data: Dict[str, Any], all_products: List[Dict[str, Any]], supplier_id: Optional[int]) -> Dict[str, Any]:
    """
    Centralized function to find a product match for an NFe item.
    Returns a dictionary with 'product', 'confidence', and 'match_type'.
    """
    ean = item_data.get('cEAN')
    if ean and 'SEM GTIN' in ean.upper():
        ean = None

    # 1. Match by EAN (Barcode)
    if ean:
        product = next((p for p in all_products if p.get('codigo_barras') == ean), None)
        if product:
            return {'product': product, 'confidence': 100, 'match_type': 'ean'}

    # 2. Match by Supplier + Reference Code (SKU)
    if supplier_id:
        product = next((p for p in all_products if p.get('fornecedor_id') == supplier_id and p.get('referencia') == item_data.get('cProd')), None)
        if product:
            return {'product': product, 'confidence': 100, 'match_type': 'supplier_ref'}

    # 3. Fuzzy Match by Name
    item_name_norm = normalize(item_data.get('xProd', ''))
    best_ratio, best_match = 0, None
    for p in all_products:
        if p.get('nome_normalizado'):
            ratio = difflib.SequenceMatcher(None, item_name_norm, p['nome_normalizado']).ratio()
            if ratio > best_ratio:
                best_ratio, best_match = ratio, p
    
    return {'product': best_match, 'confidence': int(best_ratio * 100), 'match_type': 'fuzzy_name'}
