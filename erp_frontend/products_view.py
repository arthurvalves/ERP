import customtkinter as ctk
from tkinter import messagebox, Menu
from erp_frontend.components.table import TableComponent
from erp_backend.services import categorization_service
from erp_backend.utils.db import get_connection
from erp_frontend import theme

class ProductModal(ctk.CTkToplevel):
    def __init__(self, master, product_id=None, initial_data=None, on_save=None):
        super().__init__(master)
        self.title("Editar Produto" if product_id else "Novo Produto")
        self.configure(fg_color=theme.BG)
        self.transient(master)
        self.grab_set()

        self.product_id = product_id
        self.initial_data = initial_data or {}
        self.on_save = on_save
        self._updating = False

        self.setup_ui()
        self.load_data()
        self.bind("<Escape>", lambda e: self.destroy())
        self.after(10, self._center_window)

    def _center_window(self):
        self.update_idletasks()
        width = 900
        height = 800
        screen_width = self.winfo_screenwidth()
        screen_height = self.winfo_screenheight()
        x = (screen_width // 2) - (width // 2)
        y = (screen_height // 2) - (height // 2)
        self.geometry(f'{width}x{height}+{x}+{y}')
        self.resizable(False, False)

    def get_categorias(self):
        return [
            "A Definir", "Motor", "Alimentação", "Ignição", "Arrefecimento", "Lubrificação",
            "Admissão e Escape", "Transmissão", "Freios", "Suspensão", "Direção",
            "Rodas e Cubos", "Sistema Elétrico", "Iluminação", "Sensores e Eletrônica",
            "Climatização", "Carroceria", "Vidros", "Limpadores", "Interior",
            "Fechaduras e Segurança", "Borrachas e Vedação", "Fixação",
            "Fluidos e Produtos Químicos", "Acessórios"
        ]

    def setup_ui(self):
        self.frame = ctk.CTkFrame(self, fg_color=theme.BG)
        self.frame.pack(fill="both", expand=True, padx=20, pady=20)

        ctk.CTkLabel(self.frame, text="Categoria:", font=theme.font_body(12), text_color=theme.TEXT_MUTED).pack(anchor="w")
        self.cb_categoria = ctk.CTkOptionMenu(self.frame, values=self.get_categorias(),
                                               fg_color=theme.SECONDARY, button_color=theme.SECONDARY, button_hover_color=theme.PRIMARY)
        self.cb_categoria.pack(fill="x", pady=(0, 10))

        self.cb_categoria.configure(command=self.aplicar_margem_categoria)

        ctk.CTkLabel(self.frame, text="Nome do Produto:", font=theme.font_bold(14), text_color=theme.TEXT).pack(anchor="w", pady=(10, 0))
        self.ent_nome = ctk.CTkEntry(self.frame, font=theme.font_body(14), width=400, fg_color=theme.CARD, border_color=theme.SECONDARY)
        self.ent_nome.pack(fill="x", pady=(0, 10))

        row1 = ctk.CTkFrame(self.frame, fg_color="transparent")
        row1.pack(fill="x", pady=5)

        f_sku = ctk.CTkFrame(row1, fg_color="transparent")
        f_sku.pack(side="left", fill="x", expand=True, padx=(0, 5))
        ctk.CTkLabel(f_sku, text="SKU / Referência:", font=theme.font_body(12), text_color=theme.TEXT_MUTED).pack(anchor="w")
        self.ent_sku = ctk.CTkEntry(f_sku, font=theme.font_body(14), fg_color=theme.CARD, border_color=theme.SECONDARY)
        self.ent_sku.pack(fill="x")

        f_ean = ctk.CTkFrame(row1, fg_color="transparent")
        f_ean.pack(side="left", fill="x", expand=True, padx=(5, 0))
        ctk.CTkLabel(f_ean, text="EAN:", font=theme.font_body(12), text_color=theme.TEXT_MUTED).pack(anchor="w")
        self.ent_ean = ctk.CTkEntry(f_ean, font=theme.font_body(14), fg_color=theme.CARD, border_color=theme.SECONDARY)
        self.ent_ean.pack(fill="x")

        f_ncm = ctk.CTkFrame(row1, fg_color="transparent")
        f_ncm.pack(side="left", fill="x", expand=True, padx=(5, 0))
        ctk.CTkLabel(f_ncm, text="NCM:", font=theme.font_body(12), text_color=theme.TEXT_MUTED).pack(anchor="w")
        self.ent_ncm = ctk.CTkEntry(f_ncm, font=theme.font_body(14), fg_color=theme.CARD, border_color=theme.SECONDARY, state='readonly')
        self.ent_ncm.pack(fill="x")

        row1_5 = ctk.CTkFrame(self.frame, fg_color="transparent")
        row1_5.pack(fill="x", pady=5)

        f_cfop = ctk.CTkFrame(row1_5, fg_color="transparent")
        f_cfop.pack(side="left", fill="x", expand=True, padx=(0, 5))
        ctk.CTkLabel(f_cfop, text="CFOP Padrão:", font=theme.font_body(12), text_color=theme.TEXT_MUTED).pack(anchor="w")
        self.ent_cfop = ctk.CTkEntry(f_cfop, font=theme.font_body(14), fg_color=theme.CARD, border_color=theme.SECONDARY)
        self.ent_cfop.pack(fill="x")

        f_tipo = ctk.CTkFrame(row1_5, fg_color="transparent")
        f_tipo.pack(side="left", fill="x", expand=True, padx=(5, 0))
        ctk.CTkLabel(f_tipo, text="Tipo de Item:", font=theme.font_body(12), text_color=theme.TEXT_MUTED).pack(anchor="w")
        self.cb_tipo = ctk.CTkOptionMenu(f_tipo, values=["Produto", "Serviço"],
                                          fg_color=theme.SECONDARY, button_color=theme.SECONDARY, button_hover_color=theme.PRIMARY)
        self.cb_tipo.pack(fill="x")

        ctk.CTkLabel(self.frame, text="Custo Unitário (R$):", font=theme.font_bold(14), text_color=theme.TEXT).pack(anchor="w", pady=(15, 0))
        self.ent_custo = ctk.CTkEntry(self.frame, font=theme.font_body(14), width=200, fg_color=theme.CARD, border_color=theme.SECONDARY)
        self.ent_custo.pack(anchor="w", pady=(0, 10))
        self.ent_custo.bind("<KeyRelease>", self.on_cost_change)

        row2 = ctk.CTkFrame(self.frame, fg_color="transparent")
        row2.pack(fill="x", pady=15)

        f_atacado = ctk.CTkFrame(row2, fg_color="transparent")
        f_atacado.pack(side="left", fill="x", expand=True, padx=(0, 5))
        ctk.CTkLabel(f_atacado, text="Preço Atacado (R$):", font=theme.font_bold(14), text_color=theme.PRIMARY).pack(anchor="w")
        self.ent_atacado = ctk.CTkEntry(f_atacado, font=theme.font_bold(16), fg_color=theme.CARD, border_color=theme.SECONDARY)
        self.ent_atacado.pack(fill="x")

        f_preco_container = ctk.CTkFrame(row2, fg_color="transparent")
        f_preco_container.pack(side="left", fill="x", expand=True, padx=(5, 0))

        ctk.CTkLabel(f_preco_container, text="Preço Varejo (R$):", font=theme.font_bold(16), text_color=theme.SUCCESS).pack(anchor="w")
        self.ent_preco = ctk.CTkEntry(f_preco_container, font=theme.font_title(24), text_color=theme.TEXT, fg_color=theme.CARD, border_color=theme.SECONDARY)
        self.ent_preco.pack(fill="x", pady=(0, 10))
        self.ent_preco.bind("<KeyRelease>", self.on_price_change)

        ctk.CTkLabel(f_preco_container, text="Margem Lucro (%):", font=theme.font_bold(12), text_color=theme.INFO).pack(anchor="w")
        self.ent_margem = ctk.CTkEntry(f_preco_container, font=theme.font_bold(14), fg_color=theme.CARD, border_color=theme.SECONDARY)
        self.ent_margem.pack(fill="x")
        self.ent_margem.bind("<KeyRelease>", self.on_margin_change)

        row3 = ctk.CTkFrame(self.frame, fg_color="transparent")
        row3.pack(fill="x", pady=15)

        f_min_stock = ctk.CTkFrame(row3, fg_color="transparent")
        f_min_stock.pack(side="left", fill="x", expand=True, padx=(0, 5))
        ctk.CTkLabel(f_min_stock, text="Estoque Mínimo:", font=theme.font_body(12), text_color=theme.TEXT_MUTED).pack(anchor="w")
        self.ent_min_stock = ctk.CTkEntry(f_min_stock, font=theme.font_body(14), fg_color=theme.CARD, border_color=theme.SECONDARY)
        self.ent_min_stock.pack(fill="x")

        f_max_stock = ctk.CTkFrame(row3, fg_color="transparent")
        f_max_stock.pack(side="left", fill="x", expand=True, padx=(5, 0))
        ctk.CTkLabel(f_max_stock, text="Estoque Máximo:", font=theme.font_body(12), text_color=theme.TEXT_MUTED).pack(anchor="w")
        self.ent_max_stock = ctk.CTkEntry(f_max_stock, font=theme.font_body(14), fg_color=theme.CARD, border_color=theme.SECONDARY)
        self.ent_max_stock.pack(fill="x")

        footer = ctk.CTkFrame(self.frame, fg_color="transparent")
        footer.pack(fill="x", side="bottom", pady=20)

        ctk.CTkButton(footer, text="SALVAR", command=self.save, **theme.btn_primary(font=theme.font_bold(16))).pack(side="right", padx=5)
        ctk.CTkButton(footer, text="CANCELAR", command=self.destroy, **theme.btn_danger()).pack(side="right", padx=5)

    def aplicar_margem_categoria(self, nome_categoria):
        try:
            custo = float(self.ent_custo.get().replace(",", "."))
            if custo <= 0: return
            conn = get_connection()
            cur = conn.cursor()
            cur.execute("SELECT margem_padrao FROM categories WHERE nome = ?", (nome_categoria,))
            row = cur.fetchone()
            conn.close()
            if row and row['margem_padrao']:
                margem = float(row['margem_padrao'])
                novo_preco = custo * (1 + (margem / 100))
                
                self.ent_preco.delete(0, 'end')
                self.ent_preco.insert(0, f"{novo_preco:.2f}")
        except ValueError:
            pass

    def load_data(self):
        if not self.product_id:
            self.ent_nome.insert(0, self.initial_data.get('nome', ''))
            self.ent_sku.insert(0, self.initial_data.get('sku', ''))
            self.ent_ean.insert(0, self.initial_data.get('codigo_barras', ''))
            self.ent_ncm.configure(state='normal'); self.ent_ncm.insert(0, self.initial_data.get('ncm', '')); self.ent_ncm.configure(state='readonly')
            self.ent_cfop.insert(0, self.initial_data.get('cfop_padrao', ''))
            self.ent_atacado.insert(0, f"{self.initial_data.get('preco_atacado', 0.0):.2f}")
            self.ent_min_stock.insert(0, f"{self.initial_data.get('estoque_minimo', 0.0):.2f}")
            self.ent_max_stock.insert(0, f"{self.initial_data.get('estoque_maximo', 0.0):.2f}")
            self.cb_tipo.set("Serviço" if self.initial_data.get('is_servico') else "Produto")

            custo = self.initial_data.get('custo', 0.0)
            self.ent_custo.insert(0, f"{custo:.2f}")
            self.ent_preco.insert(0, "0.00")

            # Pré-seleciona a categoria se ela foi adivinhada na tela de NF-e
            categoria_id = self.initial_data.get('categoria_id')
            if categoria_id:
                conn = get_connection()
                cat_row = conn.cursor().execute("SELECT nome FROM categories WHERE id = ?", (categoria_id,)).fetchone()
                conn.close()
                if cat_row:
                    self.cb_categoria.set(cat_row['nome'])

            self.ent_margem.insert(0, "0.00")
            self._update_margin_color(0.0)
            return

        conn = get_connection()
        cur = conn.cursor()
        cur.execute("SELECT * FROM products WHERE id = ?", (self.product_id,))
        row = cur.fetchone()
        conn.close()

        if row:
            self.ent_nome.insert(0, row['nome'] or "")
            self.ent_sku.insert(0, row['sku'] or "")
            self.ent_ean.insert(0, row['codigo_barras'] or "")
            self.ent_ncm.configure(state='normal'); self.ent_ncm.insert(0, row['ncm'] or ""); self.ent_ncm.configure(state='readonly')
            self.ent_cfop.insert(0, row['cfop_padrao'] or "")
            self.ent_min_stock.insert(0, f"{row['estoque_minimo'] or 0.0:.2f}")
            self.ent_max_stock.insert(0, f"{row['estoque_maximo'] or 0.0:.2f}")
            self.ent_atacado.insert(0, f"{row['preco_atacado'] or 0.0:.2f}")
            self.cb_tipo.set("Serviço" if row['is_servico'] else "Produto")

            custo = row['custo'] or 0.0
            preco = row['preco_venda'] or 0.0
            self.ent_custo.insert(0, f"{custo:.2f}")
            self.ent_preco.insert(0, f"{preco:.2f}")

            if row['categoria_id']:
                cur.execute("SELECT nome FROM categories WHERE id = ?", (row['categoria_id'],))
                cat_row = cur.fetchone()
                if cat_row:
                    self.cb_categoria.set(cat_row['nome'])
        self.on_price_change()

    def _update_margin_color(self, margem: float):
        if margem < 0:
            self.ent_margem.configure(text_color=theme.DANGER)
        else:
            self.ent_margem.configure(text_color=theme.TEXT)

    def on_cost_change(self, event=None):
        self.on_margin_change()

    def on_price_change(self, event=None):
        if self._updating: return
        self._updating = True
        try:
            custo = float(self.ent_custo.get().replace(",", "."))
            preco = float(self.ent_preco.get().replace(",", "."))
            if custo > 0:
                margem = ((preco - custo) / custo) * 100
            else:
                margem = 100.0 if preco > 0 else 0.0
            self.ent_margem.delete(0, "end")
            self.ent_margem.insert(0, f"{margem:.2f}")
            self._update_margin_color(margem)
        except ValueError:
            pass
        self._updating = False

    def on_margin_change(self, event=None):
        if self._updating: return
        self._updating = True
        try:
            custo = float(self.ent_custo.get().replace(",", "."))
            margem = float(self.ent_margem.get().replace(",", "."))
            preco = custo + (custo * (margem / 100))
            self.ent_preco.delete(0, "end")
            self.ent_preco.insert(0, f"{preco:.2f}")
            self._update_margin_color(margem)
        except ValueError:
            pass
        self._updating = False

    def save(self):
        nome = self.ent_nome.get().strip()
        sku = self.ent_sku.get().strip()
        ean = self.ent_ean.get().strip()
        ncm = self.ent_ncm.cget('state') == 'normal' and self.ent_ncm.get().strip() or self.initial_data.get('ncm', '')
        cfop = self.ent_cfop.get().strip()
        is_servico = 1 if self.cb_tipo.get() == "Serviço" else 0
        categoria_nome = self.cb_categoria.get()

        try:
            custo = float(self.ent_custo.get().replace(",", "."))
            preco = float(self.ent_preco.get().replace(",", "."))
            atacado = float(self.ent_atacado.get().replace(",", "."))
            min_stock = float(self.ent_min_stock.get().replace(",", "."))
            max_stock = float(self.ent_max_stock.get().replace(",", "."))
        except ValueError:
            messagebox.showerror("Erro", "Valores numéricos inválidos.")
            return

        if not all(c.isalnum() or c.isspace() for c in nome):
            messagebox.showerror("Erro de Validação", "O nome do produto deve conter apenas letras, números e espaços.")
            return

        if not nome:
            messagebox.showerror("Erro", "Nome é obrigatório.")
            return

        conn = get_connection()
        cur = conn.cursor()
        
        categoria_id = None # Default para nulo
        if categoria_nome:
            cur.execute("SELECT id FROM categories WHERE nome = ?", (categoria_nome,))
            cat_row = cur.fetchone()
            if cat_row: categoria_id = cat_row['id']
        
        # Lógica de aprendizado: se o usuário definiu uma categoria e o produto tem NCM, o sistema aprende.
        if categoria_id and ncm:
            categorization_service.learn_ncm_category(ncm, categoria_id, conn=conn)

        try:
            if self.product_id:
                cur.execute("UPDATE products SET nome=?, sku=?, codigo_barras=?, ncm=?, custo=?, preco_venda=?, cfop_padrao=?, preco_atacado=?, is_servico=?, estoque_minimo=?, estoque_maximo=?, categoria_id=? WHERE id=?",
                            (nome, sku, ean, ncm, custo, preco, cfop, atacado, is_servico, min_stock, max_stock, categoria_id, self.product_id))
            else:
                try:
                    from erp_backend.core.normalizer import normalize
                    nome_norm = normalize(nome)
                except ImportError:
                    nome_norm = nome.upper()
                # Correção: Incluindo referencia e fornecedor_id no INSERT
                referencia = self.initial_data.get('referencia')
                fornecedor_id = self.initial_data.get('fornecedor_id')
                cur.execute("INSERT INTO products (nome, nome_normalizado, sku, codigo_barras, ncm, referencia, fornecedor_id, custo, preco_venda, estoque_atual, cfop_padrao, preco_atacado, is_servico, estoque_minimo, estoque_maximo, categoria_id) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, 0, ?, ?, ?, ?, ?, ?)",
                            (nome, nome_norm, sku, ean, ncm, referencia, fornecedor_id, custo, preco, cfop, atacado, is_servico, min_stock, max_stock, categoria_id))
            conn.commit()
            if self.on_save:
                self.on_save()
            self.destroy()
        except Exception as e:
            conn.rollback()
            messagebox.showerror("Erro ao Salvar", str(e))
        finally:
            conn.close()

class ProductsView(ctk.CTkFrame):
    def __init__(self, master, app_window, **kwargs):
        super().__init__(master, fg_color=theme.BG, **kwargs)
        self.app_window = app_window
        self.setup_ui()
        self.load_data()
        self.bind_shortcuts()

    def bind_shortcuts(self):
        self.app_window.bind("<F2>", lambda e: self.edit_selected())
        self.app_window.bind("<F5>", lambda e: self.load_data())
        self.app_window.bind("<F6>", lambda e: self.import_nfe())

    def unbind_shortcuts(self):
        self.app_window.unbind("<F2>")
        self.app_window.unbind("<F5>")
        self.app_window.unbind("<F6>")

    def destroy(self):
        self.unbind_shortcuts()
        super().destroy()

    def setup_ui(self):
        top_frame = ctk.CTkFrame(self, fg_color="transparent")
        top_frame.pack(fill="x", padx=20, pady=10)

        search_frame = ctk.CTkFrame(top_frame, fg_color="transparent")
        search_frame.pack(side="left", fill="x", expand=True)

        self.search_entry = ctk.CTkEntry(search_frame, placeholder_text="🔎 BUSCA: NOME / SKU / EAN / FORNECEDOR...", height=40,
                                          font=theme.font_body(16), fg_color=theme.CARD, border_color=theme.SECONDARY)
        self.search_entry.pack(fill="x", padx=(0, 20))
        self.search_entry.bind("<KeyRelease>", self.on_search)

        summary_frame = ctk.CTkFrame(top_frame, **theme.card_frame_kwargs())
        summary_frame.pack(side="right", padx=10)

        self.lbl_total_prod = ctk.CTkLabel(summary_frame, text="PRODUTOS: 0", font=theme.font_bold(14), text_color=theme.TEXT)
        self.lbl_total_prod.pack(side="left", padx=15, pady=10)

        self.lbl_critical_stock = ctk.CTkLabel(summary_frame, text="ESTOQUE CRÍTICO: 0", font=theme.font_bold(14), text_color=theme.DANGER)
        self.lbl_critical_stock.pack(side="left", padx=15, pady=10)

        self.lbl_total_value = ctk.CTkLabel(summary_frame, text="VALOR: R$ 0.00", font=theme.font_bold(14), text_color=theme.SUCCESS)
        self.lbl_total_value.pack(side="left", padx=15, pady=10)

        actions_frame = ctk.CTkFrame(self, fg_color="transparent")
        actions_frame.pack(fill="x", padx=20, pady=(0, 10))

        btn_new = ctk.CTkButton(actions_frame, text="[ NOVO ]", command=self.new_product, **theme.btn_primary())
        btn_new.pack(side="left", padx=5)

        btn_edit = ctk.CTkButton(actions_frame, text="[F2] EDITAR", command=self.edit_selected, **theme.btn_secondary())
        btn_edit.pack(side="left", padx=5)

        btn_refresh = ctk.CTkButton(actions_frame, text="[F5] ATUALIZAR", command=self.load_data,
                                     **theme.btn_secondary(fg_color=theme.INFO, hover_color="#2563eb", text_color="#ffffff"))
        btn_refresh.pack(side="left", padx=5)

        btn_recalc = ctk.CTkButton(actions_frame, text="[ RECALCULAR ]", command=self.recalc_stock,
                                    **theme.btn_secondary(fg_color="#a855f7", hover_color="#9333ea", text_color="#ffffff"))
        btn_recalc.pack(side="left", padx=5)

        btn_import = ctk.CTkButton(actions_frame, text="[F6] IMPORTAR NF-e", command=self.import_nfe, **theme.btn_success())
        btn_import.pack(side="right", padx=5)

        columns = ("NOME", "CATEGORIA", "SKU", "EAN", "ESTOQUE", "CUSTO", "PREÇO", "STATUS")
        self.table = TableComponent(self, columns, style="Products.Treeview")
        self.table.column("NOME", width=350, anchor="w")
        self.table.column("CATEGORIA", width=150, anchor="w")
        self.table.column("SKU", width=120)
        self.table.column("EAN", width=120)
        self.table.column("ESTOQUE", width=100)
        self.table.column("CUSTO", width=100)
        self.table.column("PREÇO", width=100)
        self.table.column("STATUS", width=120)

        self.table.tag_configure("ok", foreground=theme.SUCCESS)
        self.table.tag_configure("low", foreground=theme.PRIMARY)
        self.table.tag_configure("empty", foreground=theme.DANGER)

        self.table.tag_configure("sem_categoria", foreground=theme.WARNING)
        self.table.tag_configure("ok", foreground="#2ecc71")
        self.table.tag_configure("low", foreground="#f1c40f")
        self.table.tag_configure("empty", foreground="#e74c3c")
        
        self.table.pack(fill="both", expand=True, padx=20, pady=10)
        self.table.bind("<Double-1>", lambda e: self.edit_selected())
        self.table.bind("<Return>", lambda e: self.edit_selected())
        self.table.bind("<Button-3>", self._show_context_menu)
        self._create_context_menu()

    def load_data(self, event=None):
        query = self.search_entry.get().strip()
        for item in self.table.get_children():
            self.table.delete(item)

        conn = get_connection()
        cur = conn.cursor()

        sql = """
            SELECT p.id, p.nome, p.sku, p.codigo_barras, p.estoque_atual, p.custo, p.preco_venda, s.razao_social, c.nome as categoria_nome
            FROM products p
            LEFT JOIN suppliers s ON p.fornecedor_id = s.id
            LEFT JOIN categories c ON p.categoria_id = c.id
        """
        params = ()
        if query:
            q = f"%{query}%"
            sql += " WHERE p.nome LIKE ? OR p.sku LIKE ? OR p.codigo_barras LIKE ? OR s.razao_social LIKE ?"
            params = (q, q, q, q)

        sql += " ORDER BY p.nome LIMIT 100"
        cur.execute(sql, params)
        rows = cur.fetchall()

        cur.execute("SELECT COUNT(id) FROM products")
        total_prod = cur.fetchone()[0] or 0
        
        cur.execute("SELECT COUNT(id) FROM products WHERE estoque_atual <= 5")
        critical = cur.fetchone()[0] or 0
        
        cur.execute("SELECT SUM(estoque_atual * custo) FROM products WHERE estoque_atual > 0")
        total_val = cur.fetchone()[0] or 0.0
        
        for row in rows:
            est = row['estoque_atual'] or 0.0
            custo = row['custo'] or 0.0            
            categoria = row['categoria_nome'] or "A CLASSIFICAR"
            
            if est <= 0:
                status, tag = "SEM ESTOQUE", "empty"
            elif est <= 5:
                status, tag = "BAIXO", "low"
            else:
                status, tag = "OK", "ok"
            
            tags = (tag, "sem_categoria" if not row['categoria_nome'] else "")
            
            self.table.insert("", "end", iid=str(row['id']), values=(
                row['nome'],
                categoria,
                row['sku'] or "--",
                row['codigo_barras'] or "--",
                f"{est:.3f}".rstrip('0').rstrip('.'),
                f"R$ {custo:.2f}",
                f"R$ {row['preco_venda'] or 0.0:.2f}",
                status
            ), tags=tags)

        conn.close()
        
        self.lbl_total_prod.configure(text=f"PRODUTOS: {total_prod}")
        self.lbl_critical_stock.configure(text=f"ESTOQUE CRÍTICO: {critical}")
        self.lbl_total_value.configure(text=f"VALOR: R$ {total_val:.2f}")

    def on_search(self, event):
        self.load_data()

    def _create_context_menu(self):
        self.context_menu = Menu(self.table, tearoff=0, font=theme.font_body(12),
                                  bg=theme.CARD, fg=theme.TEXT, activebackground=theme.PRIMARY,
                                  activeforeground=theme.PRIMARY_FOREGROUND)
        self.context_menu.add_command(label="Novo Produto", command=self.new_product)
        self.context_menu.add_command(label="Editar Produto Selecionado", command=self.edit_selected)
        self.context_menu.add_separator()
        self.context_menu.add_command(label="Importar NF-e", command=self.import_nfe)

    def _show_context_menu(self, event):
        selection = self.table.selection()
        if selection:
            self.context_menu.entryconfigure("Editar Produto Selecionado", state="normal")
        else:
            self.context_menu.entryconfigure("Editar Produto Selecionado", state="disabled")
        self.context_menu.post(event.x_root, event.y_root)

    def new_product(self):
        ProductModal(self, on_save=self.load_data)

    def edit_selected(self):
        selected = self.table.selection()
        if not selected:
            return
        product_id = int(selected[0])
        ProductModal(self, product_id=product_id, on_save=self.load_data)

    def import_nfe(self):
        from erp_frontend.nfe_view import NFeView
        self.app_window.show_view(NFeView)

    def recalc_stock(self):
            try:
                from erp_backend.core.stock_reconciliation import detect_stock_inconsistencies, recompute_stock
                anomalies = detect_stock_inconsistencies()
                if not anomalies:
                    messagebox.showinfo("Estoque", "Estoque está perfeitamente consistente.")
                    return
                for a in anomalies:
                    recompute_stock(a['product_id'])
                messagebox.showinfo("Estoque", f"{len(anomalies)} inconsistências corrigidas.")
                self.load_data()
            except ImportError:
                messagebox.showerror("Erro", "Módulo de reconciliação não disponível.")
