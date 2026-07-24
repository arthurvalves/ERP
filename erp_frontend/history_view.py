import customtkinter as ctk
from tkinter import messagebox
from erp_frontend.components.table import TableComponent
from erp_backend.services import history_service
from datetime import datetime
<<<<<<< HEAD
from erp_frontend import theme

class HistoryView(ctk.CTkFrame):
    def __init__(self, master, app_window, **kwargs):
        super().__init__(master, fg_color=theme.BG, **kwargs)
=======

class HistoryView(ctk.CTkFrame):
    def __init__(self, master, app_window, **kwargs):
        super().__init__(master, fg_color="#1e1e1e", **kwargs)
>>>>>>> b8696156ad077242d2bbfc43a202beb2b9ea5c18
        self.app_window = app_window
        self.setup_ui()

    def setup_ui(self):
<<<<<<< HEAD
        top_frame = ctk.CTkFrame(self, fg_color="transparent")
        top_frame.pack(fill="x", padx=20, pady=10)

        self.search_entry = ctk.CTkEntry(top_frame, placeholder_text="🔎 DIGITE A PLACA DO VEÍCULO...", height=45,
                                          font=theme.font_body(20), fg_color=theme.CARD, border_color=theme.SECONDARY)
        self.search_entry.pack(side="left", fill="x", expand=True, padx=(0, 20))
        self.search_entry.bind("<Return>", self.search_history)

        btn_search = ctk.CTkButton(top_frame, text="BUSCAR HISTÓRICO", height=45, command=self.search_history, **theme.btn_primary())
        btn_search.pack(side="right")

        self.info_frame = ctk.CTkFrame(self, **theme.card_frame_kwargs())
        self.info_frame.pack(fill="x", padx=20, pady=10, ipady=10)
        self.lbl_vehicle_info = ctk.CTkLabel(self.info_frame, text="Veículo: -- | Cliente: --", font=theme.font_body(16), text_color=theme.TEXT)
        self.lbl_vehicle_info.pack(padx=20)
        self.info_frame.pack_forget()

        container = ctk.CTkFrame(self, fg_color="transparent")
        container.pack(fill="both", expand=True, padx=20, pady=10)
        container.grid_columnconfigure(0, weight=1)
        container.grid_rowconfigure(0, weight=1)
        container.grid_rowconfigure(1, weight=1)

=======
        # Frame de busca no topo
        top_frame = ctk.CTkFrame(self, fg_color="transparent")
        top_frame.pack(fill="x", padx=20, pady=10)

        self.search_entry = ctk.CTkEntry(top_frame, placeholder_text="🔎 DIGITE A PLACA DO VEÍCULO...", height=45, font=("Roboto", 20))
        self.search_entry.pack(side="left", fill="x", expand=True, padx=(0, 20))
        self.search_entry.bind("<Return>", self.search_history)

        btn_search = ctk.CTkButton(top_frame, text="BUSCAR HISTÓRICO", height=45, font=("Roboto", 16, "bold"), command=self.search_history)
        btn_search.pack(side="right")

        # Frame para informações do veículo e cliente
        self.info_frame = ctk.CTkFrame(self, fg_color="#2b2b2b", corner_radius=8)
        self.info_frame.pack(fill="x", padx=20, pady=10, ipady=10)
        self.lbl_vehicle_info = ctk.CTkLabel(self.info_frame, text="Veículo: -- | Cliente: --", font=("Roboto", 16))
        self.lbl_vehicle_info.pack(padx=20)
        self.info_frame.pack_forget() # Começa oculto

        # Container principal para as duas tabelas
        container = ctk.CTkFrame(self, fg_color="transparent")
        container.pack(fill="both", expand=True, padx=20, pady=10)
        container.grid_columnconfigure(0, weight=1)
        container.grid_rowconfigure(0, weight=1) # Linha da tabela de OS
        container.grid_rowconfigure(1, weight=1) # Linha da tabela de itens

        # Tabela de Ordens de Serviço
