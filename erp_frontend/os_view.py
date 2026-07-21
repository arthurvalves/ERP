import customtkinter as ctk
from tkinter import messagebox
from erp_backend.utils.db import transaction
from erp_frontend.components.table import TableComponent
from erp_backend.utils.db import get_connection
from erp_backend.services.sales_service import create_sale, add_sale_item

class OSModal(ctk.CTkToplevel):
    def __init__(self, master, os_id=None, on_save=None):
        super().__init__(master)
        self.title(f"Ordem de Serviço #{os_id}" if os_id else "Nova Ordem de Serviço")
        self.geometry("950x750")
        self.transient(master)
        self.grab_set()

        self.os_id = os_id
        self.on_save = on_save
        self.items = [] 
        
        self.setup_ui()
        self.load_data()
        self.bind("<Escape>", lambda e: self.destroy())

    def setup_ui(self):
        self.frame = ctk.CTkFrame(self)
        self.frame.pack(fill="both", expand=True, padx=15, pady=15)

        # --- CABEÇALHO (INFO VEÍCULO / STATUS) ---
        f_header = ctk.CTkFrame(self.frame, fg_color="#2b2b2b", corner_radius=8)
        f_header.pack(fill="x", pady=(0, 10), ipady=5)

        f_placa = ctk.CTkFrame(f_header, fg_color="transparent")
        f_placa.pack(side="left", expand=True, fill="x", padx=10)
        ctk.CTkLabel(f_placa, text="Placa:", font=("Roboto", 12, "bold")).pack(anchor="w")
        self.ent_placa = ctk.CTkEntry(f_placa, font=("Roboto", 16))
        self.ent_placa.pack(fill="x")

        f_veiculo = ctk.CTkFrame(f_header, fg_color="transparent")
        f_veiculo.pack(side="left", expand=True, fill="x", padx=10)
        ctk.CTkLabel(f_veiculo, text="Veículo/Modelo:", font=("Roboto", 12, "bold")).pack(anchor="w")
        self.ent_veiculo = ctk.CTkEntry(f_veiculo, font=("Roboto", 16))
        self.ent_veiculo.pack(fill="x")

        f_status = ctk.CTkFrame(f_header, fg_color="transparent")
        f_status.pack(side="left", expand=True, fill="x", padx=10)
        ctk.CTkLabel(f_status, text="Status do Atendimento:", font=("Roboto", 12, "bold")).pack(anchor="w")
        self.cb_status = ctk.CTkOptionMenu(f_status, values=["Aberta", "Em Andamento", "Aguardando Peça", "Concluída", "Faturada", "Cancelada"], font=("Roboto", 14))
        self.cb_status.pack(fill="x")

        # --- DESCRIÇÃO DO SERVIÇO ---
        ctk.CTkLabel(self.frame, text="Serviço a ser executado / Relato do Cliente:", font=("Roboto", 14, "bold")).pack(anchor="w", padx=5)
        self.txt_desc = ctk.CTkTextbox(self.frame, height=80, font=("Roboto", 14))
        self.txt_desc.pack(fill="x", padx=5, pady=(0, 15))

        # --- ADIÇÃO DE PEÇAS E MÃO DE OBRA ---
        f_add = ctk.CTkFrame(self.frame, fg_color="#1a1a1a", corner_radius=8)
        f_add.pack(fill="x", padx=5, pady=(0, 10), ipady=5)
        
        ctk.CTkLabel(f_add, text="Inserir Peça ou Serviço:", font=("Roboto", 12)).pack(side="left", padx=10)
        self.ent_code = ctk.CTkEntry(f_add, placeholder_text="SKU ou Cód. Barras", width=250, font=("Roboto", 14))
        self.ent_code.pack(side="left", padx=5)
        self.ent_code.bind("<Return>", lambda e: self.add_item())
        
        ctk.CTkLabel(f_add, text="Qtd:", font=("Roboto", 12)).pack(side="left", padx=5)
        self.ent_qtd = ctk.CTkEntry(f_add, width=60, font=("Roboto", 14))
        self.ent_qtd.insert(0, "1")
        self.ent_qtd.pack(side="left", padx=5)
        self.ent_qtd.bind("<Return>", lambda e: self.add_item())

        btn_add = ctk.CTkButton(f_add, text="ADICIONAR", fg_color="#3498db", hover_color="#2980b9", font=("Roboto", 14, "bold"), command=self.add_item)
        btn_add.pack(side="left", padx=10)
        
        ctk.CTkLabel(f_add, text="[DEL] para remover item selecionado", text_color="#7f8c8d", font=("Roboto", 10)).pack(side="right", padx=10)

        # --- TABELA DE ITENS ---
        columns = ("TIPO", "CÓDIGO", "NOME", "QTD", "UNIT", "TOTAL")
        self.table = TableComponent(self.frame, columns)
        self.table.column("TIPO", width=120)
        self.table.column("CÓDIGO", width=120)
        self.table.column("NOME", width=350, anchor="w")
        self.table.column("QTD", width=60)
        self.table.column("UNIT", width=100)
        self.table.column("TOTAL", width=100)
        
        self.table.tag_configure("peca", foreground="#3498db")
        self.table.tag_configure("servico", foreground="#9b59b6")
        
        self.table.pack(fill="both", expand=True, padx=5, pady=5)
        self.table.bind("<Delete>", self.remove_item)

        # --- RODAPÉ (CUSTOS E COBRANÇA) ---
        f_footer = ctk.CTkFrame(self.frame, fg_color="transparent")
        f_footer.pack(fill="x", side="bottom", padx=5, pady=10)

        f_totals = ctk.CTkFrame(f_footer, fg_color="#2b2b2b", corner_radius=8)
        f_totals.pack(side="left", fill="y", ipadx=10, ipady=5)
        
        self.lbl_tot_pecas = ctk.CTkLabel(f_totals, text="Peças: R$ 0.00", font=("Roboto", 14), text_color="#3498db")
        self.lbl_tot_pecas.pack(anchor="w", padx=10, pady=2)
        self.lbl_tot_serv = ctk.CTkLabel(f_totals, text="Mão de Obra: R$ 0.00", font=("Roboto", 14), text_color="#9b59b6")
        self.lbl_tot_serv.pack(anchor="w", padx=10, pady=2)
        self.lbl_tot_geral = ctk.CTkLabel(f_totals, text="TOTAL GERAL: R$ 0.00", font=("Roboto", 18, "bold"), text_color="#2ecc71")
        self.lbl_tot_geral.pack(anchor="w", padx=10, pady=(5, 2))

        f_actions = ctk.CTkFrame(f_footer, fg_color="transparent")
        f_actions.pack(side="right", fill="y")

        ctk.CTkLabel(f_actions, text="Forma Pgto:", font=("Roboto", 12)).pack(side="left", padx=5)
        self.cb_pagamento = ctk.CTkOptionMenu(f_actions, values=["DINHEIRO", "PIX", "CARTÃO CRÉDITO", "CARTÃO DÉBITO", "MISTO"], width=140)
        self.cb_pagamento.pack(side="left", padx=5)

        btn_faturar = ctk.CTkButton(f_actions, text="FATURAR E COBRAR", font=("Roboto", 16, "bold"), height=45, fg_color="#2ecc71", hover_color="#27ae60", command=self.faturar)
        btn_faturar.pack(side="right", padx=5)

        btn_share = ctk.CTkButton(f_actions, text="AÇÕES (WHATSAPP / PDF)", font=("Roboto", 16, "bold"), height=45, fg_color="#8e44ad", hover_color="#9b59b6", command=self.open_post_action)
        btn_share.pack(side="right", padx=5)

        btn_salvar = ctk.CTkButton(f_actions, text="SALVAR OS", font=("Roboto", 16, "bold"), height=45, fg_color="#f39c12", hover_color="#d68910", command=self.save)
        btn_salvar.pack(side="right", padx=5)

    def load_data(self):
        if not self.os_id:
            self.refresh_items()
            return
            
        conn = get_connection()
        cur = conn.cursor()
        cur.execute("SELECT * FROM service_orders WHERE id = ?", (self.os_id,))
        os_data = cur.fetchone()
        if os_data:
            self.ent_placa.insert(0, os_data['placa'] or "")
            self.ent_veiculo.insert(0, os_data['veiculo'] or "")
            self.cb_status.set(os_data['status'])
            self.txt_desc.insert("1.0", os_data['descricao_problema'] or "")

        cur.execute("""
            SELECT i.*, p.nome, p.sku, p.codigo_barras 
            FROM service_order_items i 
            JOIN products p ON i.product_id = p.id 
            WHERE i.service_order_id = ?
        """, (self.os_id,))
        
        for row in cur.fetchall():
            self.items.append({
                'product_id': row['product_id'],
                'tipo': row['tipo'],
                'nome': row['nome'],
                'codigo': row['sku'] or row['codigo_barras'],
                'quantidade': row['quantidade'],
                'preco_unitario': row['preco_unitario'],
                'desconto_item': row['desconto_item']
            })
        conn.close()
        self.refresh_items()

    def add_item(self):
        code = self.ent_code.get().strip()
        try:
            qtd = float(self.ent_qtd.get().replace(",", "."))
        except ValueError:
            qtd = 1.0

        if not code:
            return

        conn = get_connection()
        cur = conn.cursor()
        cur.execute("SELECT id, nome, sku, codigo_barras, preco_venda, is_servico FROM products WHERE sku = ? OR codigo_barras = ?", (code, code))
        row = cur.fetchone()
        conn.close()

        if not row:
            messagebox.showwarning("Não Encontrado", f"Peça/Serviço '{code}' não localizado no sistema.")
            return

        tipo = 'servico' if row['is_servico'] else 'peca'
        self.items.append({
            'product_id': row['id'],
            'tipo': tipo,
            'nome': row['nome'],
            'codigo': row['sku'] or row['codigo_barras'],
            'quantidade': qtd,
            'preco_unitario': row['preco_venda'],
            'desconto_item': 0.0
        })
        
        self.ent_code.delete(0, 'end')
        self.ent_qtd.delete(0, 'end')
        self.ent_qtd.insert(0, "1")
        self.refresh_items()
        self.ent_code.focus_set()

    def remove_item(self, event=None):
        selected = self.table.selection()
        if not selected: return
        idx = int(selected[0])
        if 0 <= idx < len(self.items):
            del self.items[idx]
            self.refresh_items()

    def refresh_items(self):
        for item in self.table.get_children():
            self.table.delete(item)
            
        t_pecas = 0.0
        t_servicos = 0.0
        
        for idx, item in enumerate(self.items):
            subtotal = (item['quantidade'] * item['preco_unitario']) - item.get('desconto_item', 0.0)
            if item['tipo'] == 'peca':
                t_pecas += subtotal
                tipo_str, tag = "PEÇA", "peca"
            else:
                t_servicos += subtotal
                tipo_str, tag = "MÃO DE OBRA", "servico"
                
            self.table.insert("", "end", iid=str(idx), values=(
                tipo_str, item['codigo'], item['nome'],
                f"{item['quantidade']:.2f}", f"R$ {item['preco_unitario']:.2f}", f"R$ {subtotal:.2f}"
            ), tags=(tag,))
            
        self.lbl_tot_pecas.configure(text=f"Peças: R$ {t_pecas:.2f}")
        self.lbl_tot_serv.configure(text=f"Mão de Obra: R$ {t_servicos:.2f}")
        self.lbl_tot_geral.configure(text=f"TOTAL GERAL: R$ {(t_pecas + t_servicos):.2f}")

    def save(self) -> bool:
        placa = self.ent_placa.get().strip()
        veiculo = self.ent_veiculo.get().strip()
        status = self.cb_status.get()
        desc = self.txt_desc.get("1.0", "end-1c").strip()

        t_pecas = sum((i['quantidade'] * i['preco_unitario']) - i.get('desconto_item', 0.0) for i in self.items if i['tipo'] == 'peca')
        t_servicos = sum((i['quantidade'] * i['preco_unitario']) - i.get('desconto_item', 0.0) for i in self.items if i['tipo'] == 'servico')
        t_geral = t_pecas + t_servicos

        conn = get_connection()
        cur = conn.cursor()
        try:
            if self.os_id:
                cur.execute("UPDATE service_orders SET placa=?, veiculo=?, descricao_problema=?, status=?, total_pecas=?, total_servicos=?, total_geral=? WHERE id=?",
                            (placa, veiculo, desc, status, t_pecas, t_servicos, t_geral, self.os_id))
                cur.execute("DELETE FROM service_order_items WHERE service_order_id=?", (self.os_id,))
            else:
                cur.execute("INSERT INTO service_orders (placa, veiculo, descricao_problema, status, total_pecas, total_servicos, total_geral) VALUES (?, ?, ?, ?, ?, ?, ?)",
                            (placa, veiculo, desc, status, t_pecas, t_servicos, t_geral))
                self.os_id = cur.lastrowid

            for item in self.items:
                cur.execute("INSERT INTO service_order_items (service_order_id, product_id, tipo, quantidade, preco_unitario, desconto_item) VALUES (?, ?, ?, ?, ?, ?)",
                            (self.os_id, item['product_id'], item['tipo'], item['quantidade'], item['preco_unitario'], item.get('desconto_item', 0.0)))
            conn.commit()
            if self.on_save: self.on_save()
            return True
        except Exception as e:
            conn.rollback()
            messagebox.showerror("Erro ao Salvar OS", str(e))
            return False
        finally:
            conn.close()
            
    def open_post_action(self):
        if not self.save(): return
        
        os_data = {
            'id': self.os_id,
            'placa': self.ent_placa.get().strip(),
            'veiculo': self.ent_veiculo.get().strip(),
            'status': self.cb_status.get(),
            'descricao_problema': self.txt_desc.get("1.0", "end-1c").strip(),
            'total_pecas': sum((i['quantidade'] * i['preco_unitario']) - i.get('desconto_item', 0.0) for i in self.items if i['tipo'] == 'peca'),
            'total_servicos': sum((i['quantidade'] * i['preco_unitario']) - i.get('desconto_item', 0.0) for i in self.items if i['tipo'] == 'servico')
        }
        os_data['total_geral'] = os_data['total_pecas'] + os_data['total_servicos']
        
        from erp_frontend.os_post_action_modal import OSPostActionModal
        OSPostActionModal(self.winfo_toplevel(), os_data, self.items)

    def faturar(self):
        if self.cb_status.get() == "Faturada":
            messagebox.showwarning("Aviso", "Esta Ordem de Serviço já foi faturada no caixa.")
            return
            
        if not self.items:
            messagebox.showwarning("Aviso", "A OS não possui itens ou serviços para ser faturada.")
            return
            
        if not self.save(): return
        
        # 1. Calcula o total somando peças e serviços
        t_pecas = sum((i['quantidade'] * i['preco_unitario']) - i.get('desconto_item', 0.0) for i in self.items if i['tipo'] == 'peca')
        t_servicos = sum((i['quantidade'] * i['preco_unitario']) - i.get('desconto_item', 0.0) for i in self.items if i['tipo'] == 'servico')
        t_geral = t_pecas + t_servicos
        
        from erp_backend.utils.db import transaction
        from erp_backend.services.sales_service import create_sale, add_sale_item
        
        try:
            # 2. Inicia a transação atómica
            with transaction() as conn:
                # Passamos None no customer_id porque a OS ainda não exige cadastro rígido de cliente (usa apenas a placa)
                sale_id = create_sale(None, t_geral, 0.0, self.cb_pagamento.get(), conn=conn)
                
                # Insere os itens da OS na Venda (o que vai acionar a nossa verificação de stock)
                for item in self.items:
                    add_sale_item(sale_id, item['product_id'], item['quantidade'], item['preco_unitario'], item.get('desconto_item', 0.0), conn=conn)
                
                # Atualiza o status da OS na mesma transação
                conn.execute("UPDATE service_orders SET status='Faturada', data_fechamento=CURRENT_TIMESTAMP WHERE id=?", (self.os_id,))
                
            # 3. Se chegou aqui, nada falhou! Atualiza a interface
            self.cb_status.set("Faturada")
            if self.on_save: self.on_save()
            messagebox.showinfo("Sucesso", "OS Faturada! O stock das peças foi baixado e a venda registada no caixa.")
            self.destroy()
            
        except ValueError as ve:
            # Captura a nossa exceção de "Stock Insuficiente"
            messagebox.showwarning("Aviso de Stock", str(ve))
        except Exception as e:
            messagebox.showerror("Erro Crítico", f"Falha ao faturar a OS. Nenhuma alteração foi guardada.\n\nDetalhes: {e}")

