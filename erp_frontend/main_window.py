import customtkinter as ctk
from tkinter import ttk, Menu
import datetime

from erp_frontend import theme
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
        self.configure(fg_color=theme.BG)
        self.current_user = get_current_user()
        self.current_view = None
        self.active_screen = None

        self.setup_styles()
        self.setup_main_ui()
        self.show_view(DashboardView, screen_key="dashboard")

    # ------------------------------------------------------------------ #
    # Estilos globais de tabela (mantidos centralizados aqui)
    # ------------------------------------------------------------------ #
    def setup_styles(self):
        style = ttk.Style()

        style.configure(
            "Customers.Treeview",
            rowheight=64,
            font=(theme.FONT_FAMILY, 16),
            background=theme.CARD_ALT,
            foreground=theme.TEXT,
            fieldbackground=theme.CARD_ALT,
        )
        style.configure("Customers.Treeview.Heading", font=(theme.FONT_FAMILY, 14, "bold"),
                         background=theme.CARD, foreground=theme.TEXT)

        style.configure(
            "Products.Treeview",
            rowheight=38,
            font=(theme.FONT_FAMILY, 13),
            background=theme.CARD_ALT,
            foreground=theme.TEXT,
            fieldbackground=theme.CARD_ALT,
        )
        style.configure("Products.Treeview.Heading", font=(theme.FONT_FAMILY, 13, "bold"),
                         background=theme.CARD, foreground=theme.TEXT)

        style.configure(
            "PDV.Treeview",
            rowheight=55,
            font=(theme.FONT_FAMILY, 18, "bold"),
            background=theme.BG,
            foreground=theme.TEXT,
            fieldbackground=theme.BG,
        )
        style.configure("PDV.Treeview.Heading", font=(theme.FONT_FAMILY, 16, "bold"),
                         background=theme.CARD, foreground=theme.TEXT_MUTED)

        style.map(
            "Treeview",
            background=[("selected", theme.PRIMARY)],
            foreground=[("selected", theme.PRIMARY_FOREGROUND)],
        )

    # ------------------------------------------------------------------ #
    # Layout principal: sidebar (esquerda) + top bar + conteúdo
    # ------------------------------------------------------------------ #
    def setup_main_ui(self):
        root = ctk.CTkFrame(self, fg_color=theme.BG)
        root.pack(fill="both", expand=True)

        self._build_sidebar(root)

        right = ctk.CTkFrame(root, fg_color=theme.BG)
        right.pack(side="left", fill="both", expand=True)

        self._build_top_bar(right)

        self.content_frame = ctk.CTkFrame(right, corner_radius=0, fg_color=theme.BG)
        self.content_frame.pack(side="top", fill="both", expand=True)

    def _build_sidebar(self, parent):
        sidebar = ctk.CTkFrame(
            parent, width=110, fg_color=theme.SIDEBAR_BG, corner_radius=0,
            border_width=0,
        )
        sidebar.pack(side="left", fill="y")
        sidebar.pack_propagate(False)

        # "Logo" - bloco preenchido com a cor primária
        logo_wrap = ctk.CTkFrame(sidebar, fg_color=theme.SIDEBAR_BG, corner_radius=0)
        logo_wrap.pack(fill="x", padx=12, pady=(16, 8))
        logo = ctk.CTkLabel(
            logo_wrap, text="ERP", fg_color=theme.PRIMARY, text_color=theme.PRIMARY_FOREGROUND,
            font=theme.font_title(20), corner_radius=theme.RADIUS, height=56,
        )
        logo.pack(fill="x")

        self._nav_buttons = {}
        menu_items = [
            ("pdv", "🛒", "PDV", lambda: self.show_view(PDVView, "pdv")),
            ("nfe", "📄", "NF-e", lambda: self.show_view(NFeView, "nfe")),
            ("dashboard", "📊", "Dashboard", lambda: self.show_view(DashboardView, "dashboard")),
            ("products", "📦", "Produtos", lambda: self.show_view(ProductsView, "products")),
            ("operational", "🔧", "Operacional", lambda: self.show_view(OSView, "operational")),
            ("support", "🎧", "Suporte", lambda: self.show_view(HistoryView, "support")),
        ]

        items_wrap = ctk.CTkFrame(sidebar, fg_color=theme.SIDEBAR_BG)
        items_wrap.pack(fill="both", expand=True, padx=10, pady=8)

        for key, icon, label, command in menu_items:
            btn = ctk.CTkButton(
                items_wrap,
                text=f"{icon}\n{label.upper()}",
                command=command,
                fg_color=theme.CARD,
                hover_color=theme.SECONDARY,
                text_color=theme.TEXT_MUTED,
                border_width=2,
                border_color=theme.SECONDARY,
                font=(theme.FONT_FAMILY, 11, "bold"),
                corner_radius=theme.RADIUS,
                height=70,
            )
            btn.pack(fill="x", pady=6)
            self._nav_buttons[key] = btn

        logout_wrap = ctk.CTkFrame(sidebar, fg_color=theme.SIDEBAR_BG)
        logout_wrap.pack(fill="x", padx=10, pady=(0, 16))
        ctk.CTkButton(
            logout_wrap, text="⏻\nSAIR", height=56,
            **theme.btn_danger(font=(theme.FONT_FAMILY, 11, "bold")),
            command=self._logout,
        ).pack(fill="x")

    def _set_active_nav(self, screen_key):
        for key, btn in self._nav_buttons.items():
            if key == screen_key:
                btn.configure(fg_color=theme.PRIMARY, text_color=theme.PRIMARY_FOREGROUND,
                              border_color=theme.PRIMARY)
            else:
                btn.configure(fg_color=theme.CARD, text_color=theme.TEXT_MUTED,
                              border_color=theme.SECONDARY)

    def _logout(self):
        from erp_frontend.session import clear_session
        clear_session()
        self.destroy()

    def _build_top_bar(self, parent):
        bar = ctk.CTkFrame(parent, fg_color=theme.SECONDARY, corner_radius=0, height=56,
                            border_width=0)
        bar.pack(side="top", fill="x")

        left = ctk.CTkFrame(bar, fg_color="transparent")
        left.pack(side="left", padx=16, pady=8)

        self._create_dropdown(left, "Cadastros", {
            "Produtos": lambda: self.show_view(ProductsView, "products"),
            "Clientes": lambda: self.show_view(CustomersView, "products"),
            "Serviços": lambda: self.show_view(ServicesView, "products"),
        })
        self._create_dropdown(left, "Operacional", {
            "Ordens de Serviço": lambda: self.show_view(OSView, "operational"),
            "Orçamentos": lambda: self.show_view(QuotesView, "operational"),
            "Agenda": lambda: self.show_view(ScheduleView, "operational"),
        })
        self._create_dropdown(left, "Análise", {
            "Histórico de Veículos": lambda: self.show_view(HistoryView, "support"),
            "Alertas de Manutenção": lambda: self.show_view(MaintenanceAlertsView, "support"),
            "Relatórios": lambda: self.show_view(ReportsView, "support"),
        })
        self._create_dropdown(left, "Financeiro", {
            "Contas a Receber": lambda: self.show_view(AccountsReceivableView, "support"),
        })
        self._create_dropdown(left, "Administrativo", {
            "Importar NF-e": lambda: self.show_view(NFeView, "nfe"),
            "Impressoras": lambda: self.show_view(PrinterView, "support"),
        })

        right = ctk.CTkFrame(bar, fg_color="transparent")
        right.pack(side="right", padx=16, pady=6)

        user_name = (self.current_user or {}).get("username", "Operador") if self.current_user else "Operador"
        user_box = ctk.CTkFrame(right, fg_color="transparent")
        user_box.pack(side="right", padx=(16, 0))
        ctk.CTkLabel(user_box, text="OPERADOR", font=(theme.FONT_FAMILY, 10, "bold"),
                     text_color=theme.TEXT_MUTED).pack(anchor="e")
        ctk.CTkLabel(user_box, text=user_name, font=theme.font_bold(13),
                     text_color=theme.TEXT).pack(anchor="e")

        clock_box = ctk.CTkFrame(right, fg_color="transparent")
        clock_box.pack(side="right", padx=16)
        self._clock_label = ctk.CTkLabel(clock_box, text="--:--:--", font=theme.font_mono(16),
                                          text_color=theme.PRIMARY)
        self._clock_label.pack(anchor="e")
        ctk.CTkLabel(clock_box, text="HORÁRIO LOCAL", font=(theme.FONT_FAMILY, 10, "bold"),
                     text_color=theme.TEXT_MUTED).pack(anchor="e")
        self._tick_clock()

    def _tick_clock(self):
        now = datetime.datetime.now().strftime("%H:%M:%S")
        if hasattr(self, "_clock_label") and self._clock_label.winfo_exists():
            self._clock_label.configure(text=now)
        self.after(1000, self._tick_clock)

    def _create_dropdown(self, parent, label, options: dict):
        menu = Menu(self, tearoff=0, bg=theme.CARD, fg=theme.TEXT,
                    activebackground=theme.PRIMARY, activeforeground=theme.PRIMARY_FOREGROUND,
                    font=(theme.FONT_FAMILY, 11, "bold"), bd=0)
        for item_label, command in options.items():
            menu.add_command(label=item_label, command=command)

        def open_menu():
            x = btn.winfo_rootx()
            y = btn.winfo_rooty() + btn.winfo_height()
            menu.tk_popup(x, y)

        btn = ctk.CTkButton(
            parent, text=f"{label} ▾", command=open_menu,
            fg_color="transparent", hover_color=theme.CARD,
            text_color=theme.TEXT_MUTED, font=(theme.FONT_FAMILY, 12, "bold"),
            corner_radius=theme.RADIUS, height=32,
        )
        btn.pack(side="left", padx=8)
        return btn

    def show_view(self, view_class, screen_key=None):
        if self.current_view:
            self.current_view.destroy()
        self.current_view = view_class(self.content_frame, self)
        self.current_view.pack(fill="both", expand=True)
        if screen_key:
            self.active_screen = screen_key
            self._set_active_nav(screen_key)


if __name__ == "__main__":
    app = MainWindow()
    try:
        app.state('zoomed')
    except Exception:
        pass
    app.mainloop()
