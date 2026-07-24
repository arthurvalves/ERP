import unicodedata
import re

def normalize(text: str) -> str:
    if text is None:
        return ''
    text = text.lower()
    text = ''.join(c for c in unicodedata.normalize('NFKD', text) if not unicodedata.combining(c))
    text = re.sub(r'[^a-z0-9]+', ' ', text)
    return text.strip()
