import customtkinter as ctk
from tkinter import messagebox, ttk, Menu
from erp_frontend.components.table import TableComponent
from erp_backend.services import customer_service
from erp_frontend.customer_modal import CustomerModal
from erp_frontend.modals.customer_vehicle_modal import CustomerVehiclesModal
<<<<<<< HEAD
from erp_frontend import theme

class CustomersView(ctk.CTkFrame):
    def __init__(self, master, app_window, **kwargs):
        super().__init__(master, fg_color=theme.BG, **kwargs)
=======

class CustomersView(ctk.CTkFrame):
    def __init__(self, master, app_window, **kwargs):
        super().__init__(master, fg_color="#1e1e1e", **kwargs)
>>>>>>> b8696156ad077242d2bbfc43a202beb2b9ea5c18
        self.app_window = app_window
        self.setup_ui()
        self.load_data()
        self.bind_shortcuts()

    def setup_ui(self):
        top_frame = ctk.CTkFrame(self, fg_color="transparent")
        top_frame.pack(fill="x", padx=20, pady=10)

<<<<<<< HEAD
        self.search_entry = ctk.CTkEntry(top_frame, placeholder_text="🔎 BUSCA: NOME / CPF / CNPJ...", height=40,
                                          font=theme.font_body(16), fg_color=theme.CARD, border_color=theme.SECONDARY)
=======
        self.search_entry = ctk.CTkEntry(top_frame, placeholder_text="🔎 BUSCA: NOME / CPF / CNPJ...", height=40, font=("Roboto", 16))
>>>>>>> b8696156ad077242d2bbfc43a202beb2b9ea5c18
        self.search_entry.pack(side="left", fill="x", expand=True, padx=(0, 20))
        self.search_entry.bind("<KeyRelease>", lambda e: self.load_data())

        actions_frame = ctk.CTkFrame(self, fg_color="transparent")
        actions_frame.pack(fill="x", padx=20, pady=(0, 10))

<<<<<<< HEAD
        btn_new = ctk.CTkButton(actions_frame, text="[ NOVO CLIENTE ]", command=self.new_customer, **theme.btn_primary())
        btn_new.pack(side="left", padx=5)

        btn_edit = ctk.CTkButton(actions_frame, text="[F2] EDITAR", command=self.edit_selected, **theme.btn_secondary())
        btn_edit.pack(side="left", padx=5)

        btn_vehicles = ctk.CTkButton(actions_frame, text="[ VER VEÍCULOS ]", command=self.view_customer_vehicles,
                                      **theme.btn_secondary(fg_color=theme.INFO, hover_color="#2563eb", text_color="#ffffff"))
        btn_vehicles.pack(side="left", padx=5)

        btn_delete = ctk.CTkButton(actions_frame, text="[DEL] DELETAR", command=self.delete_selected, **theme.btn_danger())
        btn_delete.pack(side="left", padx=5)

        btn_refresh = ctk.CTkButton(actions_frame, text="[F5] ATUALIZAR", command=self.load_data,
                                     **theme.btn_secondary(fg_color=theme.INFO, hover_color="#2563eb", text_color="#ffffff"))
        btn_refresh.pack(side="left", padx=5)

=======
        btn_new = ctk.CTkButton(actions_frame, text="[ NOVO CLIENTE ]", font=("Roboto", 14, "bold"), command=self.new_customer)
        btn_new.pack(side="left", padx=5)

        btn_edit = ctk.CTkButton(actions_frame, text="[F2] EDITAR", font=("Roboto", 14, "bold"), fg_color="#f39c12", hover_color="#d68910", command=self.edit_selected)
        btn_edit.pack(side="left", padx=5)

        btn_vehicles = ctk.CTkButton(actions_frame, text="[ VER VEÍCULOS ]", font=("Roboto", 14, "bold"), fg_color="#2980b9", hover_color="#3498db", command=self.view_customer_vehicles)
        btn_vehicles.pack(side="left", padx=5)

        btn_delete = ctk.CTkButton(actions_frame, text="[DEL] DELETAR", font=("Roboto", 14, "bold"), fg_color="#e74c3c", hover_color="#c0392b", command=self.delete_selected)
        btn_delete.pack(side="left", padx=5)

        btn_refresh = ctk.CTkButton(actions_frame, text="[F5] ATUALIZAR", font=("Roboto", 14, "bold"), fg_color="#3498db", hover_color="#2980b9", command=self.load_data)
        btn_refresh.pack(side="left", padx=5)


