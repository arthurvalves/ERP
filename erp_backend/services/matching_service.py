from ..models.product import Product
from ..services.product_service import search_by_barcode
from ..core.normalizer import normalize
from typing import Optional
import difflib
from ..utils.db import fetchall

# simple in-memory cache for normalized product names -> list of products
_cache = {}

def match_product_by_barcode(barcode: str) -> Optional[Product]:
    return search_by_barcode(barcode)

def _load_candidates():
    rows = fetchall('SELECT * FROM products')
    return [dict(r) for r in rows]

def fuzzy_match_by_name(name: str, min_score: float = 0.85) -> Optional[Product]:
    target = normalize(name)
    if target in _cache:
        candidates = _cache[target]
    else:
        candidates = _load_candidates()
        _cache[target] = candidates

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

