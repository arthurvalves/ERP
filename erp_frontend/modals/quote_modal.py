import customtkinter as ctk
from tkinter import messagebox
from erp_backend.utils.db import get_connection
from erp_frontend.components.table import TableComponent
from erp_backend.services import vehicle_service, customer_service, quote_service
from erp_frontend.modals.customer_search_modal import CustomerSearchModal
from erp_frontend.modals.vehicle_modal import VehicleModal

class QuoteModal(ctk.CTkToplevel):
    def __init__(self, master, quote_id=None, on_save=None):
        super().__init__(master)
        self.title(f"Orçamento #{quote_id}" if quote_id else "Novo Orçamento")
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
        self.frame = ctk.CTkFrame(self)
        self.frame.pack(fill="both", expand=True, padx=15, pady=15)

        f_header = ctk.CTkFrame(self.frame, fg_color="#2b2b2b", corner_radius=8)
        f_header.pack(fill="x", pady=(0, 10), ipady=5)

        f_placa = ctk.CTkFrame(f_header, fg_color="transparent")
        f_placa.pack(side="left", expand=True, fill="x", padx=10)
        ctk.CTkLabel(f_placa, text="Placa (Pressione ENTER para buscar):", font=("Roboto", 12, "bold")).pack(anchor="w")
        self.ent_placa = ctk.CTkEntry(f_placa, font=("Roboto", 16))
        self.ent_placa.pack(fill="x")
        self.ent_placa.bind("<Return>", self.search_vehicle_by_plate)

        self.lbl_vehicle_info = ctk.CTkLabel(f_header, text="Veículo: --", font=("Roboto", 14), anchor="w")
        self.lbl_vehicle_info.pack(side="left", expand=True, fill="x", padx=10)

        self.lbl_customer_info = ctk.CTkLabel(f_header, text="Cliente: --", font=("Roboto", 14), anchor="w")
        self.lbl_customer_info.pack(side="left", expand=True, fill="x", padx=10)

        self.btn_edit_vehicle = ctk.CTkButton(f_header, text="EDITAR VEÍCULO", font=("Roboto", 12), command=self.edit_vehicle, state="disabled")
        self.btn_edit_vehicle.pack(side="left", padx=10)

        f_add = ctk.CTkFrame(self.frame, fg_color="#1a1a1a", corner_radius=8)
        f_add.pack(fill="x", padx=5, pady=10, ipady=5)
        
        ctk.CTkLabel(f_add, text="Inserir Peça ou Serviço:", font=("Roboto", 12)).pack(side="left", padx=10)
        self.ent_code = ctk.CTkEntry(f_add, placeholder_text="SKU ou Cód. Barras", width=250, font=("Roboto", 14))
        self.ent_code.pack(side="left", padx=5)
        self.ent_code.bind("<Return>", lambda e: self.add_item())
        
        ctk.CTkLabel(f_add, text="Qtd:", font=("Roboto", 12)).pack(side="left", padx=5)
        self.ent_qtd = ctk.CTkEntry(f_add, width=60, font=("Roboto", 14))
        self.ent_qtd.insert(0, "1")
        self.ent_qtd.pack(side="left", padx=5)
        self.ent_qtd.bind("<Return>", lambda e: self.add_item())

        btn_add = ctk.CTkButton(f_add, text="ADICIONAR", command=self.add_item)
        btn_add.pack(side="left", padx=10)

        columns = ("TIPO", "CÓDIGO", "NOME", "QTD", "UNIT", "TOTAL")
        self.table = TableComponent(self.frame, columns)
        self.table.pack(fill="both", expand=True, padx=5, pady=5)
        self.table.bind("<Delete>", self.remove_item)

        f_footer = ctk.CTkFrame(self.frame, fg_color="transparent")
        f_footer.pack(fill="x", side="bottom", padx=5, pady=10)

        self.lbl_tot_geral = ctk.CTkLabel(f_footer, text="TOTAL GERAL: R$ 0.00", font=("Roboto", 24, "bold"), text_color="#2ecc71")
        self.lbl_tot_geral.pack(side="left", padx=20)

        btn_salvar = ctk.CTkButton(f_footer, text="SALVAR ORÇAMENTO", font=("Roboto", 16, "bold"), height=45, command=self.save)
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
            self.lbl_customer_info.configure(text="Cliente não encontrado!", text_color="red")

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
        row = conn.cursor().execute("SELECT id, nome, sku, codigo_barras, preco_venda, is_servico FROM products WHERE sku = ? OR codigo_barras = ?", (code, code)).fetchone()
        conn.close()

        if not row:
            messagebox.showwarning("Não Encontrado", f"Peça/Serviço '{code}' não localizado.")
            return

        self.items.append({
            'product_id': row['id'], 'tipo': 'servico' if row['is_servico'] else 'peca',
            'nome': row['nome'], 'codigo': row['sku'] or row['codigo_barras'],
            'quantidade': qtd, 'preco_unitario': row['preco_venda']
        })
        self.ent_code.delete(0, 'end'); self.ent_qtd.delete(0, 'end'); self.ent_qtd.insert(0, "1")
        self.refresh_items(); self.ent_code.focus_set()

    def remove_item(self, event=None):
        selected = self.table.selection()
        if not selected: return
        del self.items[int(selected[0])]; self.refresh_items()

    def refresh_items(self):
        for item in self.table.get_children(): self.table.delete(item)
        total = 0.0
        for idx, item in enumerate(self.items):
            subtotal = item['quantidade'] * item['preco_unitario']
            total += subtotal
            tipo_str = "MÃO DE OBRA" if item['tipo'] == 'servico' else "PEÇA"
            self.table.insert("", "end", iid=str(idx), values=(
                tipo_str, item['codigo'], item['nome'], f"{item['quantidade']:.2f}",
                f"R$ {item['preco_unitario']:.2f}", f"R$ {subtotal:.2f}"
            ))
        self.lbl_tot_geral.configure(text=f"TOTAL GERAL: R$ {total:.2f}")

    def save(self):
        if not self.vehicle_id or not self.customer_id:
            messagebox.showerror("Erro", "É obrigatório associar um veículo e um cliente ao orçamento.")
            return

        total = sum(i['quantidade'] * i['preco_unitario'] for i in self.items)
        conn = get_connection()
        cur = conn.cursor()
        try:
            if self.quote_id:
                cur.execute("UPDATE quotes SET customer_id=?, vehicle_id=?, total=? WHERE id=?",
                            (self.customer_id, self.vehicle_id, total, self.quote_id))
                cur.execute("DELETE FROM quote_items WHERE quote_id=?", (self.quote_id,))
            else:
                cur.execute("INSERT INTO quotes (customer_id, vehicle_id, total) VALUES (?, ?, ?)",
                            (self.customer_id, self.vehicle_id, total))
                self.quote_id = cur.lastrowid

            for item in self.items:
                cur.execute("INSERT INTO quote_items (quote_id, product_id, quantidade, preco_unitario) VALUES (?, ?, ?, ?)",
                            (self.quote_id, item['product_id'], item['quantidade'], item['preco_unitario']))
            conn.commit()
            if self.on_save: self.on_save()
            self.destroy()
        except Exception as e:
            conn.rollback(); messagebox.showerror("Erro ao Salvar", str(e))
        finally:
            conn.close()

    def _close(self):
        if self.on_save:
            self.on_save()
        self.destroy()