>>>>>>> b8696156ad077242d2bbfc43a202beb2b9ea5c18
        columns = ("NOME / RAZÃO SOCIAL", "CPF / CNPJ", "TELEFONE", "EMAIL", "ENDEREÇO")
        self.table = TableComponent(self, columns, style="Customers.Treeview")
        self.table.column("NOME / RAZÃO SOCIAL", width=350, anchor="w")
        self.table.column("CPF / CNPJ", width=180)
        self.table.column("TELEFONE", width=150)
        self.table.column("EMAIL", width=200, anchor="w")
        self.table.column("ENDEREÇO", width=400, anchor="w")
        self.table.pack(fill="both", expand=True, padx=20, pady=10)
        self.table.bind("<Double-1>", lambda e: self.edit_selected())
<<<<<<< HEAD
        self.table.bind("<Button-3>", self._show_context_menu)
=======
        self.table.bind("<Button-3>", self._show_context_menu) # Botão direito
>>>>>>> b8696156ad077242d2bbfc43a202beb2b9ea5c18
        self._create_context_menu()

    def bind_shortcuts(self):
        self.app_window.bind("<F2>", lambda e: self.edit_selected())
        self.app_window.bind("<F5>", lambda e: self.load_data())
        self.app_window.bind("<Delete>", lambda e: self.delete_selected())

    def unbind_shortcuts(self):
        self.app_window.unbind("<F2>")
        self.app_window.unbind("<F5>")
        self.app_window.unbind("<Delete>")

    def destroy(self):
        self.unbind_shortcuts()
        super().destroy()

    def _create_context_menu(self):
<<<<<<< HEAD
        self.context_menu = Menu(self.table, tearoff=0, font=(theme.FONT_FAMILY, 12),
                                  bg=theme.CARD, fg=theme.TEXT, activebackground=theme.PRIMARY,
                                  activeforeground=theme.PRIMARY_FOREGROUND)
=======
        self.context_menu = Menu(self.table, tearoff=0, font=("Roboto", 12))
>>>>>>> b8696156ad077242d2bbfc43a202beb2b9ea5c18
        self.context_menu.add_command(label="Novo Cliente", command=self.new_customer)
        self.context_menu.add_command(label="Editar Cliente Selecionado", command=self.edit_selected)
        self.context_menu.add_separator()
        self.context_menu.add_command(label="Deletar Cliente Selecionado", command=self.delete_selected)

    def _show_context_menu(self, event):
        selection = self.table.selection()
        if selection:
            self.context_menu.entryconfigure("Editar Cliente Selecionado", state="normal")
            self.context_menu.entryconfigure("Deletar Cliente Selecionado", state="normal")
        else:
            self.context_menu.entryconfigure("Editar Cliente Selecionado", state="disabled")
            self.context_menu.entryconfigure("Deletar Cliente Selecionado", state="disabled")
        self.context_menu.post(event.x_root, event.y_root)

    def load_data(self):
        search_term = self.search_entry.get().strip()
        for item in self.table.get_children():
            self.table.delete(item)

        customers = customer_service.search_customers(search_term)
        for customer in customers:
            self.table.insert("", "end", iid=str(customer.id), values=(
                customer.nome_razao_social,
                customer.cpf_cnpj,
                customer.telefone or "--",
                customer.email or "--",
                customer.endereco or "--"
            ))

    def new_customer(self):
        CustomerModal(self, on_save=self.load_data)

    def edit_selected(self):
        selected = self.table.selection()
        if not selected:
            messagebox.showwarning("Aviso", "Selecione um cliente para editar.")
            return
        customer_id = int(selected[0])
        CustomerModal(self, customer_id=customer_id, on_save=self.load_data)

    def view_customer_vehicles(self):
        selected = self.table.selection()
        if not selected:
            messagebox.showwarning("Aviso", "Selecione um cliente para ver os veículos.")
            return
        customer_id = int(selected[0])
        customer_name = self.table.item(selected[0])['values'][0]
        CustomerVehiclesModal(self, customer_id=customer_id, customer_name=customer_name)

    def delete_selected(self):
        selected = self.table.selection()
        if not selected:
            messagebox.showwarning("Aviso", "Selecione um cliente para deletar.")
            return
<<<<<<< HEAD

=======
        
>>>>>>> b8696156ad077242d2bbfc43a202beb2b9ea5c18
        customer_id = int(selected[0])
        customer_name = self.table.item(selected[0])['values'][0]

        if messagebox.askyesno("Confirmar Exclusão", f"Tem certeza que deseja deletar o cliente '{customer_name}'?\n\nEsta ação não pode ser desfeita."):
            try:
                success = customer_service.delete_customer_by_id(customer_id)
                if success:
                    messagebox.showinfo("Sucesso", "Cliente deletado com sucesso.")
                    self.load_data()
            except ValueError as e:
                messagebox.showerror("Erro ao Deletar", str(e))
            except Exception as e:
<<<<<<< HEAD
                messagebox.showerror("Erro Crítico", f"Ocorreu um erro inesperado: {e}")
=======
                messagebox.showerror("Erro Crítico", f"Ocorreu um erro inesperado: {e}")
>>>>>>> b8696156ad077242d2bbfc43a202beb2b9ea5c18
