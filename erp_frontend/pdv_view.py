import customtkinter as ctk
from tkinter import messagebox, ttk
from erp_frontend.components.table import TableComponent
from erp_frontend.components.scanner_input import InputBarScanner
from erp_backend.services.printer_service import get_default_printer, generate_receipt_text, save_receipt_pdf
from erp_backend.services.product_service import search_by_barcode, get_by_sku
from erp_backend.services.sales_service import process_sale_transaction
<<<<<<< HEAD
from erp_frontend import theme
=======
>>>>>>> b8696156ad077242d2bbfc43a202beb2b9ea5c18

class DiscountModal(ctk.CTkToplevel):
    def __init__(self, master, item_total_price, current_discount=0.0):
        super().__init__(master)
        self.title("Aplicar Desconto no Item")
        self.geometry("450x400")
<<<<<<< HEAD
        self.configure(fg_color=theme.BG)
=======
>>>>>>> b8696156ad077242d2bbfc43a202beb2b9ea5c18
        self.transient(master)
        self.grab_set()

        self.item_total_price = item_total_price
        self.result = current_discount
        self._updating = False

        self.setup_ui()
<<<<<<< HEAD
        self.on_value_change()
=======
        self.on_value_change() # Initialize with current discount
>>>>>>> b8696156ad077242d2bbfc43a202beb2b9ea5c18
        self.bind("<Escape>", lambda e: self.destroy())

    def setup_ui(self):
        main_frame = ctk.CTkFrame(self, fg_color="transparent")
        main_frame.pack(fill="both", expand=True, padx=20, pady=20)

<<<<<<< HEAD
        ctk.CTkLabel(main_frame, text=f"Valor Original do Item: R$ {self.item_total_price:.2f}", font=theme.font_body(16), text_color=theme.TEXT).pack(pady=(0, 20))

        f_percent = ctk.CTkFrame(main_frame, fg_color="transparent")
        f_percent.pack(fill="x", pady=5)
        ctk.CTkLabel(f_percent, text="Desconto (%):", font=theme.font_bold(14), text_color=theme.TEXT).pack(side="left", padx=(0, 10))
        self.ent_percent = ctk.CTkEntry(f_percent, font=theme.font_body(16), fg_color=theme.CARD, border_color=theme.SECONDARY)
=======
        ctk.CTkLabel(main_frame, text=f"Valor Original do Item: R$ {self.item_total_price:.2f}", font=("Roboto", 16)).pack(pady=(0, 20))

        f_percent = ctk.CTkFrame(main_frame, fg_color="transparent")
        f_percent.pack(fill="x", pady=5)
        ctk.CTkLabel(f_percent, text="Desconto (%):", font=("Roboto", 14, "bold")).pack(side="left", padx=(0, 10))
        self.ent_percent = ctk.CTkEntry(f_percent, font=("Roboto", 16))
>>>>>>> b8696156ad077242d2bbfc43a202beb2b9ea5c18
        self.ent_percent.pack(side="left", fill="x", expand=True)
        self.ent_percent.bind("<KeyRelease>", self.on_percent_change)

        f_value = ctk.CTkFrame(main_frame, fg_color="transparent")
        f_value.pack(fill="x", pady=5)
<<<<<<< HEAD
        ctk.CTkLabel(f_value, text="Desconto (R$):", font=theme.font_bold(14), text_color=theme.TEXT).pack(side="left", padx=(0, 10))
        self.ent_value = ctk.CTkEntry(f_value, font=theme.font_body(16), fg_color=theme.CARD, border_color=theme.SECONDARY)
=======
        ctk.CTkLabel(f_value, text="Desconto (R$):", font=("Roboto", 14, "bold")).pack(side="left", padx=(0, 10))
        self.ent_value = ctk.CTkEntry(f_value, font=("Roboto", 16))
>>>>>>> b8696156ad077242d2bbfc43a202beb2b9ea5c18
        self.ent_value.pack(side="left", fill="x", expand=True)
        self.ent_value.insert(0, f"{self.result:.2f}")
        self.ent_value.bind("<KeyRelease>", self.on_value_change)

<<<<<<< HEAD
        self.lbl_final_price = ctk.CTkLabel(main_frame, text="", font=theme.font_title(20), text_color=theme.SUCCESS)
=======
        self.lbl_final_price = ctk.CTkLabel(main_frame, text="", font=("Roboto", 20, "bold"), text_color="#2ecc71")
>>>>>>> b8696156ad077242d2bbfc43a202beb2b9ea5c18
        self.lbl_final_price.pack(pady=20)

        btn_frame = ctk.CTkFrame(main_frame, fg_color="transparent")
        btn_frame.pack(side="bottom", fill="x", pady=10)
<<<<<<< HEAD
        ctk.CTkButton(btn_frame, text="APLICAR", command=self.apply, height=40, **theme.btn_primary(font=theme.font_bold(16))).pack(fill="x")
