import customtkinter as ctk
from tkinter import messagebox
from erp_frontend.components.table import TableComponent
from erp_backend.services import quote_service
from erp_frontend.modals.quote_modal import QuoteModal

class QuotesView(ctk.CTkFrame):
    def __init__(self, master, app_window, **kwargs):
        super().__init__(master, fg_color="#1e1e1e", **kwargs)
        self.app_window = app_window
        self.setup_ui()
        self.load_data()

    def setup_ui(self):
        top_frame = ctk.CTkFrame(self, fg_color="transparent")
        top_frame.pack(fill="x", padx=20, pady=10)

        self.search_entry = ctk.CTkEntry(top_frame, placeholder_text="🔎 BUSCA: PLACA, CLIENTE OU STATUS...", height=40, font=("Roboto", 16))
        self.search_entry.pack(side="left", fill="x", expand=True, padx=(0, 20))
        self.search_entry.bind("<KeyRelease>", lambda e: self.load_data())

        btn_new = ctk.CTkButton(top_frame, text="[ NOVO ORÇAMENTO ]", command=self.new_quote)
        btn_new.pack(side="right", padx=5)

        btn_edit = ctk.CTkButton(top_frame, text="[ EDITAR ]", command=self.edit_selected)
        btn_edit.pack(side="right", padx=5)

        btn_convert = ctk.CTkButton(top_frame, text="[ CONVERTER EM OS ]", fg_color="#2ecc71", hover_color="#27ae60", command=self.convert_to_os)
        btn_convert.pack(side="right", padx=5)

        columns = ("ORÇ #", "PLACA", "VEÍCULO", "CLIENTE", "STATUS", "TOTAL", "DATA")
        self.table = TableComponent(self, columns)
        self.table.column("ORÇ #", width=60)
        self.table.column("PLACA", width=100)
        self.table.column("VEÍCULO", width=200, anchor="w")
        self.table.column("CLIENTE", width=250, anchor="w")
        self.table.column("STATUS", width=120)
        self.table.column("TOTAL", width=120)
        self.table.column("DATA", width=150)
        self.table.pack(fill="both", expand=True, padx=20, pady=10)
        self.table.bind("<Double-1>", lambda e: self.edit_selected())

    def load_data(self):
        search_term = self.search_entry.get().strip()
        for item in self.table.get_children():
            self.table.delete(item)

        quotes = quote_service.get_all_quotes(search_term)
        for row in quotes:
            self.table.insert("", "end", iid=str(row['id']), values=(
                f"{row['id']:05d}",
                row['plate'] or "--",
                row['model'] or "--",
                row['nome_razao_social'] or "--",
                row['status'],
                f"R$ {row['total']:.2f}",
                row['data_criacao'][:16] if row['data_criacao'] else "--"
            ))

    def new_quote(self):
        QuoteModal(self, on_save=self.load_data)

    def edit_selected(self):
        selected = self.table.selection()
        if not selected: return
        quote_id = int(selected[0])
        QuoteModal(self, quote_id=quote_id, on_save=self.load_data)

    def convert_to_os(self):
        selected = self.table.selection()
        if not selected: return
        quote_id = int(selected[0])
        
        os_id = quote_service.convert_quote_to_os(quote_id)
        if os_id:
            messagebox.showinfo("Sucesso", f"Orçamento convertido com sucesso!\n\nNova Ordem de Serviço #{os_id} foi criada.")
            self.load_data()
            # Opcional: Abrir a OS recém-criada
            # from erp_frontend.os_view import OSModal
            # OSModal(self, os_id=os_id, on_save=self.load_data)