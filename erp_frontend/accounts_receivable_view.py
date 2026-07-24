import customtkinter as ctk
from tkinter import messagebox
from erp_frontend.components.table import TableComponent
from erp_backend.services import finance_service, whatsapp_service
from datetime import datetime
<<<<<<< HEAD
from erp_frontend import theme

class AccountsReceivableView(ctk.CTkFrame):
    def __init__(self, master, app_window, **kwargs):
        super().__init__(master, fg_color=theme.BG, **kwargs)
=======

class AccountsReceivableView(ctk.CTkFrame):
    def __init__(self, master, app_window, **kwargs):
        super().__init__(master, fg_color="#1e1e1e", **kwargs)
>>>>>>> b8696156ad077242d2bbfc43a202beb2b9ea5c18
        self.app_window = app_window
        self.setup_ui()
        self.load_data()

    def setup_ui(self):
        top_frame = ctk.CTkFrame(self, fg_color="transparent")
        top_frame.pack(fill="x", padx=20, pady=10)

<<<<<<< HEAD
        self.search_entry = ctk.CTkEntry(top_frame, placeholder_text="🔎 BUSCA: CLIENTE OU Nº DA VENDA...", height=40,
                                          font=theme.font_body(16), fg_color=theme.CARD, border_color=theme.SECONDARY)
        self.search_entry.pack(side="left", fill="x", expand=True, padx=(0, 20))
        self.search_entry.bind("<KeyRelease>", lambda e: self.load_data())

        btn_settle = ctk.CTkButton(top_frame, text="[ DAR BAIXA ]", command=self.settle_payment, **theme.btn_success())
        btn_settle.pack(side="right", padx=5)

        btn_notify = ctk.CTkButton(top_frame, text="[ AVISAR WHATSAPP ]", command=self.notify_customer, **theme.btn_primary())
=======
        self.search_entry = ctk.CTkEntry(top_frame, placeholder_text="🔎 BUSCA: CLIENTE OU Nº DA VENDA...", height=40, font=("Roboto", 16))
        self.search_entry.pack(side="left", fill="x", expand=True, padx=(0, 20))
        self.search_entry.bind("<KeyRelease>", lambda e: self.load_data())

        btn_settle = ctk.CTkButton(top_frame, text="[ DAR BAIXA ]", fg_color="#2ecc71", hover_color="#27ae60", command=self.settle_payment)
        btn_settle.pack(side="right", padx=5)

        btn_notify = ctk.CTkButton(top_frame, text="[ AVISAR WHATSAPP ]", fg_color="#3498db", hover_color="#2980b9", command=self.notify_customer)
>>>>>>> b8696156ad077242d2bbfc43a202beb2b9ea5c18
        btn_notify.pack(side="right", padx=5)

        columns = ("CLIENTE", "VENDA", "PARCELA", "VENCIMENTO", "VALOR", "STATUS")
        self.table = TableComponent(self, columns)
        self.table.column("CLIENTE", width=350, anchor="w")
        self.table.column("VENDA", width=80)
        self.table.column("PARCELA", width=100)
        self.table.column("VENCIMENTO", width=120)
        self.table.column("VALOR", width=120)
        self.table.column("STATUS", width=120)
<<<<<<< HEAD

        self.table.tag_configure("overdue", foreground=theme.DANGER)
        self.table.tag_configure("pending", foreground=theme.PRIMARY)
=======
        
        self.table.tag_configure("overdue", foreground="#e74c3c")
        self.table.tag_configure("pending", foreground="#f1c40f")
>>>>>>> b8696156ad077242d2bbfc43a202beb2b9ea5c18

        self.table.pack(fill="both", expand=True, padx=20, pady=10)

    def load_data(self):
        search_term = self.search_entry.get().strip()
        for item in self.table.get_children():
            self.table.delete(item)

        receivables = finance_service.get_receivables(search_term)
        for row in receivables:
            due_date = datetime.strptime(row['due_date'], '%Y-%m-%d').strftime('%d/%m/%Y')
            status = row['status'].upper()
            tag = row['status']

            self.table.insert("", "end", iid=str(row['id']), values=(
                row['nome_razao_social'],
                f"#{row['sale_id']}",
                f"{row['installment_number']}/{row['total_installments']}",
                due_date,
                f"R$ {row['amount']:.2f}",
                status
            ), tags=(tag,))

    def settle_payment(self):
        selected = self.table.selection()
        if not selected:
            messagebox.showwarning("Aviso", "Selecione uma parcela para dar baixa.")
            return
<<<<<<< HEAD

        installment_id = int(selected[0])
        item_values = self.table.item(selected[0])['values']

        if messagebox.askyesno("Confirmar Baixa", f"Deseja realmente quitar a parcela de {item_values[4]} do cliente {item_values[0]}?"):
=======
        
        installment_id = int(selected[0])
        item_values = self.table.item(selected[0])['values']
        
        if messagebox.askyesno("Confirmar Baixa", f"Deseja realmente quitar a parcela de {item_values[4]} do cliente {item_values[0]}?"):
            # Pergunta a forma de pagamento para registrar no caixa
>>>>>>> b8696156ad077242d2bbfc43a202beb2b9ea5c18
            dialog = ctk.CTkInputDialog(text="Qual a forma de pagamento?", title="Forma de Pagamento")
            payment_method = dialog.get_input()
            if not payment_method: payment_method = "DINHEIRO"

            try:
                finance_service.settle_installment(installment_id, payment_method.upper())
                messagebox.showinfo("Sucesso", "Parcela quitada com sucesso!")
                self.load_data()
            except Exception as e:
                messagebox.showerror("Erro", f"Não foi possível dar baixa na parcela.\n\nDetalhes: {e}")

    def notify_customer(self):
        selected = self.table.selection()
        if not selected:
            messagebox.showwarning("Aviso", "Selecione uma parcela para notificar o cliente.")
            return

        installment_id = int(selected[0])
        details = finance_service.get_installment_details_for_notification(installment_id)

        if not details or not details['telefone']:
            messagebox.showerror("Erro", "Cliente não possui um número de telefone cadastrado.")
            return

        if messagebox.askyesno("Confirmar Envio", f"Enviar notificação via WhatsApp para {details['nome_razao_social']} sobre a parcela de R$ {details['amount']:.2f}?"):
            try:
                due_date_obj = datetime.strptime(details['due_date'], '%Y-%m-%d')
                whatsapp_service.send_installment_due_date_whatsapp(
                    telefone=details['telefone'],
                    customer_name=details['nome_razao_social'],
                    due_date=due_date_obj,
                    amount=details['amount'],
                    installment_str=f"{details['installment_number']}/{details['total_installments']}"
                )
            except Exception as e:
<<<<<<< HEAD
                messagebox.showerror("Erro", f"Falha ao tentar abrir o WhatsApp.\n\nDetalhes: {e}")
=======
                messagebox.showerror("Erro", f"Falha ao tentar abrir o WhatsApp.\n\nDetalhes: {e}")
>>>>>>> b8696156ad077242d2bbfc43a202beb2b9ea5c18