=======
        ctk.CTkButton(btn_frame, text="APLICAR", command=self.apply, height=40, font=("Roboto", 16, "bold")).pack(fill="x")
>>>>>>> b8696156ad077242d2bbfc43a202beb2b9ea5c18

    def on_percent_change(self, event=None):
        if self._updating: return
        self._updating = True
        try:
            percent = float(self.ent_percent.get().replace(",", "."))
            value = (self.item_total_price * percent) / 100.0
            self.ent_value.delete(0, "end")
            self.ent_value.insert(0, f"{value:.2f}")
            self.update_final_price(value)
        except (ValueError, TypeError):
            self.update_final_price(0)
        self._updating = False

    def on_value_change(self, event=None):
        if self._updating: return
        self._updating = True
        try:
            value = float(self.ent_value.get().replace(",", "."))
            percent = (value / self.item_total_price) * 100.0 if self.item_total_price > 0 else 0.0
            self.ent_percent.delete(0, "end")
            self.ent_percent.insert(0, f"{percent:.2f}")
            self.update_final_price(value)
        except (ValueError, TypeError):
            self.update_final_price(0)
        self._updating = False

    def update_final_price(self, discount_value):
        final_price = self.item_total_price - discount_value
        self.lbl_final_price.configure(text=f"Valor Final do Item: R$ {final_price:.2f}")

    def apply(self):
        try:
            self.result = float(self.ent_value.get().replace(",", "."))
        except (ValueError, TypeError):
            self.result = 0.0
        self.destroy()

    def get_input(self):
        self.master.wait_window(self)
        return self.result

class PaymentModal(ctk.CTkToplevel):
    def __init__(self, master, cart, total, on_success):
        super().__init__(master)
        self.title("Finalizar Venda")
        self.geometry("800x600")
<<<<<<< HEAD
        self.configure(fg_color=theme.BG)
        self.transient(master)
        self.grab_set()

=======
        self.transient(master)
        self.grab_set()
        
>>>>>>> b8696156ad077242d2bbfc43a202beb2b9ea5c18
        self.cart = cart
        self.total = total
        self.on_success = on_success
        self.payment_methods = ["DINHEIRO", "PIX", "CARTÃO CRÉDITO", "CARTÃO DÉBITO", "CREDIARIO", "MISTO"]
        self.current_payment_idx = 0
<<<<<<< HEAD
        self.customer_id = None

        self.setup_ui()
        self.update_customer_label()
        self.bind_shortcuts()

    def setup_ui(self):
        self.lbl_total = ctk.CTkLabel(self, text=f"TOTAL DA VENDA: R$ {self.total:.2f}", font=theme.font_title(44), text_color=theme.SUCCESS)
        self.lbl_total.pack(pady=20)

        content = ctk.CTkFrame(self, fg_color="transparent")
        content.pack(fill="both", expand=True, padx=20, pady=10)

        f_summary = ctk.CTkFrame(content, **theme.card_frame_kwargs())
        f_summary.pack(side="left", fill="both", expand=True, padx=(0, 10))
        self.lbl_customer = ctk.CTkLabel(f_summary, text="Cliente: CONSUMIDOR FINAL", font=theme.font_body(14), text_color=theme.TEXT)
        self.lbl_customer.pack(pady=5)

        ctk.CTkLabel(f_summary, text="Resumo da Venda", font=theme.font_heading(18), text_color=theme.TEXT).pack(pady=10)

        summary_text = ctk.CTkTextbox(f_summary, font=theme.font_body(16), state="normal", fg_color=theme.CARD_ALT)
=======
        self.customer_id = None # Armazena o cliente selecionado para a venda
        
        self.setup_ui()
        self.update_customer_label()
        self.bind_shortcuts()
        
    def setup_ui(self):
        self.lbl_total = ctk.CTkLabel(self, text=f"TOTAL DA VENDA: R$ {self.total:.2f}", font=("Roboto", 48, "bold"), text_color="#2ecc71")
        self.lbl_total.pack(pady=20)
        
        content = ctk.CTkFrame(self, fg_color="transparent")
        content.pack(fill="both", expand=True, padx=20, pady=10)
        
        f_summary = ctk.CTkFrame(content, fg_color="#2b2b2b")
        f_summary.pack(side="left", fill="both", expand=True, padx=(0, 10))
        self.lbl_customer = ctk.CTkLabel(f_summary, text="Cliente: CONSUMIDOR FINAL", font=("Roboto", 14))
        self.lbl_customer.pack(pady=5)

        ctk.CTkLabel(f_summary, text="Resumo da Venda", font=("Roboto", 18, "bold")).pack(pady=10)
        
        summary_text = ctk.CTkTextbox(f_summary, font=("Roboto", 16), state="normal")
