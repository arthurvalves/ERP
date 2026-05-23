from ..normalizer import normalize

def semantic_normalize(name: str) -> str:
    # remove common noise tokens
    s = normalize(name)
    tokens = [t for t in s.split() if t not in ('und','bivolt','12v')]
    return ' '.join(tokens)
