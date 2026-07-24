import customtkinter as ctk
from tkinter import messagebox
import re
from erp_backend.services import customer_service
from erp_frontend.modals.vehicle_modal import VehicleModal
from erp_frontend import theme

class CustomerModal(ctk.CTkToplevel):
    def __init__(self, master, customer_id=None, on_save=None):
        super().__init__(master)
        self.customer_id = customer_id
        self.on_save = on_save
        self.configure(fg_color=theme.BG)

        self.title("Editar Cliente" if customer_id else "Novo Cliente")
        self.transient(master)
        self.grab_set()

        self.setup_ui()
        if self.customer_id:
            self.load_customer_data()
        self.after(10, self._center_window)

    def _center_window(self):
        self.update_idletasks()
        width = 600
        height = 500
        screen_width = self.winfo_screenwidth()
        screen_height = self.winfo_screenheight()
        x = (screen_width // 2) - (width // 2)
        y = (screen_height // 2) - (height // 2)
        self.geometry(f'{width}x{height}+{x}+{y}')
        self.resizable(False, False)

    def setup_ui(self):
        main_frame = ctk.CTkFrame(self, fg_color=theme.BG)
        main_frame.pack(fill="both", expand=True, padx=20, pady=20)

        ctk.CTkLabel(main_frame, text="Nome / Razão Social:", font=theme.font_body(14), text_color=theme.TEXT).pack(anchor="w")
        self.nome_entry = ctk.CTkEntry(main_frame, height=40, font=theme.font_body(14), fg_color=theme.CARD, border_color=theme.SECONDARY)
        self.nome_entry.pack(fill="x", pady=(0, 10))

        ctk.CTkLabel(main_frame, text="CPF / CNPJ:", font=theme.font_body(14), text_color=theme.TEXT).pack(anchor="w")
        self.cpf_cnpj_entry = ctk.CTkEntry(main_frame, height=40, font=theme.font_body(14), fg_color=theme.CARD, border_color=theme.SECONDARY)
        self.cpf_cnpj_entry.pack(fill="x", pady=(0, 10))

        ctk.CTkLabel(main_frame, text="Telefone:", font=theme.font_body(14), text_color=theme.TEXT).pack(anchor="w")
        self.telefone_entry = ctk.CTkEntry(main_frame, height=40, font=theme.font_body(14), fg_color=theme.CARD, border_color=theme.SECONDARY)
        self.telefone_entry.pack(fill="x", pady=(0, 10))

        ctk.CTkLabel(main_frame, text="Email:", font=theme.font_body(14), text_color=theme.TEXT).pack(anchor="w")
        self.email_entry = ctk.CTkEntry(main_frame, height=40, font=theme.font_body(14), fg_color=theme.CARD, border_color=theme.SECONDARY)
        self.email_entry.pack(fill="x", pady=(0, 10))

        ctk.CTkLabel(main_frame, text="Endereço:", font=theme.font_body(14), text_color=theme.TEXT).pack(anchor="w")
        self.endereco_entry = ctk.CTkEntry(main_frame, height=40, font=theme.font_body(14), fg_color=theme.CARD, border_color=theme.SECONDARY)
        self.endereco_entry.pack(fill="x", pady=(0, 10))

        save_button = ctk.CTkButton(main_frame, text="SALVAR CLIENTE", height=45, command=self.save_customer, **theme.btn_primary(font=theme.font_bold(16)))
        save_button.pack(fill="x", pady=(20, 0))

        self.nome_entry.focus()

    def load_customer_data(self):
        customer = customer_service.get_customer_by_id(self.customer_id)
        if customer:
            self.nome_entry.insert(0, customer.nome_razao_social or "")
            self.cpf_cnpj_entry.insert(0, customer.cpf_cnpj or "")
            self.telefone_entry.insert(0, customer.telefone or "")
            self.email_entry.insert(0, customer.email or "")
            self.endereco_entry.insert(0, customer.endereco or "")

    def save_customer(self):
        nome = self.nome_entry.get().strip()
        cpf_cnpj_raw = self.cpf_cnpj_entry.get().strip()
        telefone_raw = self.telefone_entry.get().strip()

        if not all(c.isalpha() or c.isspace() for c in nome):
            messagebox.showerror("Erro de Validação", "O campo 'Nome / Razão Social' deve conter apenas letras e espaços.")
            return

        cpf_cnpj_limpo = re.sub(r'[^0-9]', '', cpf_cnpj_raw)
        if not (len(cpf_cnpj_limpo) == 11 or len(cpf_cnpj_limpo) == 14):
            messagebox.showerror("Erro de Validação", "O CPF deve ter 11 dígitos e o CNPJ deve ter 14 dígitos (apenas números).")
            return

        telefone_limpo = re.sub(r'[^0-9]', '', telefone_raw)
        if not (len(telefone_limpo) == 10 or len(telefone_limpo) == 11):
            messagebox.showerror("Erro de Validação", "O telefone deve conter 10 ou 11 dígitos (DDD + Número).")
            return

        data = {
            "id": self.customer_id,
            "nome_razao_social": nome,
            "cpf_cnpj": cpf_cnpj_limpo,
            "telefone": telefone_limpo,
            "email": self.email_entry.get(),
            "endereco": self.endereco_entry.get()
        }

        try:
            new_or_updated_customer_id = customer_service.create_or_update_customer(data)

            if not self.customer_id:
                if messagebox.askyesno("Sucesso", "Cliente salvo com sucesso!\nDeseja cadastrar um veículo para este cliente agora?"):
                    VehicleModal(self, customer_id=new_or_updated_customer_id).get_input()
            else:
                messagebox.showinfo("Sucesso", "Cliente atualizado com sucesso!")

            if self.on_save:
                self.on_save()

            self.destroy()

        except ValueError as e:
            messagebox.showerror("Erro de Validação", str(e))
        except Exception as e:
            messagebox.showerror("Erro", f"Ocorreu um erro inesperado: {e}")