>>>>>>> b8696156ad077242d2bbfc43a202beb2b9ea5c18
        summary_text.pack(fill="both", expand=True, padx=10, pady=10)
        for item in self.cart:
            subtotal = (item['quantidade'] * item['preco_unitario']) - item.get('desconto_item', 0.0)
            qtd = f"{item['quantidade']:.3f}".rstrip('0').rstrip('.')
            summary_text.insert("end", f"{qtd}x {item['product'].nome[:25]} - R$ {subtotal:.2f}\n")
        summary_text.configure(state="disabled")
<<<<<<< HEAD

        f_pay = ctk.CTkFrame(content, **theme.card_frame_kwargs())
        f_pay.pack(side="right", fill="both", expand=True, padx=(10, 0))

        ctk.CTkLabel(f_pay, text="Forma de Pagamento (F4)", font=theme.font_heading(16), text_color=theme.TEXT).pack(pady=(10, 5))

        ctk.CTkLabel(f_pay, text="Desconto Total (R$):", font=theme.font_body(16), text_color=theme.TEXT).pack(anchor="w", padx=20)
        self.ent_desconto = ctk.CTkEntry(f_pay, font=theme.font_body(24), height=40, fg_color=theme.CARD_ALT, border_color=theme.SECONDARY)
        self.ent_desconto.pack(fill="x", padx=20, pady=5)
        self.ent_desconto.bind("<KeyRelease>", self.update_total_with_discount)

        self.btn_pay_method = ctk.CTkButton(f_pay, text=self.payment_methods[self.current_payment_idx], height=50, command=self.toggle_payment,
                                             **theme.btn_primary(font=theme.font_bold(24)))
        self.btn_pay_method.pack(pady=10, fill="x", padx=20)

        self.f_dinheiro = ctk.CTkFrame(f_pay, fg_color="transparent")

        ctk.CTkLabel(self.f_dinheiro, text="Valor Recebido (R$):", font=theme.font_body(16), text_color=theme.TEXT).pack(anchor="w", padx=20)
        self.ent_recebido = ctk.CTkEntry(self.f_dinheiro, font=theme.font_bold(32), height=50, fg_color=theme.CARD_ALT, border_color=theme.SECONDARY)
        self.ent_recebido.pack(fill="x", padx=20, pady=5)
        self.ent_recebido.bind("<KeyRelease>", self.calc_troco)

        self.lbl_troco = ctk.CTkLabel(self.f_dinheiro, text="Troco: R$ 0.00", font=theme.font_title(28), text_color=theme.PRIMARY)
        self.lbl_troco.pack(pady=20)

        self.f_crediario = ctk.CTkFrame(f_pay, fg_color="transparent")
        ctk.CTkLabel(self.f_crediario, text="Número de Parcelas:", font=theme.font_body(16), text_color=theme.TEXT).pack(anchor="w", padx=20)
        self.ent_installments = ctk.CTkEntry(self.f_crediario, font=theme.font_bold(32), height=50, fg_color=theme.CARD_ALT, border_color=theme.SECONDARY)
=======
        
        f_pay = ctk.CTkFrame(content, fg_color="#2b2b2b")
        f_pay.pack(side="right", fill="both", expand=True, padx=(10, 0))
        
        ctk.CTkLabel(f_pay, text="Forma de Pagamento (F4)", font=("Roboto", 16, "bold")).pack(pady=(10, 5))
        
        ctk.CTkLabel(f_pay, text="Desconto Total (R$):", font=("Roboto", 16)).pack(anchor="w", padx=20)
        self.ent_desconto = ctk.CTkEntry(f_pay, font=("Roboto", 24), height=40)
        self.ent_desconto.pack(fill="x", padx=20, pady=5)
        self.ent_desconto.bind("<KeyRelease>", self.update_total_with_discount)
        
        self.btn_pay_method = ctk.CTkButton(f_pay, text=self.payment_methods[self.current_payment_idx], font=("Roboto", 24, "bold"), height=50, command=self.toggle_payment)
        self.btn_pay_method.pack(pady=10, fill="x", padx=20)
        
        self.f_dinheiro = ctk.CTkFrame(f_pay, fg_color="transparent")
        
        ctk.CTkLabel(self.f_dinheiro, text="Valor Recebido (R$):", font=("Roboto", 16)).pack(anchor="w", padx=20)
        self.ent_recebido = ctk.CTkEntry(self.f_dinheiro, font=("Roboto", 32, "bold"), height=50)
        self.ent_recebido.pack(fill="x", padx=20, pady=5)
        self.ent_recebido.bind("<KeyRelease>", self.calc_troco)
        
        self.lbl_troco = ctk.CTkLabel(self.f_dinheiro, text="Troco: R$ 0.00", font=("Roboto", 28, "bold"), text_color="#f1c40f")
        self.lbl_troco.pack(pady=20)
        
        # Frame para crediário
        self.f_crediario = ctk.CTkFrame(f_pay, fg_color="transparent")
        ctk.CTkLabel(self.f_crediario, text="Número de Parcelas:", font=("Roboto", 16)).pack(anchor="w", padx=20)
        self.ent_installments = ctk.CTkEntry(self.f_crediario, font=("Roboto", 32, "bold"), height=50)
