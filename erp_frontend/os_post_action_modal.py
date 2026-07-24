import customtkinter as ctk
from tkinter import messagebox, filedialog
import os
from erp_backend.services.pdf_service import generate_os_pdf
from erp_backend.services.whatsapp_service import send_os_whatsapp
from erp_backend.services.printer_service import get_default_printer, generate_os_receipt_text, save_receipt_pdf
from erp_frontend import theme

class OSPostActionModal(ctk.CTkToplevel):
    def __init__(self, master, os_data, items):
        super().__init__(master)
        self.title("Ações da Ordem de Serviço")
        self.geometry("400x380")
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

        desktop = os.path.join(os.path.join(os.environ['USERPROFILE']), 'Desktop')
        
        if printer_name == "PDF (Salvar arquivo)":
            filepath = os.path.join(desktop, f"Cupom_OS_{self.os_data.get('id', 0):05d}.pdf")
            save_receipt_pdf(text_receipt, filepath)
            messagebox.showinfo("Cupom Salvo em PDF", f"O cupom da OS foi salvo como PDF em:\n{filepath}")
        else:
            from erp_backend.services.printer_service import save_receipt_txt
            filepath = os.path.join(desktop, f"Cupom_OS_{self.os_data.get('id', 0):05d}.txt")
            save_receipt_txt(text_receipt, filepath)
            messagebox.showinfo("Cupom de Texto Gerado", f"Cupom da OS salvo como '{os.path.basename(filepath)}' na sua Área de Trabalho.\n\nEnvie este arquivo para sua impressora térmica.")
        
        try: os.startfile(filepath)
        except Exception: pass
