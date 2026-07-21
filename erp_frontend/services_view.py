import customtkinter as ctk
from tkinter import messagebox
from erp_frontend.components.table import TableComponent
from erp_backend.services import service_service

class ServiceModal(ctk.CTkToplevel):
    def __init__(self, master, service_id=None, on_save=None):
        super().__init__(master)
        self.title("Editar Serviço" if service_id else "Novo Serviço")
        self.geometry("500x450")
        self.transient(master)
        self.grab_set()

        self.service_id = service_id
        self.on_save = on_save

        self.setup_ui()
        if self.service_id:
            self.load_data()

    def setup_ui(self):
        frame = ctk.CTkFrame(self)
        frame.pack(fill="both", expand=True, padx=20, pady=20)

        ctk.CTkLabel(frame, text="Nome do Serviço:", font=("Roboto", 14, "bold")).pack(anchor="w")
        self.ent_name = ctk.CTkEntry(frame, font=("Roboto", 14))
        self.ent_name.pack(fill="x", pady=(0, 10))

        ctk.CTkLabel(frame, text="SKU / Código:", font=("Roboto", 12)).pack(anchor="w")
        self.ent_sku = ctk.CTkEntry(frame, font=("Roboto", 14))
        self.ent_sku.pack(fill="x", pady=(0, 10))

        ctk.CTkLabel(frame, text="Preço Padrão (R$):", font=("Roboto", 12)).pack(anchor="w")
        self.ent_price = ctk.CTkEntry(frame, font=("Roboto", 14))
        self.ent_price.pack(fill="x", pady=(0, 10))

        ctk.CTkLabel(frame, text="Categoria:", font=("Roboto", 12)).pack(anchor="w")
        self.ent_category = ctk.CTkEntry(frame, font=("Roboto", 14))
        self.ent_category.pack(fill="x", pady=(0, 10))

        ctk.CTkLabel(frame, text="Descrição:", font=("Roboto", 12)).pack(anchor="w")
        self.ent_description = ctk.CTkEntry(frame, font=("Roboto", 14))
        self.ent_description.pack(fill="x", pady=(0, 20))

        btn_save = ctk.CTkButton(frame, text="SALVAR", font=("Roboto", 16, "bold"), command=self.save)
        btn_save.pack(fill="x", ipady=5)

    def load_data(self):
        # No futuro, isso usaria service_service.get_by_id(self.service_id)
        from erp_backend.utils.db import fetchone
        service = fetchone("SELECT * FROM services WHERE id = ?", (self.service_id,))
        if service:
            self.ent_name.insert(0, service['name'])
            self.ent_sku.insert(0, service['sku'] or "")
            self.ent_price.insert(0, f"{service['standard_price']:.2f}")
            self.ent_category.insert(0, service['category'] or "")
            self.ent_description.insert(0, service['description'] or "")

    def save(self):
        name = self.ent_name.get().strip()
        if not name:
            messagebox.showerror("Erro", "O nome do serviço é obrigatório.")
            return

        try:
            price = float(self.ent_price.get().replace(",", "."))
        except ValueError:
            price = 0.0

        service_data = {
            "name": name,
            "sku": self.ent_sku.get().strip(),
            "standard_price": price,
            "category": self.ent_category.get().strip(),
            "description": self.ent_description.get().strip(),
        }

        try:
            service_service.create_or_update_service(service_data, self.service_id)
            if self.on_save:
                self.on_save()
            self.destroy()
        except Exception as e:
            messagebox.showerror("Erro ao Salvar", str(e))

class ServicesView(ctk.CTkFrame):
    def __init__(self, master, app_window, **kwargs):
        super().__init__(master, fg_color="#1e1e1e", **kwargs)
        self.app_window = app_window
        self.setup_ui()
        self.load_data()

    def setup_ui(self):
        top_frame = ctk.CTkFrame(self, fg_color="transparent")
        top_frame.pack(fill="x", padx=20, pady=10)

        self.search_entry = ctk.CTkEntry(top_frame, placeholder_text="🔎 BUSCAR SERVIÇO...", height=40, font=("Roboto", 16))
        self.search_entry.pack(side="left", fill="x", expand=True, padx=(0, 20))
        self.search_entry.bind("<KeyRelease>", lambda e: self.load_data())

        btn_new = ctk.CTkButton(top_frame, text="[ NOVO SERVIÇO ]", command=self.new_service)
        btn_new.pack(side="right", padx=5)

        btn_edit = ctk.CTkButton(top_frame, text="[ EDITAR ]", command=self.edit_selected)
        btn_edit.pack(side="right", padx=5)

        columns = ("NOME DO SERVIÇO", "SKU", "CATEGORIA", "PREÇO PADRÃO")
        self.table = TableComponent(self, columns)
        self.table.column("NOME DO SERVIÇO", width=400, anchor="w")
        self.table.column("SKU", width=150)
        self.table.column("CATEGORIA", width=200)
        self.table.column("PREÇO PADRÃO", width=150)
        self.table.pack(fill="both", expand=True, padx=20, pady=10)
        self.table.bind("<Double-1>", lambda e: self.edit_selected())

    def load_data(self):
        search_term = self.search_entry.get().strip()
        for item in self.table.get_children():
            self.table.delete(item)

        services = service_service.get_all_services(search_term)
        for row in services:
            self.table.insert("", "end", iid=str(row['id']), values=(
                row['name'],
                row['sku'] or "--",
                row['category'] or "--",
                f"R$ {row['standard_price']:.2f}"
            ))

    def new_service(self):
        ServiceModal(self, on_save=self.load_data)

    def edit_selected(self):
        selected = self.table.selection()
        if not selected: return
        service_id = int(selected[0])
        ServiceModal(self, service_id=service_id, on_save=self.load_data)