>>>>>>> b8696156ad077242d2bbfc43a202beb2b9ea5c18
        self.ent_installments.pack(fill="x", padx=20, pady=5)
        self.ent_installments.insert(0, "1")

        self.update_pay_form()
<<<<<<< HEAD

        f_btn = ctk.CTkFrame(self, fg_color="transparent")
        f_btn.pack(fill="x", side="bottom", pady=20)

        btn_confirm = ctk.CTkButton(f_btn, text="[ENTER] CONFIRMAR VENDA", height=50, command=self.confirm, **theme.btn_success(font=theme.font_bold(20)))
        btn_confirm.pack(side="right", padx=20)

        btn_cancel = ctk.CTkButton(f_btn, text="[ESC] CANCELAR", height=50, command=self.destroy, **theme.btn_danger(font=theme.font_body(20)))
        btn_cancel.pack(side="right")

    def update_customer_label(self):
        if self.customer_id:
            self.lbl_customer.configure(text=f"Cliente ID: {self.customer_id}", text_color=theme.SUCCESS)
=======
        
        f_btn = ctk.CTkFrame(self, fg_color="transparent")
        f_btn.pack(fill="x", side="bottom", pady=20)
        
        btn_confirm = ctk.CTkButton(f_btn, text="[ENTER] CONFIRMAR VENDA", font=("Roboto", 20, "bold"), height=50, fg_color="#2ecc71", hover_color="#27ae60", command=self.confirm)
        btn_confirm.pack(side="right", padx=20)
        
        btn_cancel = ctk.CTkButton(f_btn, text="[ESC] CANCELAR", font=("Roboto", 20), height=50, fg_color="#e74c3c", hover_color="#c0392b", command=self.destroy)
        btn_cancel.pack(side="right")
        
    def update_customer_label(self):
        if self.customer_id:
            # Aqui poderíamos buscar o nome do cliente, mas para manter simples, apenas mostramos o ID
            self.lbl_customer.configure(text=f"Cliente ID: {self.customer_id}", text_color="#2ecc71")
>>>>>>> b8696156ad077242d2bbfc43a202beb2b9ea5c18

    def bind_shortcuts(self):
        self.bind("<F4>", lambda e: self.toggle_payment())
        self.bind("<Return>", lambda e: self.confirm())
        self.bind("<Escape>", lambda e: self.destroy())
<<<<<<< HEAD

=======
        
>>>>>>> b8696156ad077242d2bbfc43a202beb2b9ea5c18
    def toggle_payment(self):
        self.current_payment_idx = (self.current_payment_idx + 1) % len(self.payment_methods)
        self.btn_pay_method.configure(text=self.payment_methods[self.current_payment_idx])
        self.update_pay_form()
<<<<<<< HEAD

=======
        
>>>>>>> b8696156ad077242d2bbfc43a202beb2b9ea5c18
    def update_pay_form(self):
        selected_method = self.payment_methods[self.current_payment_idx]
        if selected_method == "DINHEIRO":
            self.f_dinheiro.pack(fill="x", pady=10)
            self.f_crediario.pack_forget()
            self.ent_recebido.focus_set()
        elif selected_method == "CREDIARIO":
            self.f_dinheiro.pack_forget()
            self.f_crediario.pack(fill="x", pady=10)
            self.ent_installments.focus_set()
<<<<<<< HEAD
=======
            # Se o cliente ainda não foi selecionado, força a seleção
>>>>>>> b8696156ad077242d2bbfc43a202beb2b9ea5c18
            if not self.customer_id:
                self.select_customer_for_credit()

        else:
            self.f_dinheiro.pack_forget()
            self.f_crediario.pack_forget()
            self.focus_set()
<<<<<<< HEAD

=======
            
>>>>>>> b8696156ad077242d2bbfc43a202beb2b9ea5c18
    def update_total_with_discount(self, event=None):
        try:
            desc = float(self.ent_desconto.get().replace(",", "."))
        except ValueError:
            desc = 0.0
        novo_total = max(0.0, self.total - desc)
        self.lbl_total.configure(text=f"TOTAL DA VENDA: R$ {novo_total:.2f}")
        self.calc_troco()

    def calc_troco(self, event=None):
        try:
            val = float(self.ent_recebido.get().replace(",", "."))
            try: desc = float(self.ent_desconto.get().replace(",", "."))
            except ValueError: desc = 0.0
            novo_total = max(0.0, self.total - desc)
            troco = val - novo_total
            if troco >= 0:
