import customtkinter as ctk
from tkinter import messagebox, simpledialog, ttk, Menu
from erp_frontend.components.table import TableComponent
from erp_backend.utils.db import get_connection
from erp_backend.services.sales_service import create_sale, add_sale_item
from erp_backend.services import vehicle_service, customer_service, user_service
from erp_frontend.modals.customer_search_modal import CustomerSearchModal
from erp_frontend.modals.vehicle_modal import VehicleModal
from erp_frontend import theme

class OSModal(ctk.CTkToplevel):
    def __init__(self, master, os_id=None, on_save=None):
        super().__init__(master)
        self.title(f"Ordem de Serviço #{os_id}" if os_id else "Nova Ordem de Serviço")
        self.configure(fg_color=theme.BG)
        self.transient(master)
        self.grab_set()

        self.os_id = os_id
        self.on_save = on_save
        self.items = []
        self.customer_id = None
        self.vehicle_id = None
        self.technicians = user_service.get_technicians()

        self.setup_ui()
        self.load_data()
        self.bind("<Escape>", lambda e: self.destroy())
        self.after(10, self._center_window)

    def _center_window(self):
        self.update_idletasks()
        width = 1200
        height = 800
        screen_width = self.winfo_screenwidth()
        screen_height = self.winfo_screenheight()
        x = (screen_width // 2) - (width // 2)
        y = (screen_height // 2) - (height // 2)
        self.geometry(f'{width}x{height}+{x}+{y}')
        self.resizable(False, False)

    def setup_ui(self):
        self.frame = ctk.CTkFrame(self, fg_color=theme.BG)
        self.frame.pack(fill="both", expand=True, padx=15, pady=15)

        f_header = ctk.CTkFrame(self.frame, **theme.card_frame_kwargs())
        f_header.pack(fill="x", pady=(0, 10), ipady=5)

        f_placa = ctk.CTkFrame(f_header, fg_color="transparent")
        f_placa.pack(side="left", expand=True, fill="x", padx=10)
        ctk.CTkLabel(f_placa, text="Placa (Pressione ENTER para buscar):", font=theme.font_bold(12), text_color=theme.TEXT_MUTED).pack(anchor="w")
        self.ent_placa = ctk.CTkEntry(f_placa, font=theme.font_body(16), fg_color=theme.CARD_ALT, border_color=theme.SECONDARY)
        self.ent_placa.pack(fill="x")
        self.ent_placa.bind("<Return>", self.search_vehicle_by_plate)

        self.lbl_vehicle_info = ctk.CTkLabel(f_header, text="Veículo: --", font=theme.font_body(14), text_color=theme.TEXT, anchor="w")
        self.lbl_vehicle_info.pack(side="left", expand=True, fill="x", padx=10)

        self.lbl_customer_info = ctk.CTkLabel(f_header, text="Cliente: --", font=theme.font_body(14), text_color=theme.TEXT, anchor="w")
        self.lbl_customer_info.pack(side="left", expand=True, fill="x", padx=10)

        self.btn_edit_vehicle = ctk.CTkButton(f_header, text="EDITAR VEÍCULO", command=self.edit_vehicle, state="disabled",
                                               **theme.btn_secondary(font=theme.font_bold(12)))
        self.btn_edit_vehicle.pack(side="left", padx=10)

        f_km = ctk.CTkFrame(f_header, fg_color="transparent")
        f_km.pack(side="left", expand=True, fill="x", padx=10)
        ctk.CTkLabel(f_km, text="KM Atual:", font=theme.font_bold(12), text_color=theme.TEXT_MUTED).pack(anchor="w")
        self.ent_km = ctk.CTkEntry(f_km, font=theme.font_body(16), fg_color=theme.CARD_ALT, border_color=theme.SECONDARY)
        self.ent_km.pack(fill="x")

        f_status = ctk.CTkFrame(f_header, fg_color="transparent")
        f_status.pack(side="left", expand=True, fill="x", padx=10)
        ctk.CTkLabel(f_status, text="Status do Atendimento:", font=theme.font_bold(12), text_color=theme.TEXT_MUTED).pack(anchor="w")
        self.cb_status = ctk.CTkOptionMenu(f_status, values=["Aberta", "Em Andamento", "Aguardando Peça", "Concluída", "Faturada", "Cancelada"],
                                            font=theme.font_body(14), fg_color=theme.SECONDARY, button_color=theme.SECONDARY,
                                            button_hover_color=theme.PRIMARY)
        self.cb_status.pack(fill="x")

        f_schedule = ctk.CTkFrame(self.frame, **theme.card_frame_kwargs())
        f_schedule.pack(fill="x", pady=10, ipady=5)

        ctk.CTkLabel(f_schedule, text="Agendamento:", font=theme.font_bold(12), text_color=theme.TEXT_MUTED).pack(side="left", padx=10)

        ctk.CTkLabel(f_schedule, text="Data:", font=theme.font_body(12), text_color=theme.TEXT_MUTED).pack(side="left", padx=(10, 5))
        self.ent_schedule_date = ctk.CTkEntry(f_schedule, placeholder_text="DD/MM/AAAA", width=120, fg_color=theme.CARD_ALT, border_color=theme.SECONDARY)
        self.ent_schedule_date.pack(side="left")

        ctk.CTkLabel(f_schedule, text="Hora:", font=theme.font_body(12), text_color=theme.TEXT_MUTED).pack(side="left", padx=(10, 5))
        self.ent_schedule_time = ctk.CTkEntry(f_schedule, placeholder_text="HH:MM", width=80, fg_color=theme.CARD_ALT, border_color=theme.SECONDARY)
        self.ent_schedule_time.pack(side="left")

        ctk.CTkLabel(self.frame, text="Serviço a ser executado / Relato do Cliente:", font=theme.font_bold(14), text_color=theme.TEXT).pack(anchor="w", padx=5)
        self.txt_desc = ctk.CTkTextbox(self.frame, height=80, font=theme.font_body(14), fg_color=theme.CARD_ALT)
        self.txt_desc.pack(fill="x", padx=5, pady=(0, 15))

        f_add = ctk.CTkFrame(self.frame, fg_color=theme.CARD_ALT, corner_radius=theme.RADIUS)
        f_add.pack(fill="x", padx=5, pady=(0, 10), ipady=5)

        ctk.CTkLabel(f_add, text="Inserir Peça ou Serviço:", font=theme.font_body(12), text_color=theme.TEXT_MUTED).pack(side="left", padx=10)
        self.ent_code = ctk.CTkEntry(f_add, placeholder_text="SKU ou Cód. Barras", width=250, font=theme.font_body(14), fg_color=theme.CARD, border_color=theme.SECONDARY)
        self.ent_code.pack(side="left", padx=5)
        self.ent_code.bind("<Return>", lambda e: self.add_item())

        ctk.CTkLabel(f_add, text="Qtd:", font=theme.font_body(12), text_color=theme.TEXT_MUTED).pack(side="left", padx=5)
        self.ent_qtd = ctk.CTkEntry(f_add, width=60, font=theme.font_body(14), fg_color=theme.CARD, border_color=theme.SECONDARY)
        self.ent_qtd.insert(0, "1")
        self.ent_qtd.pack(side="left", padx=5)
        self.ent_qtd.bind("<Return>", lambda e: self.add_item())

        btn_add = ctk.CTkButton(f_add, text="ADICIONAR", command=self.add_item, **theme.btn_primary())
        btn_add.pack(side="left", padx=10)

        ctk.CTkLabel(f_add, text="Técnico:", font=theme.font_body(12), text_color=theme.TEXT_MUTED).pack(side="left", padx=(20, 5))
        technician_names = [tech['username'] for tech in self.technicians]
        self.cb_technician = ctk.CTkOptionMenu(f_add, values=technician_names, width=150, font=theme.font_body(14),
                                                fg_color=theme.SECONDARY, button_color=theme.SECONDARY, button_hover_color=theme.PRIMARY)
        if technician_names: self.cb_technician.set(technician_names[0])
        self.cb_technician.pack(side="left")

        ctk.CTkLabel(f_add, text="[DEL] para remover item selecionado", text_color=theme.TEXT_MUTED, font=theme.font_body(10)).pack(side="right", padx=10)

        columns = ("TIPO", "CÓDIGO", "NOME", "QTD", "UNIT", "TOTAL")
        self.table = TableComponent(self.frame, columns)
        self.table.column("TIPO", width=120)
        self.table.column("CÓDIGO", width=120)
        self.table.column("NOME", width=300, anchor="w")
        self.table.column("QTD", width=60)
        self.table.column("UNIT", width=100)
        self.table.column("TOTAL", width=100)

        self.table.tag_configure("peca", foreground=theme.INFO)
        self.table.tag_configure("servico", foreground="#a855f7")

        self.table.pack(fill="both", expand=True, padx=5, pady=5)
        self.table.bind("<Delete>", self.remove_item)

        f_footer = ctk.CTkFrame(self.frame, fg_color="transparent")
        f_footer.pack(fill="x", side="bottom", padx=5, pady=10)

        f_totals = ctk.CTkFrame(f_footer, **theme.card_frame_kwargs())
        f_totals.pack(side="left", fill="y", ipadx=10, ipady=5)

        self.lbl_tot_pecas = ctk.CTkLabel(f_totals, text="Peças: R$ 0.00", font=theme.font_body(14), text_color=theme.INFO)
        self.lbl_tot_pecas.pack(anchor="w", padx=10, pady=2)
        self.lbl_tot_serv = ctk.CTkLabel(f_totals, text="Mão de Obra: R$ 0.00", font=theme.font_body(14), text_color="#a855f7")
        self.lbl_tot_serv.pack(anchor="w", padx=10, pady=2)
        self.lbl_tot_geral = ctk.CTkLabel(f_totals, text="TOTAL GERAL: R$ 0.00", font=theme.font_title(18), text_color=theme.PRIMARY)
        self.lbl_tot_geral.pack(anchor="w", padx=10, pady=(5, 2))

        f_actions = ctk.CTkFrame(f_footer, fg_color="transparent")
        f_actions.pack(side="right", fill="y")

        ctk.CTkLabel(f_actions, text="Forma Pgto:", font=theme.font_body(12), text_color=theme.TEXT_MUTED).pack(side="left", padx=5)
        self.cb_pagamento = ctk.CTkOptionMenu(f_actions, values=["DINHEIRO", "PIX", "CARTÃO CRÉDITO", "CARTÃO DÉBITO", "CREDIARIO", "MISTO"],
                                               width=140, command=self.toggle_installments_entry,
                                               fg_color=theme.SECONDARY, button_color=theme.SECONDARY, button_hover_color=theme.PRIMARY)
        self.cb_pagamento.pack(side="left", padx=5)

        self.f_installments = ctk.CTkFrame(f_actions, fg_color="transparent")
        ctk.CTkLabel(self.f_installments, text="Parcelas:", font=theme.font_body(12), text_color=theme.TEXT_MUTED).pack(side="left", padx=5)
        self.ent_installments = ctk.CTkEntry(self.f_installments, width=60, font=theme.font_body(14), fg_color=theme.CARD, border_color=theme.SECONDARY)
        self.ent_installments.insert(0, "1")
        self.ent_installments.pack(side="left")

        btn_faturar = ctk.CTkButton(f_actions, text="FATURAR E COBRAR", height=45, command=self.faturar, **theme.btn_success(font=theme.font_bold(16)))
        btn_faturar.pack(side="right", padx=5)

        btn_share = ctk.CTkButton(f_actions, text="AÇÕES (WHATSAPP / PDF)", height=45, command=self.open_post_action,
                                   **theme.btn_secondary(fg_color="#a855f7", hover_color="#9333ea", text_color="#ffffff", font=theme.font_bold(16)))
        btn_share.pack(side="right", padx=5)

        btn_salvar = ctk.CTkButton(f_actions, text="SALVAR OS", height=45, command=self.save, **theme.btn_primary(font=theme.font_bold(16)))
        btn_salvar.pack(side="right", padx=5)

    def load_data(self):
        if not self.os_id:
            self.refresh_items()
            return

        conn = get_connection()
        cur = conn.cursor()
        cur.execute("SELECT * FROM service_orders WHERE id = ?", (self.os_id,))
        os_data = dict(cur.fetchone())
        if os_data:
            self.cb_status.set(os_data['status'])
            self.txt_desc.insert("1.0", os_data['descricao_problema'] or "")
            self.customer_id = os_data.get('customer_id')
            self.vehicle_id = os_data.get('vehicle_id')

            if self.vehicle_id:
                vehicle = vehicle_service.get_vehicle_by_id(self.vehicle_id, conn=conn)
                if vehicle:
                    self.ent_placa.insert(0, vehicle.plate)
                    self.ent_km.insert(0, str(vehicle.current_km or ''))
                    self.update_vehicle_and_customer_info(vehicle, conn=conn)

            if os_data.get('scheduled_start_time'):
                from datetime import datetime
                dt = datetime.strptime(os_data['scheduled_start_time'], '%Y-%m-%d %H:%M:%S')
                self.ent_schedule_date.insert(0, dt.strftime('%d/%m/%Y'))
                self.ent_schedule_time.insert(0, dt.strftime('%H:%M'))

        cur.execute("""
            SELECT i.*, p.nome, p.sku, p.codigo_barras, u.username as technician_name
            FROM service_order_items i 
            JOIN products p ON i.product_id = p.id 
            LEFT JOIN users u ON i.technician_id = u.id
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
                'desconto_item': row['desconto_item'],
                'technician_id': row['technician_id'],
                'technician_name': row['technician_name']
            })
        conn.close()
        self.refresh_items()

    def search_vehicle_by_plate(self, event=None):
        plate = self.ent_placa.get().strip().upper()
        if not plate: return

        vehicle = vehicle_service.get_vehicle_by_plate(plate)
        if vehicle:
            self.update_vehicle_and_customer_info(vehicle)
        else:
            if messagebox.askyesno("Veículo não encontrado", f"A placa '{plate}' não está registada.\nDeseja adicionar um novo veículo?"):
                self.edit_vehicle(plate_suggestion=plate)

    def update_vehicle_and_customer_info(self, vehicle, conn=None):
        self.vehicle_id = vehicle.id
        self.customer_id = vehicle.customer_id
        self.lbl_vehicle_info.configure(text=f"Veículo: {vehicle.brand or ''} {vehicle.model or ''} ({vehicle.year or ''})")
        self.ent_km.delete(0, 'end')
        self.ent_km.insert(0, str(vehicle.current_km or ''))

        customer = customer_service.get_customer_by_id(self.customer_id, conn=conn)
        if customer:
            self.lbl_customer_info.configure(text=f"Cliente: {customer.nome_razao_social}")
        else:
            self.lbl_customer_info.configure(text="Cliente não encontrado!", text_color=theme.DANGER)
        self.btn_edit_vehicle.configure(state="normal")

    def edit_vehicle(self, plate_suggestion=None):
        if not self.customer_id:
            customer_id = CustomerSearchModal(self).get_input()
            if not customer_id:
                messagebox.showwarning("Aviso", "É necessário selecionar um cliente para adicionar ou editar um veículo.")
                return
            self.customer_id = customer_id

        initial_plate = plate_suggestion or self.ent_placa.get().strip().upper()
        vehicle_modal = VehicleModal(self, customer_id=self.customer_id, vehicle_id=self.vehicle_id, initial_plate=initial_plate)
        new_vehicle_id = vehicle_modal.get_input()

        if new_vehicle_id:
            self.vehicle_id = new_vehicle_id
            vehicle = vehicle_service.get_vehicle_by_id(self.vehicle_id)
            if vehicle:
                self.ent_placa.delete(0, 'end')
                self.ent_placa.insert(0, vehicle.plate)

    def get_customer_id(self):
        dialog = CustomerSearchModal(self)
        return dialog.get_input()

    def toggle_installments_entry(self, selected_payment: str):
        if selected_payment == "CREDIARIO":
            self.f_installments.pack(side="left", padx=5, before=self.cb_pagamento.master.children['!ctkbutton'])
        else:
            self.f_installments.pack_forget()

    def add_item(self):
        code = self.ent_code.get().strip()
        try:
            qtd = float(self.ent_qtd.get().replace(",", "."))
        except ValueError:
            qtd = 1.0

        technician_name = self.cb_technician.get()
        technician_id = None
        if technician_name:
            tech_data = next((t for t in self.technicians if t['username'] == technician_name), None)
            if tech_data:
                technician_id = tech_data['id']

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

        self.items.append({
            'product_id': row['id'],
            'tipo': 'servico' if row['is_servico'] else 'peca',
            'nome': row['nome'],
            'codigo': row['sku'] or row['codigo_barras'],
            'quantidade': qtd,
            'preco_unitario': row['preco_venda'] or 0.0,
            'desconto_item': 0.0,
            'technician_id': technician_id,
            'technician_name': technician_name
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
                tipo_str, item['codigo'], item['nome'], item.get('technician_name', '--'),
                f"{item['quantidade']:.2f}", f"R$ {item['preco_unitario']:.2f}", f"R$ {subtotal:.2f}"
            ), tags=(tag,))

        self.lbl_tot_pecas.configure(text=f"Peças: R$ {t_pecas:.2f}")
        self.lbl_tot_serv.configure(text=f"Mão de Obra: R$ {t_servicos:.2f}")
        self.lbl_tot_geral.configure(text=f"TOTAL GERAL: R$ {(t_pecas + t_servicos):.2f}")

    def save(self) -> bool:
        status = self.cb_status.get()
        desc = self.txt_desc.get("1.0", "end-1c").strip()
        current_km = self.ent_km.get().strip()
        schedule_datetime_str = None

        if not self.vehicle_id or not self.customer_id:
            messagebox.showerror("Erro", "É obrigatório associar um veículo e um cliente à Ordem de Serviço.")
            return False

        t_pecas = sum((i['quantidade'] * i['preco_unitario']) - i.get('desconto_item', 0.0) for i in self.items if i['tipo'] == 'peca')
        t_servicos = sum((i['quantidade'] * i['preco_unitario']) - i.get('desconto_item', 0.0) for i in self.items if i['tipo'] == 'servico')
        t_geral = t_pecas + t_servicos

        schedule_date = self.ent_schedule_date.get().strip()
        schedule_time = self.ent_schedule_time.get().strip()
        if schedule_date and schedule_time:
            try:
                from datetime import datetime
                dt_obj = datetime.strptime(f"{schedule_date} {schedule_time}", '%d/%m/%Y %H:%M')
                schedule_datetime_str = dt_obj.strftime('%Y-%m-%d %H:%M:%S')
            except ValueError:
                messagebox.showerror("Erro de Formato", "Data ou hora do agendamento em formato inválido. Use DD/MM/AAAA e HH:MM.")
                return False

        conn = get_connection()
        cur = conn.cursor()
        try:
            if self.os_id:
                if current_km.isdigit():
                    cur.execute("UPDATE vehicles SET current_km = ? WHERE id = ?", (int(current_km), self.vehicle_id))

                cur.execute("UPDATE service_orders SET customer_id=?, vehicle_id=?, descricao_problema=?, status=?, total_pecas=?, total_servicos=?, total_geral=?, scheduled_start_time=? WHERE id=?",
                            (self.customer_id, self.vehicle_id, desc, status, t_pecas, t_servicos, t_geral, schedule_datetime_str, self.os_id))
                cur.execute("DELETE FROM service_order_items WHERE service_order_id=?", (self.os_id,))
            else:
                cur.execute("INSERT INTO service_orders (customer_id, vehicle_id, descricao_problema, status, total_pecas, total_servicos, total_geral, scheduled_start_time) VALUES (?, ?, ?, ?, ?, ?, ?, ?)",
                            (self.customer_id, self.vehicle_id, desc, status, t_pecas, t_servicos, t_geral, schedule_datetime_str))
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

        vehicle = vehicle_service.get_vehicle_by_id(self.vehicle_id)
        placa = vehicle.plate if vehicle else "N/A"
        veiculo_str = f"{vehicle.brand} {vehicle.model}" if vehicle else "N/A"

        os_data = {
            'id': self.os_id,
            'placa': placa,
            'veiculo': veiculo_str,
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

        t_pecas = sum((i['quantidade'] * i['preco_unitario']) - i.get('desconto_item', 0.0) for i in self.items if i['tipo'] == 'peca')
        t_servicos = sum((i['quantidade'] * i['preco_unitario']) - i.get('desconto_item', 0.0) for i in self.items if i['tipo'] == 'servico')
        t_geral = t_pecas + t_servicos

        from erp_backend.utils.db import transaction
        from erp_backend.services.sales_service import create_sale, add_sale_item

        try:
            with transaction() as conn:
                payment_method = self.cb_pagamento.get()
                installments = 1

                if payment_method == 'CREDIARIO':
                    try:
                        installments = int(self.ent_installments.get())
                        if installments <= 0: raise ValueError()
                    except ValueError:
                        messagebox.showerror("Erro", "Número de parcelas inválido para o crediário.")
                        return

                sale_id = create_sale(self.customer_id, t_geral, 0.0, payment_method, installments, conn=conn)

                for item in self.items:
                    add_sale_item(sale_id, item['product_id'], item['quantidade'], item['preco_unitario'], item.get('desconto_item', 0.0), conn=conn)

                conn.execute("UPDATE service_orders SET status='Faturada', data_fechamento=CURRENT_TIMESTAMP WHERE id=?", (self.os_id,))

            self.cb_status.set("Faturada")

            vehicle = vehicle_service.get_vehicle_by_id(self.vehicle_id, conn=conn)
            os_data_final = {
                'id': self.os_id,
                'placa': vehicle.plate if vehicle else "N/A",
                'veiculo': f"{vehicle.brand} {vehicle.model}" if vehicle else "N/A",
                'status': "Faturada",
                'descricao_problema': self.txt_desc.get("1.0", "end-1c").strip(),
                'total_pecas': t_pecas,
                'total_servicos': t_servicos,
                'total_geral': t_geral
            }

            from erp_frontend.os_post_action_modal import OSPostActionModal
            OSPostActionModal(self.winfo_toplevel(), os_data_final, self.items)
            self.destroy()

        except ValueError as ve:
            messagebox.showwarning("Aviso de Stock", str(ve))
        except Exception as e:
            messagebox.showerror("Erro Crítico", f"Falha ao faturar a OS. Nenhuma alteração foi guardada.\n\nDetalhes: {e}")

class OSView(ctk.CTkFrame):
    def __init__(self, master, app_window, **kwargs):
        super().__init__(master, fg_color=theme.BG, **kwargs)
        self.app_window = app_window
        self.setup_ui()
        self.load_data()

    def setup_ui(self):
        top_frame = ctk.CTkFrame(self, fg_color="transparent")
        top_frame.pack(fill="x", padx=20, pady=10)

        self.search_entry = ctk.CTkEntry(top_frame, placeholder_text="🔎 BUSCA: PLACA OU VEÍCULO...", height=40,
                                          font=theme.font_body(16), fg_color=theme.CARD, border_color=theme.SECONDARY)
        self.search_entry.pack(side="left", fill="x", expand=True, padx=(0, 20))
        self.search_entry.bind("<KeyRelease>", lambda e: self.load_data())

        btn_new = ctk.CTkButton(top_frame, text="[ NOVA O.S. ]", command=self.new_os, **theme.btn_success())
        btn_new.pack(side="right", padx=5)

        btn_edit = ctk.CTkButton(top_frame, text="[ EDITAR ]", command=self.edit_selected, **theme.btn_secondary())
        btn_edit.pack(side="right", padx=5)

        btn_refresh = ctk.CTkButton(top_frame, text="[ ATUALIZAR ]", command=self.load_data, **theme.btn_primary())
        btn_refresh.pack(side="right", padx=5)

        columns = ("OS #", "PLACA", "VEÍCULO", "CLIENTE", "STATUS", "TOTAL GERAL", "DATA ABERTURA")
        self.table = TableComponent(self, columns)
        self.table.column("OS #", width=60)
        self.table.column("PLACA", width=100)
        self.table.column("VEÍCULO", width=200, anchor="w")
        self.table.column("CLIENTE", width=250, anchor="w")
        self.table.column("STATUS", width=120)
        self.table.column("TOTAL GERAL", width=120)
        self.table.column("DATA ABERTURA", width=150)
        self.table.pack(fill="both", expand=True, padx=20, pady=10)
        self.table.bind("<Double-1>", lambda e: self.edit_selected())
        self.table.bind("<Button-3>", self._show_context_menu)
        self._create_context_menu()

    def load_data(self):
        search_term = self.search_entry.get().strip()
        for item in self.table.get_children():
            self.table.delete(item)

        conn = get_connection()
        cur = conn.cursor()

        sql = """
            SELECT so.*, v.plate, v.brand, v.model, c.nome_razao_social
            FROM service_orders so
            LEFT JOIN vehicles v ON so.vehicle_id = v.id
            LEFT JOIN customers c ON so.customer_id = c.id
        """
        params = ()
        if search_term:
            sql += " WHERE v.plate LIKE ? OR v.model LIKE ? OR c.nome_razao_social LIKE ?"
            params = (f"%{search_term}%", f"%{search_term}%", f"%{search_term}%")
        sql += " ORDER BY id DESC LIMIT 100"

        cur.execute(sql, params)
        for row in cur.fetchall():
            self.table.insert("", "end", iid=str(row['id']), values=(
                f"{row['id']:05d}",
                row['plate'] or "--",
                f"{row['brand'] or ''} {row['model'] or ''}".strip(),
                row['nome_razao_social'] or "--",
                row['status'],
                f"R$ {row['total_geral']:.2f}",
                row['data_abertura'][:16] if row['data_abertura'] else "--"
            ))
        conn.close()

    def _create_context_menu(self):
        self.context_menu = Menu(self.table, tearoff=0, font=theme.font_body(12),
                                  bg=theme.CARD, fg=theme.TEXT, activebackground=theme.PRIMARY,
                                  activeforeground=theme.PRIMARY_FOREGROUND)
        self.context_menu.add_command(label="Nova Ordem de Serviço", command=self.new_os)
        self.context_menu.add_command(label="Editar O.S. Selecionada", command=self.edit_selected)
        self.context_menu.add_separator()
        self.context_menu.add_command(label="Atualizar Lista", command=self.load_data)

    def _show_context_menu(self, event):
        selection = self.table.selection()
        if selection:
            self.context_menu.entryconfigure("Editar O.S. Selecionada", state="normal")
        else:
            self.context_menu.entryconfigure("Editar O.S. Selecionada", state="disabled")
        self.context_menu.post(event.x_root, event.y_root)

    def new_os(self):
        OSModal(self, on_save=self.load_data)

    def edit_selected(self):
        selected = self.table.selection()
        if not selected: return
        os_id = int(selected[0])
        OSModal(self, os_id=os_id, on_save=self.load_data)
