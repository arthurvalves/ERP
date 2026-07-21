import customtkinter as ctk

from erp_backend.services import quote_service


class QuoteModal(ctk.CTkToplevel):
    def __init__(self, master, quote_id=None, on_save=None):
        super().__init__(master)
        self.title("Orçamento")
        self.geometry("480x220")
        self.transient(master)
        self.grab_set()

        self.quote_id = quote_id
        self.on_save = on_save

        self._setup_ui()

    def _setup_ui(self):
        container = ctk.CTkFrame(self, fg_color="transparent")
        container.pack(fill="both", expand=True, padx=20, pady=20)

        if self.quote_id:
            quote_data, _items = quote_service.get_quote_details(self.quote_id)
            status_text = quote_data["status"] if quote_data else "Nao encontrado"
            title = f"Orcamento #{self.quote_id:05d}"
        else:
            status_text = "Novo orcamento"
            title = "Novo Orcamento"

        ctk.CTkLabel(container, text=title, font=("Roboto", 20, "bold")).pack(anchor="w")
        ctk.CTkLabel(container, text=f"Status: {status_text}").pack(anchor="w", pady=(8, 0))
        ctk.CTkLabel(
            container,
            text="Este modal mantem a navegacao funcional. A edicao completa pode ser expandida depois.",
            justify="left",
            wraplength=420,
        ).pack(anchor="w", pady=(16, 0))

        buttons = ctk.CTkFrame(container, fg_color="transparent")
        buttons.pack(fill="x", pady=(24, 0))
        ctk.CTkButton(buttons, text="Fechar", command=self._close).pack(side="right")

    def _close(self):
        if self.on_save:
            self.on_save()
        self.destroy()