<<<<<<< HEAD
                self.lbl_troco.configure(text=f"Troco: R$ {troco:.2f}", text_color=theme.SUCCESS)
            else:
                self.lbl_troco.configure(text=f"Faltam: R$ {abs(troco):.2f}", text_color=theme.DANGER)
        except ValueError:
            self.lbl_troco.configure(text="Troco: R$ 0.00", text_color=theme.PRIMARY)

    def select_customer_for_credit(self):
        from erp_frontend.modals.customer_search_modal import CustomerSearchModal
        messagebox.showinfo("Cliente Necessário", "Para vendas no crediário, é obrigatório selecionar um cliente.")

=======
                self.lbl_troco.configure(text=f"Troco: R$ {troco:.2f}", text_color="#2ecc71")
            else:
                self.lbl_troco.configure(text=f"Faltam: R$ {abs(troco):.2f}", text_color="#e74c3c")
        except ValueError:
            self.lbl_troco.configure(text="Troco: R$ 0.00", text_color="#f1c40f")
            
    def select_customer_for_credit(self):
        from erp_frontend.modals.customer_search_modal import CustomerSearchModal
        messagebox.showinfo("Cliente Necessário", "Para vendas no crediário, é obrigatório selecionar um cliente.")
        
>>>>>>> b8696156ad077242d2bbfc43a202beb2b9ea5c18
        dialog = CustomerSearchModal(self)
        customer_id = dialog.get_input()
        if customer_id:
            self.customer_id = customer_id
            self.update_customer_label()

    def confirm(self):
        try:
            desc_total = float(self.ent_desconto.get().replace(",", "."))
        except ValueError:
            desc_total = 0.0
        final_total = max(0.0, self.total - desc_total)
        payment_method = self.payment_methods[self.current_payment_idx]

        if payment_method == "DINHEIRO":
            try:
                val = float(self.ent_recebido.get().replace(",", "."))
                if val < final_total:
                    messagebox.showwarning("Aviso", "Valor recebido menor que o total da venda.")
                    return
            except ValueError:
                messagebox.showwarning("Aviso", "Valor recebido inválido.")
                return
<<<<<<< HEAD
=======
                
>>>>>>> b8696156ad077242d2bbfc43a202beb2b9ea5c18

        installments = 1
        if payment_method == 'CREDIARIO':
            try:
                installments = int(self.ent_installments.get())
                if installments <= 0: raise ValueError()
            except ValueError:
                messagebox.showwarning("Aviso", "Número de parcelas inválido.")
                return
            if not self.customer_id:
                messagebox.showerror("Cliente não Selecionado", "É obrigatório selecionar um cliente para vendas no crediário.")
<<<<<<< HEAD
                self.select_customer_for_credit()
=======
                self.select_customer_for_credit() # Tenta de novo
>>>>>>> b8696156ad077242d2bbfc43a202beb2b9ea5c18
                return

        items = [{'product_id': i['product'].id, 'quantidade': i['quantidade'], 'preco_unitario': i['preco_unitario'], 'desconto_item': i.get('desconto_item', 0.0)} for i in self.cart]
        try:
            sale_id = process_sale_transaction(customer_id=self.customer_id, items=items, forma_pagamento=payment_method, desconto_total=desc_total, installments=installments)
<<<<<<< HEAD

            printer_name = get_default_printer()
            text_receipt = generate_receipt_text(sale_id, self.cart, final_total, payment_method, desc_total)

=======
            
            # DISPARO DA IMPRESSÃO DO CUPOM 80MM
            printer_name = get_default_printer()
            text_receipt = generate_receipt_text(sale_id, self.cart, final_total, payment_method, desc_total)
            
>>>>>>> b8696156ad077242d2bbfc43a202beb2b9ea5c18
            if "PDF" in printer_name:
                from tkinter import filedialog
                import os
                filepath = filedialog.asksaveasfilename(defaultextension=".pdf", filetypes=[("PDF", "*.pdf")], initialfile=f"cupom_venda_{sale_id}.pdf")
                if filepath:
                    save_receipt_pdf(text_receipt, filepath)
<<<<<<< HEAD
                    try: os.startfile(filepath)
                    except: pass
            else:
=======
                    try: os.startfile(filepath) 
                    except: pass
            else:
                # Comunicação Direta LPT1/COM1 ESC/POS
>>>>>>> b8696156ad077242d2bbfc43a202beb2b9ea5c18
                print(f"--- ENVIANDO PARA IMPRESSORA {printer_name} ---\n{text_receipt}")

            self.on_success()
            self.destroy()
        except Exception as e:
            messagebox.showerror("Erro ao Finalizar", str(e))

class PDVView(ctk.CTkFrame):
    def __init__(self, master, app_window, **kwargs):
