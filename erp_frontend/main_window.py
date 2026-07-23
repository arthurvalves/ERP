import customtkinter as ctk
from tkinter import ttk
from erp_frontend.dashboard_view import DashboardView
from erp_frontend.pdv_view import PDVView
from erp_frontend.nfe_view import NFeView
from erp_frontend.products_view import ProductsView
from erp_frontend.customers_view import CustomersView
from erp_frontend.services_view import ServicesView
from erp_frontend.printer_view import PrinterView
from erp_frontend.os_view import OSView
from erp_frontend.quotes_view import QuotesView
from erp_frontend.history_view import HistoryView
from erp_frontend.accounts_receivable_view import AccountsReceivableView
from erp_frontend.schedule_view import ScheduleView
from erp_frontend.maintenance_alerts_view import MaintenanceAlertsView
from erp_frontend.reports_view import ReportsView
from erp_frontend.session import get_current_user

ctk.set_appearance_mode("dark")
ctk.set_default_color_theme("blue")

class MainWindow(ctk.CTk):
    def __init__(self):
        super().__init__()
        self.title("miniERP - Frente de Caixa")
        # self.geometry("1920x1080") # Substituído pela opção de tela cheia real
        self.current_user = get_current_user()
        self.current_view = None

        self.setup_styles()
        self.setup_main_ui()
        self.show_view(DashboardView)

    def setup_styles(self):
        """Centraliza a configuração de todos os estilos de tabela (ttk.Treeview)."""
        style = ttk.Style()
        
        # Estilo para a tabela de Clientes (fonte 18)
        style.configure("Customers.Treeview", rowheight=80, font=("Roboto", 30), background="#1e1e1e", foreground="#ffffff")
        style.configure("Customers.Treeview.Heading", font=("Roboto", 28, "bold"))

        # Estilo padrão para outras tabelas (fonte 14)
        style.configure("Products.Treeview", rowheight=40, font=("Roboto", 14), background="#1e1e1e", foreground="#ffffff")
        style.configure("Products.Treeview.Heading", font=("Roboto", 14, "bold"))

        # Adiciona outros estilos de tabela aqui se necessário no futuro...


    def _create_nav_menu(self, text, options):
        """Cria um menu suspenso na barra de navegação."""
        # O truque é que o comando do menu chama a função show_view com a tela correspondente.
        menu_values = list(options.keys())

        def menu_callback(choice):
            if choice in options:
                self.show_view(options[choice])

        # Usamos um CTkButton que se parece com o menu, e um CTkOptionMenu sem texto visível ao lado.
        menu = ctk.CTkOptionMenu(
            self.nav_frame,
            values=menu_values,
            command=menu_callback,
            font=("Roboto", 14),
            width=140,
            height=35,
            dropdown_font=("Roboto", 14),
            fg_color="#343638",
            button_color="#343638",
            button_hover_color="#3f4143"
        )
        menu.set(text) # Define o texto inicial do botão
        menu.pack(side="left", padx=5, pady=10)

    def setup_main_ui(self):
        self.nav_frame = ctk.CTkFrame(self, height=60, corner_radius=0)
        self.nav_frame.pack(side="top", fill="x")
        
        self.logo = ctk.CTkLabel(self.nav_frame, text="ERP", font=("Roboto", 24, "bold"), text_color="#2ecc71")
        self.logo.pack(side="left", padx=20)

        # Botão principal do Dashboard
        ctk.CTkButton(self.nav_frame, text="[DASHBOARD]", command=lambda: self.show_view(DashboardView)).pack(side="left", padx=5)

        # Menus Suspensos
        self._create_nav_menu("Cadastros", {"Produtos": ProductsView, "Clientes": CustomersView, "Serviços": ServicesView})
        self._create_nav_menu("Operacional", {"PDV": PDVView, "Orçamentos": QuotesView, "Ordens de Serviço": OSView, "Agenda": ScheduleView})
        self._create_nav_menu("Análise", {"Histórico de Veículos": HistoryView, "Alertas de Manutenção": MaintenanceAlertsView, "Relatórios": ReportsView})
        self._create_nav_menu("Financeiro", {"Contas a Receber": AccountsReceivableView})
        self._create_nav_menu("Administrativo", {"Importar NF-e": NFeView, "Impressoras": PrinterView})
        
        self.content_frame = ctk.CTkFrame(self, corner_radius=0, fg_color="#1e1e1e")
        self.content_frame.pack(side="top", fill="both", expand=True)
        
    def show_view(self, view_class):
        if self.current_view:
            self.current_view.destroy()
        self.current_view = view_class(self.content_frame, self)
        self.current_view.pack(fill="both", expand=True)

if __name__ == "__main__":
    app = MainWindow()
    # Tries to maximize on Windows
    try:
        app.state('zoomed')
    except:
        pass
    app.mainloop()