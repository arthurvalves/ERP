import customtkinter as ctk
from tkinter import messagebox
from erp_backend.utils.db import get_connection
from erp_frontend.components.table import TableComponent
from erp_backend.services import vehicle_service, customer_service, quote_service
from erp_frontend.modals.customer_search_modal import CustomerSearchModal
from erp_frontend.modals.vehicle_modal import VehicleModal
from erp_frontend import theme

class QuoteModal(ctk.CTkToplevel):
    def __init__(self, master, quote_id=None, on_save=None):
        super().__init__(master)
        self.title(f"Orçamento #{quote_id}" if quote_id else "Novo Orçamento")
        self.configure(fg_color=theme.BG)
        self.transient(master)
        self.grab_set()

        self.quote_id = quote_id
        self.on_save = on_save
        self.items = []
        self.customer_id = None
        self.vehicle_id = None

        self._setup_ui()
        self.load_data()
        self.bind("<Escape>", lambda e: self.destroy())
        self.after(10, self._center_window)

    def _center_window(self):
        self.update_idletasks()
        width = 950
        height = 700
        screen_width = self.winfo_screenwidth()
        screen_height = self.winfo_screenheight()
        x = (screen_width // 2) - (width // 2)
        y = (screen_height // 2) - (height // 2)
        self.geometry(f'{width}x{height}+{x}+{y}')
        self.resizable(False, False)

    def _setup_ui(self):
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

        self.btn_edit_vehicle = ctk.CTkButton(f_header, text="EDITAR VEÍCULO", command=self.edit_vehicle, state="disabled", **theme.btn_secondary(font=theme.font_bold(12)))
        self.btn_edit_vehicle.pack(side="left", padx=10)

        f_add = ctk.CTkFrame(self.frame, fg_color=theme.CARD_ALT, corner_radius=theme.RADIUS)
        f_add.pack(fill="x", padx=5, pady=10, ipady=5)

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

        columns = ("TIPO", "CÓDIGO", "NOME", "QTD", "UNIT", "TOTAL")
        self.table = TableComponent(self.frame, columns)
        self.table.pack(fill="both", expand=True, padx=5, pady=5)
        self.table.bind("<Delete>", self.remove_item)

        f_footer = ctk.CTkFrame(self.frame, fg_color="transparent")
        f_footer.pack(fill="x", side="bottom", padx=5, pady=10)

        self.lbl_tot_geral = ctk.CTkLabel(f_footer, text="TOTAL GERAL: R$ 0.00", font=theme.font_title(24), text_color=theme.PRIMARY)
        self.lbl_tot_geral.pack(side="left", padx=20)

        btn_salvar = ctk.CTkButton(f_footer, text="SALVAR ORÇAMENTO", height=45, command=self.save, **theme.btn_primary(font=theme.font_bold(16)))
        btn_salvar.pack(side="right", padx=20)

    def load_data(self):
        if not self.quote_id:
            self.refresh_items()
            return
        quote_data, items_data = quote_service.get_quote_details(self.quote_id)
        if quote_data:
            self.customer_id = quote_data.get('customer_id')
            self.vehicle_id = quote_data.get('vehicle_id')

            if self.vehicle_id:
                vehicle = vehicle_service.get_vehicle_by_id(self.vehicle_id)
                if vehicle:
                    self.ent_placa.insert(0, vehicle.plate)
                    self.update_vehicle_and_customer_info(vehicle)
                    self.btn_edit_vehicle.configure(state="normal")

            for item in items_data:
                self.items.append({
                    'product_id': item['product_id'],
                    'tipo': 'servico' if item['is_servico'] else 'peca',
                    'nome': item['nome'],
                    'codigo': item['sku'] or item['codigo_barras'],
                    'quantidade': item['quantidade'],
                    'preco_unitario': item['preco_unitario'],
                })
        self.refresh_items()

    def search_vehicle_by_plate(self, event=None):
        plate = self.ent_placa.get().strip().upper()
        if not plate: return

        vehicle = vehicle_service.get_vehicle_by_plate(plate)
        if vehicle:
            self.update_vehicle_and_customer_info(vehicle)
            self.btn_edit_vehicle.configure(state="normal")
        else:
            if messagebox.askyesno("Veículo não encontrado", f"A placa '{plate}' não está registada.\nDeseja adicionar um novo veículo?"):
                self.edit_vehicle(plate_suggestion=plate)

    def update_vehicle_and_customer_info(self, vehicle, conn=None):
        self.vehicle_id = vehicle.id
        self.customer_id = vehicle.customer_id
        self.lbl_vehicle_info.configure(text=f"Veículo: {vehicle.brand or ''} {vehicle.model or ''} ({vehicle.year or ''})")
        customer = customer_service.get_customer_by_id(self.customer_id, conn=conn)
        if customer:
            self.lbl_customer_info.configure(text=f"Cliente: {customer.nome_razao_social}")
        else:
            self.lbl_customer_info.configure(text="Cliente não encontrado!", text_color=theme.DANGER)

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
                self.update_vehicle_and_customer_info(vehicle)
                self.btn_edit_vehicle.configure(state="normal")

    def add_item(self):
        code = self.ent_code.get().strip()
        try: qtd = float(self.ent_qtd.get().replace(",", "."))
        except ValueError: qtd = 1.0
        if not code: return

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
        })

        self.ent_code.delete(0, 'end')
        self.ent_qtd.delete(0, 'end')
        self.ent_qtd.insert(0, "1")
        self.refresh_items()
        self.ent_code.focus_set()
      