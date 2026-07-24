import customtkinter as ctk
from tkinter import messagebox, filedialog
import os
from erp_backend.services.pdf_service import generate_os_pdf
from erp_backend.services.whatsapp_service import send_os_whatsapp
from erp_backend.services.printer_service import get_default_printer, generate_os_receipt_text, save_receipt_pdf
<<<<<<< HEAD
from erp_frontend import theme
=======
>>>>>>> b8696156ad077242d2bbfc43a202beb2b9ea5c18

class OSPostActionModal(ctk.CTkToplevel):
    def __init__(self, master, os_data, items):
        super().__init__(master)
        self.title("Ações da Ordem de Serviço")
        self.geometry("400x380")
<<<<<<< HEAD
        self.configure(fg_color=theme.BG)
        self.transient(master)
        self.grab_set()

        self.os_data = os_data
        self.items = items

        self.setup_ui()

    def setup_ui(self):
        lbl = ctk.CTkLabel(self, text="✅ OS Salva com Sucesso!", font=theme.font_heading(20), text_color=theme.SUCCESS)
        lbl.pack(pady=(20, 10))

        ctk.CTkLabel(self, text="Escolha uma ação para este documento:", font=theme.font_body(14), text_color=theme.TEXT_MUTED).pack(pady=(0, 20))

        btn_pdf = ctk.CTkButton(self, text="📄 Gerar PDF (A4)", height=45, command=self.generate_pdf, **theme.btn_primary())
        btn_pdf.pack(fill="x", padx=40, pady=5)

        btn_wpp = ctk.CTkButton(self, text="📲 Enviar via WhatsApp", height=45, command=self.send_whatsapp, **theme.btn_success())
        btn_wpp.pack(fill="x", padx=40, pady=5)

        btn_print = ctk.CTkButton(self, text="🖨️ Imprimir OS (80mm)", height=45, command=self.print_80mm,
                                   **theme.btn_secondary(fg_color=theme.INFO, hover_color="#2563eb", text_color="#ffffff"))
        btn_print.pack(fill="x", padx=40, pady=5)

        btn_close = ctk.CTkButton(self, text="❌ Fechar", height=45, command=self.destroy, **theme.btn_danger())
=======
        self.transient(master)
        self.grab_set()
        
        self.os_data = os_data
        self.items = items
        
        self.setup_ui()
        
    def setup_ui(self):
        lbl = ctk.CTkLabel(self, text="✅ OS Salva com Sucesso!", font=("Roboto", 20, "bold"), text_color="#2ecc71")
        lbl.pack(pady=(20, 10))
        
        ctk.CTkLabel(self, text="Escolha uma ação para este documento:", font=("Roboto", 14)).pack(pady=(0, 20))
        
        btn_pdf = ctk.CTkButton(self, text="📄 Gerar PDF (A4)", height=45, font=("Roboto", 14, "bold"), command=self.generate_pdf)
        btn_pdf.pack(fill="x", padx=40, pady=5)
        
        btn_wpp = ctk.CTkButton(self, text="📲 Enviar via WhatsApp", height=45, font=("Roboto", 14, "bold"), fg_color="#27ae60", hover_color="#2ecc71", command=self.send_whatsapp)
        btn_wpp.pack(fill="x", padx=40, pady=5)
        
        btn_print = ctk.CTkButton(self, text="🖨️ Imprimir OS (80mm)", height=45, font=("Roboto", 14, "bold"), fg_color="#3498db", hover_color="#2980b9", command=self.print_80mm)
        btn_print.pack(fill="x", padx=40, pady=5)
        
        btn_close = ctk.CTkButton(self, text="❌ Fechar", height=45, font=("Roboto", 14), fg_color="#e74c3c", hover_color="#c0392b", command=self.destroy)
>>>>>>> b8696156ad077242d2bbfc43a202beb2b9ea5c18
        btn_close.pack(fill="x", padx=40, pady=(20, 10))

    def generate_pdf(self):
        filepath = filedialog.asksaveasfilename(defaultextension=".pdf", filetypes=[("PDF", "*.pdf")], initialfile=f"OS_{self.os_data.get('id', 0):05d}.pdf")
        if filepath:
            generate_os_pdf(filepath, self.os_data, self.items)
            try: os.startfile(filepath)
            except Exception: pass

    def send_whatsapp(self):
        dialog = ctk.CTkInputDialog(text="Digite o número do WhatsApp do cliente (com DDD):", title="Enviar WhatsApp")
        telefone = dialog.get_input()
        if telefone:
            send_os_whatsapp(telefone, self.os_data.get('id', 0))

    def print_80mm(self):
        printer_name = get_default_printer()
        text_receipt = generate_os_receipt_text(self.os_data.get('id', 0), self.os_data, self.items)
<<<<<<< HEAD

        if "PDF" in printer_name:
            project_root = os.path.abspath(os.path.join(os.path.dirname(__file__), '..'))
            filename = f"Cupom_OS_{self.os_data.get('id', 0):05d}.pdf"
            filepath = os.path.join(project_root, filename)

            save_receipt_pdf(text_receipt, filepath)
            messagebox.showinfo("PDF Gerado", f"O recibo foi salvo como '{filename}' na pasta do projeto.")
            try:
                os.startfile(filepath)
=======
        
        if "PDF" in printer_name:
            # Salva o PDF automaticamente na pasta do projeto
            project_root = os.path.abspath(os.path.join(os.path.dirname(__file__), '..'))
            filename = f"Cupom_OS_{self.os_data.get('id', 0):05d}.pdf"
            filepath = os.path.join(project_root, filename)
            
            save_receipt_pdf(text_receipt, filepath)
            messagebox.showinfo("PDF Gerado", f"O recibo foi salvo como '{filename}' na pasta do projeto.")
            try:
                os.startfile(filepath) # Tenta abrir o PDF automaticamente
>>>>>>> b8696156ad077242d2bbfc43a202beb2b9ea5c18
            except Exception:
                pass
        else:
            print(f"--- ENVIANDO PARA IMPRESSORA {printer_name} ---\n{text_receipt}")
<<<<<<< HEAD
            messagebox.showinfo("Sucesso", f"Enviado para a impressora: {printer_name}")
=======
            messagebox.showinfo("Sucesso", f"Enviado para a impressora: {printer_name}")
>>>>>>> b8696156ad077242d2bbfc43a202beb2b9ea5c18