>>>>>>> b8696156ad077242d2bbfc43a202beb2b9ea5c18
        os_columns = ("OS #", "DATA", "STATUS", "TOTAL")
        self.os_table = TableComponent(container, os_columns)
        self.os_table.grid(row=0, column=0, sticky="nsew", pady=(0, 10))
        self.os_table.bind("<<TreeviewSelect>>", self.on_os_selected)

<<<<<<< HEAD
=======
        # Tabela de Itens da OS selecionada
>>>>>>> b8696156ad077242d2bbfc43a202beb2b9ea5c18
        items_columns = ("TIPO", "DESCRIÇÃO DO ITEM/SERVIÇO", "TÉCNICO RESPONSÁVEL", "QTD", "VALOR")
        self.items_table = TableComponent(container, items_columns)
        self.items_table.column("TIPO", width=100)
        self.items_table.column("DESCRIÇÃO DO ITEM/SERVIÇO", width=400, anchor="w")
        self.items_table.column("TÉCNICO RESPONSÁVEL", width=200)
        self.items_table.grid(row=1, column=0, sticky="nsew")

        self.history_data = []

    def search_history(self, event=None):
        plate = self.search_entry.get()
        if not plate:
            return

<<<<<<< HEAD
=======
        # Limpa dados antigos
>>>>>>> b8696156ad077242d2bbfc43a202beb2b9ea5c18
        for i in self.os_table.get_children(): self.os_table.delete(i)
        for i in self.items_table.get_children(): self.items_table.delete(i)
        self.info_frame.pack_forget()

        vehicle_data, history = history_service.get_vehicle_history_by_plate(plate)
        self.history_data = history

        if not vehicle_data:
            messagebox.showinfo("Não Encontrado", f"Nenhum veículo encontrado com a placa '{plate}'.")
            return

<<<<<<< HEAD
=======
        # Exibe informações do veículo
>>>>>>> b8696156ad077242d2bbfc43a202beb2b9ea5c18
        self.info_frame.pack(fill="x", padx=20, pady=10, ipady=10)
        vehicle_str = f"{vehicle_data.get('brand', '')} {vehicle_data.get('model', '')} ({vehicle_data.get('year', 'N/A')})"
        customer_str = vehicle_data.get('nome_razao_social', 'N/A')
        self.lbl_vehicle_info.configure(text=f"Veículo: {vehicle_str}   |   Cliente: {customer_str}")

<<<<<<< HEAD
=======
        # Preenche a tabela de Ordens de Serviço
>>>>>>> b8696156ad077242d2bbfc43a202beb2b9ea5c18
        for so in history:
            date_formatted = datetime.strptime(so['data_abertura'], '%Y-%m-%d %H:%M:%S').strftime('%d/%m/%Y')
            self.os_table.insert("", "end", iid=str(so['id']), values=(
                f"{so['id']:05d}",
                date_formatted,
                so['status'],
                f"R$ {so['total_geral']:.2f}"
            ))

    def on_os_selected(self, event=None):
        selected = self.os_table.selection()
        if not selected:
            return

        os_id = int(selected[0])
<<<<<<< HEAD

        for i in self.items_table.get_children(): self.items_table.delete(i)

=======
        
        # Limpa a tabela de itens
        for i in self.items_table.get_children(): self.items_table.delete(i)

        # Encontra a OS selecionada nos dados em memória
>>>>>>> b8696156ad077242d2bbfc43a202beb2b9ea5c18
        selected_os = next((so for so in self.history_data if so['id'] == os_id), None)

        if selected_os and 'items' in selected_os:
            for item in selected_os['items']:
                self.items_table.insert("", "end", values=(
                    item['tipo'].upper(),
                    item['product_name'],
                    item.get('technician_name', 'N/A'),
                    f"{item['quantidade']:.2f}",
                    f"R$ {item['preco_unitario']:.2f}"
<<<<<<< HEAD
                ))
=======
                ))
>>>>>>> b8696156ad077242d2bbfc43a202beb2b9ea5c18
