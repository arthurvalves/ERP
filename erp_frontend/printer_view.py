import customtkinter as ctk
from tkinter import messagebox
from erp_backend.services.printer_service import get_default_printer, set_default_printer, get_available_printers, generate_receipt_text, save_receipt_pdf
<<<<<<< HEAD
from erp_frontend import theme

class PrinterView(ctk.CTkFrame):
    def __init__(self, master, app_window, **kwargs):
        super().__init__(master, fg_color=theme.BG, **kwargs)
        self.app_window = app_window
        self.setup_ui()

    def setup_ui(self):
        self.header = ctk.CTkFrame(self, fg_color="transparent")
        self.header.pack(fill="x", padx=40, pady=40)

        title = ctk.CTkLabel(self.header, text="🖨️ CONFIGURAÇÃO DE IMPRESSORA TÉRMICA (80mm)", font=theme.font_title(28), text_color=theme.PRIMARY)
        title.pack(anchor="w")

        self.card = ctk.CTkFrame(self, **theme.card_frame_kwargs())
        self.card.pack(fill="both", expand=True, padx=40, pady=10)

        ctk.CTkLabel(self.card, text="Selecione a Impressora Padrão do PDV:", font=theme.font_body(18), text_color=theme.TEXT).pack(anchor="w", padx=40, pady=(40, 10))

=======

class PrinterView(ctk.CTkFrame):
    def __init__(self, master, app_window, **kwargs):
        super().__init__(master, fg_color="#1e1e1e", **kwargs)
        self.app_window = app_window
        self.setup_ui()
        
    def setup_ui(self):
        self.header = ctk.CTkFrame(self, fg_color="transparent")
        self.header.pack(fill="x", padx=40, pady=40)
        
        title = ctk.CTkLabel(self.header, text="🖨️ CONFIGURAÇÃO DE IMPRESSORA TÉRMICA (80mm)", font=("Roboto", 28, "bold"))
        title.pack(anchor="w")
        
        self.card = ctk.CTkFrame(self, fg_color="#2b2b2b", corner_radius=10)
        self.card.pack(fill="both", expand=True, padx=40, pady=10)
        
        ctk.CTkLabel(self.card, text="Selecione a Impressora Padrão do PDV:", font=("Roboto", 18)).pack(anchor="w", padx=40, pady=(40, 10))
        
>>>>>>> b8696156ad077242d2bbfc43a202beb2b9ea5c18
        printers = get_available_printers()
        current_printer = get_default_printer()
        if current_printer not in printers:
            printers.append(current_printer)
<<<<<<< HEAD

        self.printer_var = ctk.StringVar(value=current_printer)
        self.dropdown = ctk.CTkOptionMenu(self.card, values=printers, variable=self.printer_var, font=theme.font_body(18), height=50, width=400,
                                           fg_color=theme.SECONDARY, button_color=theme.SECONDARY, button_hover_color=theme.PRIMARY)
        self.dropdown.pack(anchor="w", padx=40, pady=10)

        f_btns = ctk.CTkFrame(self.card, fg_color="transparent")
        f_btns.pack(anchor="w", padx=40, pady=30)

        btn_save = ctk.CTkButton(f_btns, text="DEFINIR COMO PADRÃO", height=45, command=self.save_printer, **theme.btn_success())
        btn_save.pack(side="left", padx=(0, 10))

        btn_test = ctk.CTkButton(f_btns, text="TESTAR IMPRESSÃO", height=45, command=self.test_print, **theme.btn_primary())
        btn_test.pack(side="left")

=======
            
        self.printer_var = ctk.StringVar(value=current_printer)
        self.dropdown = ctk.CTkOptionMenu(self.card, values=printers, variable=self.printer_var, font=("Roboto", 18), height=50, width=400)
        self.dropdown.pack(anchor="w", padx=40, pady=10)
        
        f_btns = ctk.CTkFrame(self.card, fg_color="transparent")
        f_btns.pack(anchor="w", padx=40, pady=30)
        
        btn_save = ctk.CTkButton(f_btns, text="DEFINIR COMO PADRÃO", font=("Roboto", 16, "bold"), fg_color="#2ecc71", hover_color="#27ae60", height=45, command=self.save_printer)
        btn_save.pack(side="left", padx=(0, 10))
        
        btn_test = ctk.CTkButton(f_btns, text="TESTAR IMPRESSÃO", font=("Roboto", 16, "bold"), fg_color="#3498db", hover_color="#2980b9", height=45, command=self.test_print)
        btn_test.pack(side="left")
        
>>>>>>> b8696156ad077242d2bbfc43a202beb2b9ea5c18
    def save_printer(self):
        selected = self.printer_var.get()
        set_default_printer(selected)
        messagebox.showinfo("Sucesso", f"Impressora '{selected}' definida como padrão para o PDV.")
<<<<<<< HEAD

    def test_print(self):
        from tkinter import filedialog
        import os

        class MockProd: nome = "PRODUTO TESTE DE IMPRESSAO"; sku = "TESTE"
        cart = [{'product': MockProd(), 'quantidade': 1, 'preco_unitario': 100.0}]

        text = generate_receipt_text(9999, cart, 100.0, "TESTE MISTO")

        path = filedialog.asksaveasfilename(defaultextension=".pdf", filetypes=[("PDF", "*.pdf")], initialfile="cupom_teste.pdf")
        if path:
            save_receipt_pdf(text, path)
            try: os.startfile(path)
            except: pass
=======
        
    def test_print(self):
        from tkinter import filedialog
        import os
        
        # Gera um carrinho simulado minificado com uma namedtuple genérica só para teste
        class MockProd: nome = "PRODUTO TESTE DE IMPRESSAO"; sku = "TESTE"
        cart = [{'product': MockProd(), 'quantidade': 1, 'preco_unitario': 100.0}]
        
        text = generate_receipt_text(9999, cart, 100.0, "TESTE MISTO")
        
        # Se for para usar PDF como visualização de Teste Universal:
        path = filedialog.asksaveasfilename(defaultextension=".pdf", filetypes=[("PDF", "*.pdf")], initialfile="cupom_teste.pdf")
        if path:
            save_receipt_pdf(text, path)
            try: os.startfile(path) 
            except: pass
>>>>>>> b8696156ad077242d2bbfc43a202beb2b9ea5c18
