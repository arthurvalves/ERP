import sqlite3
from erp_backend.utils.db import get_connection

def run_autocenter_migrations():
    conn = get_connection()
    cur = conn.cursor()
    
    # 1. Adicionar novos campos na tabela de produtos
    colunas_produtos = [
        ("cfop_padrao", "TEXT DEFAULT ''"),
        ("preco_atacado", "REAL DEFAULT 0.0"),
        ("is_servico", "INTEGER DEFAULT 0") # 0 = Peça/Produto, 1 = Mão de Obra/Serviço
    ]
    
    for col, tipo in colunas_produtos:
        try:
            cur.execute(f"ALTER TABLE products ADD COLUMN {col} {tipo};")
        except sqlite3.OperationalError:
            pass # Coluna já existe
            
    # 2. Tabela de Orçamentos (Pré-venda AutoCenter)
    cur.execute('''
        CREATE TABLE IF NOT EXISTS quotes (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            customer_id INTEGER,
            placa TEXT,
            total REAL DEFAULT 0.0,
            status TEXT DEFAULT 'pendente',
            data_criacao DATETIME DEFAULT CURRENT_TIMESTAMP
        )
    ''')
    
    cur.execute('''
        CREATE TABLE IF NOT EXISTS quote_items (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            quote_id INTEGER,
            product_id INTEGER,
            quantidade REAL,
            preco_unitario REAL,
            desconto_item REAL DEFAULT 0.0,
            FOREIGN KEY(quote_id) REFERENCES quotes(id)
        )
    ''')
    
    # 3. Tabela de Ordens de Serviço (OS)
    cur.execute('''
        CREATE TABLE IF NOT EXISTS service_orders (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            customer_id INTEGER,
            veiculo TEXT,
            placa TEXT,
            descricao_problema TEXT,
            status TEXT DEFAULT 'aberta',
            total_pecas REAL DEFAULT 0.0,
            total_servicos REAL DEFAULT 0.0,
            total_geral REAL DEFAULT 0.0,
            data_abertura DATETIME DEFAULT CURRENT_TIMESTAMP,
            data_fechamento DATETIME
        )
    ''')
    
    cur.execute('''
        CREATE TABLE IF NOT EXISTS service_order_items (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            service_order_id INTEGER,
            product_id INTEGER,
            tipo TEXT,
            quantidade REAL,
            preco_unitario REAL,
            desconto_item REAL DEFAULT 0.0,
            FOREIGN KEY(service_order_id) REFERENCES service_orders(id)
        )
    ''')
    
    conn.commit()
    conn.close()