class OSView(ctk.CTkFrame):
    def __init__(self, master, app_window, **kwargs):
        super().__init__(master, fg_color="#1e1e1e", **kwargs)
        self.app_window = app_window
        self.setup_ui()
        self.load_data()
        
    def setup_ui(self):
        top_frame = ctk.CTkFrame(self, fg_color="transparent")
        top_frame.pack(fill="x", padx=20, pady=10)
        
        self.search_entry = ctk.CTkEntry(top_frame, placeholder_text="🔎 BUSCA: PLACA OU VEÍCULO...", height=40, font=("Roboto", 16))
        self.search_entry.pack(side="left", fill="x", expand=True, padx=(0, 20))
        self.search_entry.bind("<KeyRelease>", lambda e: self.load_data())
        
        btn_new = ctk.CTkButton(top_frame, text="[ NOVA O.S. ]", font=("Roboto", 14, "bold"), fg_color="#2ecc71", hover_color="#27ae60", command=self.new_os)
        btn_new.pack(side="right", padx=5)
        
        btn_edit = ctk.CTkButton(top_frame, text="[ EDITAR ]", font=("Roboto", 14, "bold"), fg_color="#f39c12", hover_color="#d68910", command=self.edit_selected)
        btn_edit.pack(side="right", padx=5)
        
        btn_refresh = ctk.CTkButton(top_frame, text="[ ATUALIZAR ]", font=("Roboto", 14, "bold"), fg_color="#3498db", hover_color="#2980b9", command=self.load_data)
        btn_refresh.pack(side="right", padx=5)
        
        columns = ("OS #", "PLACA", "VEÍCULO", "STATUS", "TOTAL PEÇAS", "TOTAL M.O.", "TOTAL GERAL", "DATA ABERTURA")
        self.table = TableComponent(self, columns)
        self.table.pack(fill="both", expand=True, padx=20, pady=10)
        self.table.bind("<Double-1>", lambda e: self.edit_selected())
        
    def load_data(self):
        query = self.search_entry.get().strip()
        for item in self.table.get_children():
            self.table.delete(item)
            
        conn = get_connection()
        cur = conn.cursor()
        
        sql = "SELECT * FROM service_orders"
        params = ()
        if query:
            sql += " WHERE placa LIKE ? OR veiculo LIKE ?"
            q = f"%{query}%"
            params = (q, q)
        sql += " ORDER BY id DESC LIMIT 100"
        
        cur.execute(sql, params)
        for row in cur.fetchall():
            self.table.insert("", "end", iid=str(row['id']), values=(
                f"{row['id']:05d}",
                row['placa'] or "--",
                row['veiculo'] or "--",
                row['status'],
                f"R$ {row['total_pecas']:.2f}",
                f"R$ {row['total_servicos']:.2f}",
                f"R$ {row['total_geral']:.2f}",
                row['data_abertura'][:16] if row['data_abertura'] else "--"
            ))
        conn.close()
        
    def new_os(self):
        OSModal(self, on_save=self.load_data)
        
    def edit_selected(self):
        selected = self.table.selection()
        if not selected: return
        os_id = int(selected[0])
        OSModal(self, os_id=os_id, on_save=self.load_data)