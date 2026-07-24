import tkinter as tk

import customtkinter as ctk

from erp_backend.services import customer_service
from erp_frontend import theme


class CustomerSearchModal(ctk.CTkToplevel):
    def __init__(self, master):
        super().__init__(master)
        self.title("Buscar Cliente")
        self.geometry("700x500")
        self.configure(fg_color=theme.BG)
        self.transient(master)
        self.grab_set()

        self.result = None
        self.customers = []

        self.protocol("WM_DELETE_WINDOW", self._close)
        self._setup_ui()
        self._refresh_list()

    def _setup_ui(self):
        top = ctk.CTkFrame(self, fg_color="transparent")
        top.pack(fill="x", padx=16, pady=16)

        self.search_entry = ctk.CTkEntry(top, placeholder_text="Buscar por nome, CPF ou CNPJ",
                                          fg_color=theme.CARD, border_color=theme.SECONDARY)
        self.search_entry.pack(side="left", fill="x", expand=True)
        self.search_entry.bind("<KeyRelease>", lambda event: self._refresh_list())
        self.search_entry.bind("<Return>", lambda event: self._confirm())

        ctk.CTkButton(top, text="Buscar", command=self._refresh_list, **theme.btn_primary()).pack(side="left", padx=(8, 0))

        self.listbox = tk.Listbox(self, height=15, bg=theme.CARD_ALT, fg=theme.TEXT,
                                   selectbackground=theme.PRIMARY, selectforeground=theme.PRIMARY_FOREGROUND,
                                   highlightthickness=0, bd=0)
        self.listbox.pack(fill="both", expand=True, padx=16, pady=(0, 12))
        self.listbox.bind("<Double-Button-1>", lambda event: self._confirm())
        self.listbox.bind("<Return>", lambda event: self._confirm())

        bottom = ctk.CTkFrame(self, fg_color="transparent")
        bottom.pack(fill="x", padx=16, pady=(0, 16))

        ctk.CTkButton(bottom, text="Cancelar", command=self._close, **theme.btn_secondary()).pack(side="right")
        ctk.CTkButton(bottom, text="Selecionar", command=self._confirm, **theme.btn_primary()).pack(side="right", padx=(0, 8))

    def _refresh_list(self):
        search_term = self.search_entry.get().strip()
        self.customers = customer_service.search_customers(search_term)

        self.listbox.delete(0, tk.END)
        for customer in self.customers:
            document = customer.cpf_cnpj or ""
            label = f"#{customer.id} - {customer.nome_razao_social} {document}".strip()
            self.listbox.insert(tk.END, label)

    def _confirm(self):
        selection = self.listbox.curselection()
        if not selection:
            return

        index = selection[0]
        if index < len(self.customers):
            self.result = self.customers[index].id
        self.destroy()

    def _close(self):
        self.result = None
        self.destroy()

    def get_input(self):
        self.wait_window()
        return self.result
