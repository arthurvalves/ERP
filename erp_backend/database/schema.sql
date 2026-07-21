-- Schema for mini ERP
PRAGMA foreign_keys = ON;

CREATE TABLE IF NOT EXISTS categories (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    nome TEXT NOT NULL,
    margem_padrao REAL DEFAULT 0
);

CREATE TABLE IF NOT EXISTS suppliers (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    razao_social TEXT,
    cnpj TEXT,
    ie TEXT,
    endereco TEXT,
    cidade TEXT,
    uf TEXT
);

CREATE TABLE IF NOT EXISTS customers (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    nome_razao_social TEXT,
    cpf_cnpj TEXT,
    telefone TEXT,
    email TEXT,
    endereco TEXT
);

CREATE TABLE IF NOT EXISTS products (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    sku TEXT NOT NULL UNIQUE,
    nome TEXT,
    nome_normalizado TEXT,
    codigo_barras TEXT,
    ncm TEXT,
    referencia TEXT,
    fornecedor_id INTEGER,
    categoria_id INTEGER,
    custo REAL DEFAULT 0,
    margem_padrao REAL DEFAULT 0,
    preco_venda REAL DEFAULT 0,
    estoque_atual REAL DEFAULT 0,
    FOREIGN KEY(fornecedor_id) REFERENCES suppliers(id),
    FOREIGN KEY(categoria_id) REFERENCES categories(id)
);

CREATE TABLE IF NOT EXISTS stock_movements (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    product_id INTEGER,
    tipo TEXT,
    quantidade REAL,
    custo_unitario REAL,
    origem TEXT,
    referencia_id INTEGER,
    data TEXT DEFAULT (datetime('now')),
    FOREIGN KEY(product_id) REFERENCES products(id)
);

CREATE TABLE IF NOT EXISTS purchases (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    chave_acesso TEXT UNIQUE,
    supplier_id INTEGER,
    valor_total REAL,
    data_emissao TEXT,
    FOREIGN KEY(supplier_id) REFERENCES suppliers(id)
);

CREATE TABLE IF NOT EXISTS purchase_items (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    purchase_id INTEGER,
    product_id INTEGER,
    descricao_xml TEXT,
    quantidade REAL,
    valor_unitario REAL,
    ncm TEXT,
    FOREIGN KEY(purchase_id) REFERENCES purchases(id),
    FOREIGN KEY(product_id) REFERENCES products(id)
);

CREATE TABLE IF NOT EXISTS sales (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    customer_id INTEGER,
    total REAL,
    desconto_total REAL,
    forma_pagamento TEXT,
    data TEXT DEFAULT (datetime('now')),
    FOREIGN KEY(customer_id) REFERENCES customers(id)
);

CREATE TABLE IF NOT EXISTS sales_items (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    sale_id INTEGER,
    product_id INTEGER,
    quantidade REAL,
    preco_unitario REAL,
    desconto_item REAL,
    FOREIGN KEY(sale_id) REFERENCES sales(id),
    FOREIGN KEY(product_id) REFERENCES products(id)
);

CREATE TABLE IF NOT EXISTS audit_log (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    entidade TEXT,
    entidade_id INTEGER,
    acao TEXT,
    origem TEXT,
    payload TEXT,
    before_payload TEXT,
    after_payload TEXT,
    data TEXT DEFAULT (datetime('now'))
);

CREATE TABLE IF NOT EXISTS product_price_history (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    product_id INTEGER,
    old_price REAL,
    new_price REAL,
    change_type TEXT,
    date TEXT DEFAULT (datetime('now')),
    FOREIGN KEY(product_id) REFERENCES products(id)
);

CREATE TABLE IF NOT EXISTS product_cost_history (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    product_id INTEGER,
    old_cost REAL,
    new_cost REAL,
    supplier_id INTEGER,
    nf_e_id INTEGER,
    date TEXT DEFAULT (datetime('now')),
    FOREIGN KEY(product_id) REFERENCES products(id),
    FOREIGN KEY(supplier_id) REFERENCES suppliers(id),
    FOREIGN KEY(nf_e_id) REFERENCES purchases(id)
);