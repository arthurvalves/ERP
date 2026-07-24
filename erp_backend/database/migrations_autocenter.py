import sqlite3
from erp_backend.utils.db import get_connection

def run_autocenter_migrations():
    # NOTA: A remoção da coluna 'is_servico' não é suportada nativamente pelo ALTER TABLE do SQLite.
    # Em um ambiente de produção real, seria necessário um processo de migração de dados mais complexo.
    # Para este projeto, assumimos que uma nova base de dados ou uma recriação da tabela products é aceitável.
    conn = get_connection()
    cur = conn.cursor()
    
    # 1. Adicionar novos campos na tabela de produtos
    colunas_produtos = [
        ("cfop_padrao", "TEXT DEFAULT ''"),
        ("preco_atacado", "REAL DEFAULT 0.0"),
        ("estoque_minimo", "REAL DEFAULT 0.0"),
        ("estoque_maximo", "REAL DEFAULT 0.0"),
        ("is_servico", "INTEGER DEFAULT 0"),
    ]
    
    for col, tipo in colunas_produtos:
        try:
            cur.execute(f"ALTER TABLE products ADD COLUMN {col} {tipo};")
        except sqlite3.OperationalError:
            pass # Coluna já existe

    # Tabela de mapeamento NCM -> Categoria para auto-classificação
    cur.execute('''
        CREATE TABLE IF NOT EXISTS ncm_category_map (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            ncm_prefix TEXT NOT NULL UNIQUE,
            categoria_id INTEGER NOT NULL,
            FOREIGN KEY(categoria_id) REFERENCES categories(id)
        );
    ''')

    # 8. Tabela de Catálogo de Serviços
    cur.execute('''
        CREATE TABLE IF NOT EXISTS services (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            name TEXT NOT NULL UNIQUE,
            sku TEXT UNIQUE,
            description TEXT,
            standard_price REAL DEFAULT 0.0,
            category TEXT,
            standard_duration_minutes INTEGER
        )
    ''')

            
    # 2. Tabela de Orçamentos (Pré-venda AutoCenter)
    cur.execute('''
        CREATE TABLE IF NOT EXISTS quotes (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            vehicle_id INTEGER,
            customer_id INTEGER,
            total REAL DEFAULT 0.0,
            status TEXT DEFAULT 'pendente',
            data_criacao DATETIME DEFAULT CURRENT_TIMESTAMP,
            FOREIGN KEY(customer_id) REFERENCES customers(id),
            FOREIGN KEY(vehicle_id) REFERENCES vehicles(id)
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

    # Adiciona a coluna vehicle_id na tabela de orçamentos, se não existir
    try:
        cur.execute("ALTER TABLE quotes ADD COLUMN vehicle_id INTEGER REFERENCES vehicles(id)")
    except sqlite3.OperationalError:
        pass # Coluna já existe
    
    # 3. Tabela de Ordens de Serviço (OS)
    cur.execute('''
        CREATE TABLE IF NOT EXISTS service_orders (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            vehicle_id INTEGER,
            customer_id INTEGER,
            veiculo TEXT,
            placa TEXT,
            descricao_problema TEXT,
            status TEXT DEFAULT 'aberta',
            total_pecas REAL DEFAULT 0.0,
            total_servicos REAL DEFAULT 0.0,
            total_geral REAL DEFAULT 0.0,
            data_abertura DATETIME DEFAULT CURRENT_TIMESTAMP,
            data_fechamento DATETIME,
            scheduled_start_time DATETIME,
            scheduled_end_time DATETIME
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
            technician_id INTEGER,
            FOREIGN KEY(service_order_id) REFERENCES service_orders(id),
            FOREIGN KEY(technician_id) REFERENCES users(id)
        )
    ''')

    # Adiciona a coluna vehicle_id na OS, se não existir
    try:
        cur.execute("ALTER TABLE service_orders ADD COLUMN vehicle_id INTEGER REFERENCES vehicles(id)")
    except sqlite3.OperationalError:
        pass # Coluna já existe

    # Adiciona colunas de agendamento na OS, se não existirem
    try:
        cur.execute("ALTER TABLE service_orders ADD COLUMN scheduled_start_time DATETIME")
        cur.execute("ALTER TABLE service_orders ADD COLUMN scheduled_end_time DATETIME")
    except sqlite3.OperationalError:
        pass # Colunas já existem

    # Adiciona a coluna technician_id na tabela de itens da OS, se não existir
    try:
        cur.execute("ALTER TABLE service_order_items ADD COLUMN technician_id INTEGER REFERENCES users(id)")
    except sqlite3.OperationalError:
        pass # Coluna já existe

    # 4. Tabela de Veículos (essencial para Autocenter)
    cur.execute('''
        CREATE TABLE IF NOT EXISTS vehicles (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            customer_id INTEGER NOT NULL,
            plate TEXT NOT NULL UNIQUE,
            brand TEXT,
            model TEXT,
            year INTEGER,
            color TEXT,
            vin TEXT, -- Chassi
            current_km INTEGER,
            FOREIGN KEY(customer_id) REFERENCES customers(id)
        )
    ''')

    # Adiciona a coluna current_km na tabela de veículos, se não existir
    try:
        cur.execute("ALTER TABLE vehicles ADD COLUMN current_km INTEGER")
    except sqlite3.OperationalError:
        pass # Coluna já existe
    try:
        cur.execute("ALTER TABLE vehicles ADD COLUMN color TEXT")
        cur.execute("ALTER TABLE vehicles ADD COLUMN vin TEXT")
    except sqlite3.OperationalError:
        pass # Coluna já existe

    # 5. Tabela de Usuários e Permissões
    cur.execute('''
        CREATE TABLE IF NOT EXISTS users (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            username TEXT NOT NULL UNIQUE,
            password_hash TEXT NOT NULL,
            profile TEXT NOT NULL CHECK(profile IN ('gerente', 'caixa', 'mecanico'))
        )
    ''')

    # Insere um usuário 'admin' padrão se a tabela estiver vazia
    cur.execute("SELECT COUNT(id) FROM users")
    if cur.fetchone()[0] == 0:
        from erp_backend.services.auth_service import hash_password
        admin_pass_hash = hash_password('admin')
        cur.execute("INSERT INTO users (username, password_hash, profile) VALUES (?, ?, ?)",
                    ('admin', admin_pass_hash, 'gerente'))

    # 6. Tabelas de Controle de Caixa (PDV)
    cur.execute('''
        CREATE TABLE IF NOT EXISTS cash_sessions (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            user_id INTEGER NOT NULL,
            start_time DATETIME DEFAULT CURRENT_TIMESTAMP,
            end_time DATETIME,
            initial_balance REAL NOT NULL,
            final_balance_calculated REAL,
            final_balance_counted REAL,
            difference REAL,
            status TEXT NOT NULL CHECK(status IN ('open', 'closed')),
            FOREIGN KEY(user_id) REFERENCES users(id)
        )
    ''')

    cur.execute('''
        CREATE TABLE IF NOT EXISTS cash_movements (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            session_id INTEGER NOT NULL,
            user_id INTEGER NOT NULL,
            type TEXT NOT NULL CHECK(type IN ('abertura', 'suprimento', 'sangria', 'venda')),
            payment_method TEXT,
            amount REAL NOT NULL,
            notes TEXT,
            reference_id INTEGER,
            timestamp DATETIME DEFAULT CURRENT_TIMESTAMP,
            FOREIGN KEY(session_id) REFERENCES cash_sessions(id),
            FOREIGN KEY(user_id) REFERENCES users(id)
        )
    ''')

    # Adiciona a coluna session_id na tabela de vendas
    try:
        cur.execute("ALTER TABLE sales ADD COLUMN session_id INTEGER REFERENCES cash_sessions(id)")
    except sqlite3.OperationalError:
        pass # Coluna já existe

    # 7. Tabela de Contas a Receber (Crediário/Fiado)
    cur.execute('''
        CREATE TABLE IF NOT EXISTS accounts_receivable (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            sale_id INTEGER NOT NULL,
            customer_id INTEGER NOT NULL,
            installment_number INTEGER NOT NULL,
            total_installments INTEGER NOT NULL,
            amount REAL NOT NULL,
            due_date DATE NOT NULL,
            payment_date DATE,
            status TEXT NOT NULL CHECK(status IN ('pending', 'paid', 'overdue')),
            FOREIGN KEY(sale_id) REFERENCES sales(id),
            FOREIGN KEY(customer_id) REFERENCES customers(id)
        )
    ''')

    def seed_default_categories(conn):
        cur = conn.cursor()
        default_categories = [
            "Motor", "Alimentação", "Ignição", "Arrefecimento", "Lubrificação",
            "Admissão e Escape", "Transmissão", "Freios", "Suspensão", "Direção",
            "Rodas e Cubos", "Sistema Elétrico", "Iluminação", "Sensores e Eletrônica",
            "Climatização", "Carroceria", "Vidros", "Limpadores", "Interior",
            "Fechaduras e Segurança", "Borrachas e Vedação", "Fixação",
            "Fluidos e Produtos Químicos", "Acessórios"
        ]
        for nome in default_categories:
            cur.execute("SELECT id FROM categories WHERE nome = ?", (nome,))
            if not cur.fetchone():
                cur.execute("INSERT INTO categories (nome, margem_padrao) VALUES (?, 0)", (nome,))
            
    seed_default_categories(conn)
        
    conn.commit()
    conn.close()