<<<<<<< HEAD
        super().__init__(master, fg_color=theme.BG, **kwargs)
        self.app_window = app_window
        self.cart = []

        self.setup_ui()
        self.bind_shortcuts()

    def setup_ui(self):
        self.scanner = InputBarScanner(self, self.add_product_from_scanner)
        self.scanner.pack(side="top", fill="x", padx=20, pady=20)

        style = ttk.Style()
        style.configure("PDV.Treeview", rowheight=55, font=theme.font_bold(18), background=theme.BG, foreground=theme.TEXT)
        style.configure("PDV.Treeview.Heading", font=theme.font_bold(16), background=theme.CARD, foreground=theme.TEXT_MUTED)

=======
        super().__init__(master, fg_color="#1e1e1e", **kwargs)
        self.app_window = app_window
        self.cart = []
        
        self.setup_ui()
        self.bind_shortcuts()
        
    def setup_ui(self):
        self.scanner = InputBarScanner(self, self.add_product_from_scanner)
        self.scanner.pack(side="top", fill="x", padx=20, pady=20)
        
        style = ttk.Style()
        style.configure("PDV.Treeview", rowheight=55, font=("Roboto", 18, "bold"), background="#1e1e1e", foreground="#ffffff")
        style.configure("PDV.Treeview.Heading", font=("Roboto", 16, "bold"), background="#2b2b2b", foreground="#aaaaaa")
        
>>>>>>> b8696156ad077242d2bbfc43a202beb2b9ea5c18
        columns = ("PRODUTO", "QTD", "UNIT", "DESC.", "SUBTOTAL")
        self.table = TableComponent(self, columns, style="PDV.Treeview")
        self.table.column("PRODUTO", width=400, anchor="w")
        self.table.column("QTD", width=80)
        self.table.column("UNIT", width=120)
        self.table.column("DESC.", width=100)
        self.table.column("SUBTOTAL", width=120)
<<<<<<< HEAD

        self.table.tag_configure("last_added", background=theme.PRIMARY, foreground=theme.PRIMARY_FOREGROUND)

        self.table.pack(side="top", fill="both", expand=True, padx=20)

        self.bottom_frame = ctk.CTkFrame(self, fg_color="transparent")
        self.bottom_frame.pack(side="bottom", fill="x", padx=20, pady=20)

        self.total_lbl = ctk.CTkLabel(self.bottom_frame, text="TOTAL: R$ 0.00", font=theme.font_title(60), text_color=theme.SUCCESS)
        self.total_lbl.pack(side="right", padx=20)

        actions_frame = ctk.CTkFrame(self.bottom_frame, fg_color="transparent")
        actions_frame.pack(side="left", padx=10, fill="x", expand=True)

        btn_finalize = ctk.CTkButton(actions_frame, text="[F2] Finalizar Venda", height=45, command=self.finalize_sale, **theme.btn_success(font=theme.font_bold(16)))
        btn_finalize.pack(side="left", padx=5)

        btn_discount = ctk.CTkButton(actions_frame, text="[F3] Desconto Item", height=45, command=self.apply_item_discount, **theme.btn_primary(font=theme.font_bold(16)))
        btn_discount.pack(side="left", padx=5)

        btn_remove = ctk.CTkButton(actions_frame, text="[DEL] Remover Item", height=45, command=self.remove_selected_item, **theme.btn_danger(font=theme.font_bold(16)))
        btn_remove.pack(side="left", padx=5)

        btn_cancel = ctk.CTkButton(actions_frame, text="[ESC] Cancelar Venda", height=45, command=self.clear_sale, **theme.btn_secondary(font=theme.font_bold(16)))
        btn_cancel.pack(side="left", padx=5)

=======
        
        self.table.tag_configure("last_added", background="#2980b9", foreground="white")
        
        self.table.pack(side="top", fill="both", expand=True, padx=20)
        
        self.bottom_frame = ctk.CTkFrame(self, fg_color="transparent")
        self.bottom_frame.pack(side="bottom", fill="x", padx=20, pady=20)
        
        self.total_lbl = ctk.CTkLabel(self.bottom_frame, text="TOTAL: R$ 0.00", font=("Roboto", 60, "bold"), text_color="#2ecc71")
        self.total_lbl.pack(side="right", padx=20)
        
        actions_frame = ctk.CTkFrame(self.bottom_frame, fg_color="transparent")
        actions_frame.pack(side="left", padx=10, fill="x", expand=True)

        btn_finalize = ctk.CTkButton(actions_frame, text="[F2] Finalizar Venda", height=45, font=("Roboto", 16, "bold"), fg_color="#27ae60", hover_color="#2ecc71", command=self.finalize_sale)
        btn_finalize.pack(side="left", padx=5)

        btn_discount = ctk.CTkButton(actions_frame, text="[F3] Desconto Item", height=45, font=("Roboto", 16, "bold"), fg_color="#2980b9", hover_color="#3498db", command=self.apply_item_discount)
        btn_discount.pack(side="left", padx=5)

        btn_remove = ctk.CTkButton(actions_frame, text="[DEL] Remover Item", height=45, font=("Roboto", 16, "bold"), fg_color="#c0392b", hover_color="#e74c3c", command=self.remove_selected_item)
        btn_remove.pack(side="left", padx=5)

        btn_cancel = ctk.CTkButton(actions_frame, text="[ESC] Cancelar Venda", height=45, font=("Roboto", 16, "bold"), fg_color="#7f8c8d", hover_color="#95a5a6", command=self.clear_sale)
        btn_cancel.pack(side="left", padx=5)
        
