import json
from .db import execute, execute_with_conn

def log(entidade: str, entidade_id: int, acao: str, payload: dict, origem: str = None, before: dict = None, after: dict = None, conn=None):
    payload_s = json.dumps(payload, ensure_ascii=False)
    before_s = json.dumps(before, ensure_ascii=False) if before is not None else None
    after_s = json.dumps(after, ensure_ascii=False) if after is not None else None
    sql = "INSERT INTO audit_log (entidade, entidade_id, acao, origem, payload, before_payload, after_payload) VALUES (?,?,?,?,?,?,?)"
    params = (entidade, entidade_id, acao, origem, payload_s, before_s, after_s)
    if conn is not None:
        return execute_with_conn(conn, sql, params)
    return execute(sql, params)
