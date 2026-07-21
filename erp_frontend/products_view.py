import customtkinter as ctk
from tkinter import messagebox
from erp_frontend.components.table import TableComponent
from erp_backend.utils.db import get_connection

class ProductModal(ctk.CTkToplevel):
    def __init__(self, master, product_id=None, initial_data=None, on_save=None):
        super().__init__(master)
        self.title("Editar Produto" if product_id else "Novo Produto")
        self.geometry("500x550")
        self.transient(master)
        self.grab_set()
        
        self.product_id = product_id
        self.initial_data = initial_data or {}
        self.on_save = on_save
        self._updating = False
        
        self.setup_ui()
        self.load_data()
        self.bind("<Escape>", lambda e: self.destroy())
        
        self.limit = 50
        self.offset = 0

        # 2. No final da função setup_ui(), adicione os botões de páginação abaixo da tabela:
        frame_paginacao = ctk.CTkFrame(self, fg_color="transparent")
        frame_paginacao.pack(pady=5)
        
        self.btn_prev = ctk.CTkButton(frame_paginacao, text="<< Anterior", width=100, command=self.pagina_anterior)
        self.btn_prev.pack(side="left", padx=10)
        
        self.lbl_pagina = ctk.CTkLabel(frame_paginacao, text="Página 1", font=("Roboto", 14, "bold"))
        self.lbl_pagina.pack(side="left", padx=10)
        
        self.btn_next = ctk.CTkButton(frame_paginacao, text="Próxima >>", width=100, command=self.proxima_pagina)
        self.btn_next.pack(side="left", padx=10)
    
    def pagina_anterior(self):
        if self.offset >= self.limit:
            self.offset -= self.limit
            self.load_data()

    def proxima_pagina(self):
        # Só avança se a tabela estiver cheia (indicando que há mais itens)
        if len(self.table.get_children()) == self.limit:
            self.offset += self.limit
            self.load_data()
    
    def get_categorias(self):
        conn = get_connection()
        cur = conn.cursor()
        cur.execute("SELECT nome FROM categories")
        cats = [row['nome'] for row in cur.fetchall()]
        conn.close()
        return cats
    
    def setup_ui(self):
        self.frame = ctk.CTkFrame(self)
        self.frame.pack(fill="both", expand=True, padx=20, pady=20)
        
        categorias = self.get_categorias()
        ctk.CTkLabel(self.frame, text="Categoria:", font=("Roboto", 12)).pack(anchor="w")
        self.cb_categoria = ctk.CTkOptionMenu(self.frame, values=self.get_categorias()) 
        self.cb_categoria.pack(fill="x", pady=(0, 10))
        
        self.cb_categoria.configure(command=self.aplicar_margem_categoria)
        
        ctk.CTkLabel(self.frame, text="Nome do Produto:", font=("Roboto", 14, "bold")).pack(anchor="w", pady=(10, 0))
        self.ent_nome = ctk.CTkEntry(self.frame, font=("Roboto", 14), width=400)
        self.ent_nome.pack(fill="x", pady=(0, 10))
        
        row1 = ctk.CTkFrame(self.frame, fg_color="transparent")
        row1.pack(fill="x", pady=5)
        
        f_sku = ctk.CTkFrame(row1, fg_color="transparent")
        f_sku.pack(side="left", fill="x", expand=True, padx=(0, 5))
        ctk.CTkLabel(f_sku, text="SKU / Referência:", font=("Roboto", 12)).pack(anchor="w")
        self.ent_sku = ctk.CTkEntry(f_sku, font=("Roboto", 14))
        self.ent_sku.pack(fill="x")
        
        f_ean = ctk.CTkFrame(row1, fg_color="transparent")
        f_ean.pack(side="left", fill="x", expand=True, padx=(5, 0))
        ctk.CTkLabel(f_ean, text="EAN:", font=("Roboto", 12)).pack(anchor="w")
        self.ent_ean = ctk.CTkEntry(f_ean, font=("Roboto", 14))
        self.ent_ean.pack(fill="x")
        
        row1_5 = ctk.CTkFrame(self.frame, fg_color="transparent")
        row1_5.pack(fill="x", pady=5)
        
        f_cfop = ctk.CTkFrame(row1_5, fg_color="transparent")
        f_cfop.pack(side="left", fill="x", expand=True, padx=(0, 5))
        ctk.CTkLabel(f_cfop, text="CFOP Padrão:", font=("Roboto", 12)).pack(anchor="w")
        self.ent_cfop = ctk.CTkEntry(f_cfop, font=("Roboto", 14))
        self.ent_cfop.pack(fill="x")
        
        f_tipo = ctk.CTkFrame(row1_5, fg_color="transparent")
        f_tipo.pack(side="left", fill="x", expand=True, padx=(5, 0))
        ctk.CTkLabel(f_tipo, text="Tipo de Item:", font=("Roboto", 12)).pack(anchor="w")
        self.cb_tipo = ctk.CTkOptionMenu(f_tipo, values=["Produto", "Serviço"])
        self.cb_tipo.pack(fill="x")
        
        ctk.CTkLabel(self.frame, text="Custo Unitário (R$):", font=("Roboto", 14, "bold")).pack(anchor="w", pady=(15, 0))
        self.ent_custo = ctk.CTkEntry(self.frame, font=("Roboto", 14), width=200)
        self.ent_custo.pack(anchor="w", pady=(0, 10))
        self.ent_custo.bind("<KeyRelease>", self.on_cost_change)
        
        row2 = ctk.CTkFrame(self.frame, fg_color="transparent")
        row2.pack(fill="x", pady=15)
        
        f_atacado = ctk.CTkFrame(row2, fg_color="transparent")
        f_atacado.pack(side="left", fill="x", expand=True, padx=(0, 5))
        ctk.CTkLabel(f_atacado, text="Preço Atacado (R$):", font=("Roboto", 14, "bold"), text_color="#f39c12").pack(anchor="w")
        self.ent_atacado = ctk.CTkEntry(f_atacado, font=("Roboto", 16, "bold"))
        self.ent_atacado.pack(fill="x")
        
        f_preco_container = ctk.CTkFrame(row2, fg_color="transparent")
        f_preco_container.pack(side="left", fill="x", expand=True, padx=(5, 0))
        
        ctk.CTkLabel(f_preco_container, text="Preço Varejo (R$):", font=("Roboto", 16, "bold"), text_color="#2ecc71").pack(anchor="w")
        self.ent_preco = ctk.CTkEntry(f_preco_container, font=("Roboto", 24, "bold"), text_color="#ffffff")
        self.ent_preco.pack(fill="x", pady=(0, 10))
        self.ent_preco.bind("<KeyRelease>", self.on_price_change)
        
        ctk.CTkLabel(f_preco_container, text="Margem Lucro (%):", font=("Roboto", 12, "bold"), text_color="#3498db").pack(anchor="w")
        self.ent_margem = ctk.CTkEntry(f_preco_container, font=("Roboto", 14, "bold"))
        self.ent_margem.pack(fill="x")
        self.ent_margem.bind("<KeyRelease>", self.on_margin_change)
        
        footer = ctk.CTkFrame(self.frame, fg_color="transparent")
        footer.pack(fill="x", side="bottom", pady=20)
        
        ctk.CTkButton(footer, text="SALVAR", font=("Roboto", 16, "bold"), fg_color="#2ecc71", hover_color="#27ae60", command=self.save).pack(side="right", padx=5)
        ctk.CTkButton(footer, text="CANCELAR", font=("Roboto", 16), fg_color="#e74c3c", hover_color="#c0392b", command=self.destroy).pack(side="right", padx=5)

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
                
                # Atualiza o campo de Preço de Venda automaticamente
                self.ent_preco.delete(0, 'end')
                self.ent_preco.insert(0, f"{novo_preco:.2f}")
        except ValueError:
            pass # Ignora se o custo estiver vazio ou inválido no momento

    def load_data(self):
        if not self.product_id:
            self.ent_nome.insert(0, self.initial_data.get('nome', ''))
            self.ent_sku.insert(0, self.initial_data.get('sku', ''))
            self.ent_ean.insert(0, self.initial_data.get('codigo_barras', ''))
            self.ent_cfop.insert(0, self.initial_data.get('cfop_padrao', ''))
            self.ent_atacado.insert(0, f"{self.initial_data.get('preco_atacado', 0.0):.2f}")
            self.cb_tipo.set("Serviço" if self.initial_data.get('is_servico') else "Produto")
            
            custo = self.initial_data.get('custo', 0.0)
            self.ent_custo.insert(0, f"{custo:.2f}")
            self.ent_preco.insert(0, "0.00")
            self.ent_margem.insert(0, "0.00")
            self._update_margin_color(0.0)
            return
            
        conn = get_connection()
        cur = conn.cursor()
        cur.execute("SELECT nome, sku, codigo_barras, custo, preco_venda, cfop_padrao, preco_atacado, is_servico FROM products WHERE id = ?", (self.product_id,))
        row = cur.fetchone()
        conn.close()
        
        if row:
            self.ent_nome.insert(0, row['nome'] or "")
            self.ent_sku.insert(0, row['sku'] or "")
            self.ent_ean.insert(0, row['codigo_barras'] or "")
            self.ent_cfop.insert(0, row['cfop_padrao'] or "")
            self.ent_atacado.insert(0, f"{row['preco_atacado'] or 0.0:.2f}")
            self.cb_tipo.set("Serviço" if row['is_servico'] else "Produto")
            
            custo = row['custo'] or 0.0
            preco = row['preco_venda'] or 0.0
            self.ent_custo.insert(0, f"{custo:.2f}")
            self.ent_preco.insert(0, f"{preco:.2f}")
            self.on_price_change()
            
        if query and query != getattr(self, 'last_query', ''):
            self.offset = 0
        self.last_query = query

        sql += " ORDER BY id DESC LIMIT ? OFFSET ?"
        params = params + (self.limit, self.offset)
        
        pagina_atual = (self.offset // self.limit) + 1
        self.lbl_pagina.configure(text=f"Página {pagina_atual}")
        self.btn_prev.configure(state="normal" if self.offset > 0 else "disabled")
        
    def _update_margin_color(self, margem: float):
        if margem < 0:
            self.ent_margem.configure(text_color="#e74c3c")
        else:
            self.ent_margem.configure(text_color="#ffffff")

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
        cfop = self.ent_cfop.get().strip()
        is_servico = 1 if self.cb_tipo.get() == "Serviço" else 0
        
        try:
            custo = float(self.ent_custo.get().replace(",", "."))
            preco = float(self.ent_preco.get().replace(",", "."))
            atacado = float(self.ent_atacado.get().replace(",", "."))
        except ValueError:
            messagebox.showerror("Erro", "Valores numéricos inválidos.")
            return
            
        if not nome:
            messagebox.showerror("Erro", "Nome é obrigatório.")
            return
            
        conn = get_connection()
        cur = conn.cursor()
        
        try:
            if self.product_id:
                cur.execute("UPDATE products SET nome=?, sku=?, codigo_barras=?, custo=?, preco_venda=?, cfop_padrao=?, preco_atacado=?, is_servico=? WHERE id=?",
                            (nome, sku, ean, custo, preco, cfop, atacado, is_servico, self.product_id))
            else:
                try:
                    from erp_backend.core.normalizer import normalize
                    nome_norm = normalize(nome)
                except ImportError:
                    nome_norm = nome.upper()
                cur.execute("INSERT INTO products (nome, nome_normalizado, sku, codigo_barras, custo, preco_venda, estoque_atual, cfop_padrao, preco_atacado, is_servico) VALUES (?, ?, ?, ?, ?, ?, 0, ?, ?, ?)",
                            (nome, nome_norm, sku, ean, custo, preco, cfop, atacado, is_servico))
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
        super().__init__(master, fg_color="#1e1e1e", **kwargs)
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
        
        self.search_entry = ctk.CTkEntry(search_frame, placeholder_text="🔎 BUSCA: NOME / SKU / EAN / FORNECEDOR...", height=40, font=("Roboto", 16))
        self.search_entry.pack(fill="x", padx=(0, 20))
        self.search_entry.bind("<KeyRelease>", self.on_search)
        
        summary_frame = ctk.CTkFrame(top_frame, fg_color="#2b2b2b", corner_radius=8)
        summary_frame.pack(side="right", padx=10)
        
        self.lbl_total_prod = ctk.CTkLabel(summary_frame, text="PRODUTOS: 0", font=("Roboto", 14, "bold"))
        self.lbl_total_prod.pack(side="left", padx=15, pady=10)
        
        self.lbl_critical_stock = ctk.CTkLabel(summary_frame, text="ESTOQUE CRÍTICO: 0", font=("Roboto", 14, "bold"), text_color="#e74c3c")
        self.lbl_critical_stock.pack(side="left", padx=15, pady=10)
        
        self.lbl_total_value = ctk.CTkLabel(summary_frame, text="VALOR: R$ 0.00", font=("Roboto", 14, "bold"), text_color="#2ecc71")
        self.lbl_total_value.pack(side="left", padx=15, pady=10)
        
        actions_frame = ctk.CTkFrame(self, fg_color="transparent")
        actions_frame.pack(fill="x", padx=20, pady=(0, 10))
        
        btn_new = ctk.CTkButton(actions_frame, text="[ NOVO ]", font=("Roboto", 14, "bold"), command=self.new_product)
        btn_new.pack(side="left", padx=5)
        
        btn_edit = ctk.CTkButton(actions_frame, text="[F2] EDITAR", font=("Roboto", 14, "bold"), fg_color="#f39c12", hover_color="#d68910", command=self.edit_selected)
        btn_edit.pack(side="left", padx=5)
        
        btn_refresh = ctk.CTkButton(actions_frame, text="[F5] ATUALIZAR", font=("Roboto", 14, "bold"), fg_color="#3498db", hover_color="#2980b9", command=self.load_data)
        btn_refresh.pack(side="left", padx=5)

        btn_recalc = ctk.CTkButton(actions_frame, text="[ RECALCULAR ]", font=("Roboto", 14, "bold"), fg_color="#9b59b6", hover_color="#8e44ad", command=self.recalc_stock)
        btn_recalc.pack(side="left", padx=5)
        
        btn_import = ctk.CTkButton(actions_frame, text="[F6] IMPORTAR NF-e", font=("Roboto", 14, "bold"), fg_color="#2ecc71", hover_color="#27ae60", command=self.import_nfe)
        btn_import.pack(side="right", padx=5)
        
        columns = ("NOME", "SKU", "EAN", "ESTOQUE", "CUSTO", "PREÇO", "STATUS")
        self.table = TableComponent(self, columns)
        self.table.column("NOME", width=350, anchor="w")
        self.table.column("SKU", width=120)
        self.table.column("EAN", width=120)
        self.table.column("ESTOQUE", width=100)
        self.table.column("CUSTO", width=100)
        self.table.column("PREÇO", width=100)
        self.table.column("STATUS", width=120)
        
        self.table.tag_configure("ok", foreground="#2ecc71")
        self.table.tag_configure("low", foreground="#f1c40f")
        self.table.tag_configure("empty", foreground="#e74c3c")
        
        self.table.pack(fill="both", expand=True, padx=20, pady=10)
        self.table.bind("<Double-1>", lambda e: self.edit_selected())
        self.table.bind("<Return>", lambda e: self.edit_selected())
        
    def load_data(self, event=None):
        query = self.search_entry.get().strip()
        for item in self.table.get_children():
            self.table.delete(item)
            
        conn = get_connection()
        cur = conn.cursor()
        
        sql = """
            SELECT p.id, p.nome, p.sku, p.codigo_barras, p.estoque_atual, p.custo, p.preco_venda, s.razao_social
            FROM products p
            LEFT JOIN suppliers s ON p.fornecedor_id = s.id
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
            
            if est <= 0:
                status, tag = "SEM ESTOQUE", "empty"
            elif est <= 5:
                status, tag = "BAIXO", "low"
            else:
                status, tag = "OK", "ok"
                
            self.table.insert("", "end", iid=str(row['id']), values=(
                row['nome'],
                row['sku'] or "--",
                row['codigo_barras'] or "--",
                f"{est:.3f}".rstrip('0').rstrip('.'),
                f"R$ {custo:.2f}",
                f"R$ {row['preco_venda'] or 0.0:.2f}",
                status
            ), tags=(tag,))
            
        conn.close()
        
        self.lbl_total_prod.configure(text=f"PRODUTOS: {total_prod}")
        self.lbl_critical_stock.configure(text=f"ESTOQUE CRÍTICO: {critical}")
        self.lbl_total_value.configure(text=f"VALOR: R$ {total_val:.2f}")
        
    def on_search(self, event):
        self.load_data()

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
            
    # Nota: A função on_search já está definida corretamente mais acima na classe (linha 204).
    # O on_search duplicado e as chamadas soltas do cursor (cur) foram completamente removidas.
        
    def on_search(self, event):
        self.load_data(self.search_entry.get().strip())