>>>>>>> b8696156ad077242d2bbfc43a202beb2b9ea5c18
    def bind_shortcuts(self):
        self.app_window.bind("<F2>", self.finalize_sale)
        self.app_window.bind("<F3>", self.apply_item_discount)
        self.app_window.bind("<Escape>", self.clear_sale)
        self.app_window.bind("<Delete>", self.remove_selected_item)
        self.app_window.bind("<Up>", self.move_selection_up)
        self.app_window.bind("<Down>", self.move_selection_down)
<<<<<<< HEAD

=======
        
>>>>>>> b8696156ad077242d2bbfc43a202beb2b9ea5c18
    def unbind_shortcuts(self):
        self.app_window.unbind("<F2>")
        self.app_window.unbind("<F3>")
        self.app_window.unbind("<Escape>")
        self.app_window.unbind("<Delete>")
        self.app_window.unbind("<Up>")
        self.app_window.unbind("<Down>")
<<<<<<< HEAD

=======
        
>>>>>>> b8696156ad077242d2bbfc43a202beb2b9ea5c18
    def destroy(self):
        self.unbind_shortcuts()
        self.scanner.keep_focus_active = False
        super().destroy()

    def add_product_from_scanner(self, code):
        qtd = 1.0
<<<<<<< HEAD
=======
        # Suporte simples a multiplicadores: "2*codigo"
>>>>>>> b8696156ad077242d2bbfc43a202beb2b9ea5c18
        if "*" in code:
            parts = code.split("*", 1)
            try:
                qtd = float(parts[0])
                code = parts[1]
            except ValueError:
                pass
        prod = search_by_barcode(code)
        if not prod:
            prod = get_by_sku(code)
        if prod:
            self.add_to_cart(prod, qtd)
        else:
            messagebox.showwarning("Não Encontrado", f"Produto '{code}' não localizado.")
            if hasattr(self.scanner, 'entry'):
                self.scanner.entry.focus_set()
<<<<<<< HEAD

=======
            
>>>>>>> b8696156ad077242d2bbfc43a202beb2b9ea5c18
    def add_to_cart(self, prod, qtd):
        target_idx = None
        for idx, item in enumerate(self.cart):
            if item['product'].id == prod.id:
                item['quantidade'] += qtd
                target_idx = idx
                break
<<<<<<< HEAD

        if target_idx is None:
            self.cart.append({'product': prod, 'quantidade': qtd, 'preco_unitario': prod.preco_venda, 'desconto_item': 0.0})
            target_idx = len(self.cart) - 1

        self.refresh_table(highlight_idx=target_idx)

=======
                
        if target_idx is None:
            self.cart.append({'product': prod, 'quantidade': qtd, 'preco_unitario': prod.preco_venda, 'desconto_item': 0.0})
            target_idx = len(self.cart) - 1
            
        self.refresh_table(highlight_idx=target_idx)
        
>>>>>>> b8696156ad077242d2bbfc43a202beb2b9ea5c18
    def apply_item_discount(self, event=None):
        selected = self.table.selection()
        if not selected: return
        idx = int(selected[0])
        if 0 <= idx < len(self.cart):
            item = self.cart[idx]
            item_total = item['quantidade'] * item['preco_unitario']
<<<<<<< HEAD

            self.scanner.keep_focus_active = False
            dialog = DiscountModal(self, item_total_price=item_total, current_discount=item.get('desconto_item', 0.0))
            discount_value = dialog.get_input()
            self.scanner.keep_focus_active = True
=======
            
            self.scanner.keep_focus_active = False  # Pausa a busca de foco
            dialog = DiscountModal(self, item_total_price=item_total, current_discount=item.get('desconto_item', 0.0))
            discount_value = dialog.get_input()
            self.scanner.keep_focus_active = True   # Retoma a busca de foco
>>>>>>> b8696156ad077242d2bbfc43a202beb2b9ea5c18
            self.scanner._focus_entry()

            if discount_value is not None:
                if discount_value > item_total:
                    messagebox.showwarning("Desconto Inválido", "O desconto não pode ser maior que o valor total do item.")
                    discount_value = item_total
                self.cart[idx]['desconto_item'] = max(0.0, discount_value)
                self.refresh_table(highlight_idx=idx)

    def refresh_table(self, highlight_idx=None):
        for item in self.table.get_children():
            self.table.delete(item)
        total = 0.0
        for idx, item in enumerate(self.cart):
            subtotal = (item['quantidade'] * item['preco_unitario']) - item.get('desconto_item', 0.0)
            total += subtotal
<<<<<<< HEAD

            tags = ()
            if idx == highlight_idx:
                tags = ("last_added",)

            self.table.insert("", "end", iid=str(idx), values=(
                item['product'].nome,
                f"{item['quantidade']:.3f}".rstrip('0').rstrip('.'),
                f"R$ {item['preco_unitario']:.2f}",
                f"R$ {item.get('desconto_item', 0.0):.2f}",
                f"R$ {subtotal:.2f}"
            ), tags=tags)

=======
            
            tags = ()
            if idx == highlight_idx:
                tags = ("last_added",)
                
            self.table.insert("", "end", iid=str(idx), values=(
                item['product'].nome, 
                f"{item['quantidade']:.3f}".rstrip('0').rstrip('.'), 
                f"R$ {item['preco_unitario']:.2f}", 
                f"R$ {item.get('desconto_item', 0.0):.2f}",
                f"R$ {subtotal:.2f}"
            ), tags=tags)
            
>>>>>>> b8696156ad077242d2bbfc43a202beb2b9ea5c18
        children = self.table.get_children()
        if children:
            if highlight_idx is not None and highlight_idx < len(children):
                self.table.see(children[highlight_idx])
            else:
                self.table.selection_set(children[-1])
                self.table.see(children[-1])
<<<<<<< HEAD

        self.total_lbl.configure(text=f"TOTAL: R$ {total:.2f}")

        if highlight_idx is not None:
            self.after(1500, lambda: self.remove_highlight(str(highlight_idx)))

    def remove_highlight(self, iid):
        if iid in self.table.get_children():
            self.table.item(iid, tags=())

=======
                
        self.total_lbl.configure(text=f"TOTAL: R$ {total:.2f}")
        
        if highlight_idx is not None:
            self.after(1500, lambda: self.remove_highlight(str(highlight_idx)))
            
    def remove_highlight(self, iid):
        if iid in self.table.get_children():
            self.table.item(iid, tags=())
            
>>>>>>> b8696156ad077242d2bbfc43a202beb2b9ea5c18
    def remove_selected_item(self, event=None):
        selected = self.table.selection()
        if not selected: return
        idx = int(selected[0])
        if 0 <= idx < len(self.cart):
            del self.cart[idx]
            self.refresh_table()
<<<<<<< HEAD

=======
            
>>>>>>> b8696156ad077242d2bbfc43a202beb2b9ea5c18
    def move_selection_up(self, event=None):
        self._move_selection(-1)

    def move_selection_down(self, event=None):
        self._move_selection(1)

    def _move_selection(self, delta):
        children = self.table.get_children()
        if not children: return
        selected = self.table.selection()
        if not selected:
            idx = 0 if delta > 0 else len(children) - 1
        else:
            idx = children.index(selected[0]) + delta
            idx = max(0, min(idx, len(children) - 1))
        self.table.selection_set(children[idx])
        self.table.see(children[idx])
<<<<<<< HEAD

    def finalize_sale(self, event=None):
        if not self.cart: return
        if getattr(self, "modal_open", False): return

        self.modal_open = True
        self.scanner.keep_focus_active = False

        def on_success():
            self.clear_sale()

        total = sum((i['quantidade'] * i['preco_unitario']) - i.get('desconto_item', 0.0) for i in self.cart)
        modal = PaymentModal(self.winfo_toplevel(), self.cart, total, on_success)

        original_destroy = modal.destroy
        def custom_destroy():
            self.modal_open = False
            self.scanner.keep_focus_active = True
            self.scanner._focus_entry()
            original_destroy()
        modal.destroy = custom_destroy

    def clear_sale(self, event=None):
        self.cart = []
        self.refresh_table()
=======
        
    def finalize_sale(self, event=None):
        if not self.cart: return
        if getattr(self, "modal_open", False): return
        
        self.modal_open = True
        self.scanner.keep_focus_active = False  # Pausa a busca de foco
        
        def on_success():
            self.clear_sale()
            
        total = sum((i['quantidade'] * i['preco_unitario']) - i.get('desconto_item', 0.0) for i in self.cart)
        modal = PaymentModal(self.winfo_toplevel(), self.cart, total, on_success)
        
        original_destroy = modal.destroy
        def custom_destroy():
            self.modal_open = False
            self.scanner.keep_focus_active = True  # Retoma a busca de foco
            self.scanner._focus_entry()
            original_destroy()
        modal.destroy = custom_destroy
            
    def clear_sale(self, event=None):
        self.cart = []
        self.refresh_table()
>>>>>>> b8696156ad077242d2bbfc43a202beb2b9ea5c18
