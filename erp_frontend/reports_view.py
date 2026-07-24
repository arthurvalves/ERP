import customtkinter as ctk
from tkinter import messagebox
from erp_frontend.components.table import TableComponent
from erp_backend.services import reports_service, product_service
from datetime import datetime, timedelta
from erp_frontend import theme

class ReportsView(ctk.CTkFrame):
    def __init__(self, master, app_window, **kwargs):
        super().__init__(master, fg_color=theme.BG, **kwargs)
        self.app_window = app_window
        self.setup_ui()
        self.load_productivity_report()

    def setup_ui(self):
        self.tab_view = ctk.CTkTabview(self, fg_color=theme.CARD_ALT,
                                        segmented_button_selected_color=theme.PRIMARY,
                                        segmented_button_selected_hover_color=theme.PRIMARY_HOVER,
                                        segmented_button_unselected_color=theme.CARD,
                                        text_color=theme.TEXT)
        self.tab_view.pack(fill="both", expand=True, padx=10, pady=10)

        self.tab_productivity = self.tab_view.add("Produtividade por Técnico")
        self.tab_suggestions = self.tab_view.add("Sugestão de Compras")
        self.tab_sales = self.tab_view.add("Vendas por Período")

        self.setup_productivity_tab()
        self.setup_suggestions_tab()
        self.setup_sales_tab()

    def setup_productivity_tab(self):
        tab = self.tab_productivity
        top_frame = ctk.CTkFrame(tab, fg_color="transparent")
        top_frame.pack(fill="x", padx=10, pady=10)

        ctk.CTkLabel(top_frame, text="Relatório de Produtividade por Técnico", font=theme.font_heading(20), text_color=theme.TEXT).pack(side="left")
        date_frame = ctk.CTkFrame(top_frame, fg_color="transparent")
        date_frame.pack(side="right")

        today = datetime.today()
        start_of_month = today.replace(day=1)

        ctk.CTkLabel(date_frame, text="De:", font=theme.font_body(12), text_color=theme.TEXT_MUTED).pack(side="left", padx=(10, 5))
        self.prod_start_date = ctk.CTkEntry(date_frame, width=100, font=theme.font_body(12), fg_color=theme.CARD, border_color=theme.SECONDARY)
        self.prod_start_date.insert(0, start_of_month.strftime('%d/%m/%Y'))
        self.prod_start_date.pack(side="left")

        ctk.CTkLabel(date_frame, text="Até:", font=theme.font_body(12), text_color=theme.TEXT_MUTED).pack(side="left", padx=(10, 5))
        self.prod_end_date = ctk.CTkEntry(date_frame, width=100, font=theme.font_body(12), fg_color=theme.CARD, border_color=theme.SECONDARY)
        self.prod_end_date.insert(0, today.strftime('%d/%m/%Y'))
        self.prod_end_date.pack(side="left")

        btn_generate = ctk.CTkButton(date_frame, text="GERAR", command=self.load_productivity_report, **theme.btn_primary())
        btn_generate.pack(side="left", padx=10)

        columns = ("TÉCNICO / MECÂNICO", "SERVIÇOS/ITENS REALIZADOS", "VALOR TOTAL GERADO")
        self.productivity_table = TableComponent(tab, columns)
        self.productivity_table.column("TÉCNICO / MECÂNICO", width=300, anchor="w")
        self.productivity_table.column("SERVIÇOS/ITENS REALIZADOS", width=250, anchor="c")
        self.productivity_table.column("VALOR TOTAL GERADO", width=250, anchor="e")
        self.productivity_table.pack(fill="both", expand=True, padx=10, pady=10)

    def setup_suggestions_tab(self):
        tab = self.tab_suggestions
        top_frame = ctk.CTkFrame(tab, fg_color="transparent")
        top_frame.pack(fill="x", padx=10, pady=10)

        ctk.CTkLabel(top_frame, text="Lista de Produtos com Estoque Baixo", font=theme.font_heading(20), text_color=theme.TEXT).pack(side="left")
        btn_refresh = ctk.CTkButton(top_frame, text="ATUALIZAR LISTA", command=self.load_suggestions_report, **theme.btn_primary())
        btn_refresh.pack(side="right")

        columns = ("PRODUTO", "SKU", "ESTOQUE ATUAL", "ESTOQUE MÍNIMO", "SUGESTÃO DE COMPRA")
        self.suggestions_table = TableComponent(tab, columns)
        self.suggestions_table.column("PRODUTO", width=400, anchor="w")
        self.suggestions_table.column("SKU", width=150)
        self.suggestions_table.column("ESTOQUE ATUAL", width=150, anchor="c")
        self.suggestions_table.column("ESTOQUE MÍNIMO", width=150, anchor="c")
        self.suggestions_table.column("SUGESTÃO DE COMPRA", width=200, anchor="c")
        self.suggestions_table.pack(fill="both", expand=True, padx=10, pady=10)
        self.suggestions_table.tag_configure("critical", foreground=theme.DANGER)

        self.load_suggestions_report()

    def setup_sales_tab(self):
        tab = self.tab_sales
        top_frame = ctk.CTkFrame(tab, fg_color="transparent")
        top_frame.pack(fill="x", padx=10, pady=10)

        ctk.CTkLabel(top_frame, text="Relatório de Vendas por Período", font=theme.font_heading(20), text_color=theme.TEXT).pack(side="left")

        date_frame = ctk.CTkFrame(top_frame, fg_color="transparent")
        date_frame.pack(side="right")

        today = datetime.today()
        start_of_month = today.replace(day=1)

        ctk.CTkLabel(date_frame, text="De:", font=theme.font_body(12), text_color=theme.TEXT_MUTED).pack(side="left", padx=(10, 5))
        self.sales_start_date = ctk.CTkEntry(date_frame, width=100, font=theme.font_body(12), fg_color=theme.CARD, border_color=theme.SECONDARY)
        self.sales_start_date.insert(0, start_of_month.strftime('%d/%m/%Y'))
        self.sales_start_date.pack(side="left")

        ctk.CTkLabel(date_frame, text="Até:", font=theme.font_body(12), text_color=theme.TEXT_MUTED).pack(side="left", padx=(10, 5))
        self.sales_end_date = ctk.CTkEntry(date_frame, width=100, font=theme.font_body(12), fg_color=theme.CARD, border_color=theme.SECONDARY)
        self.sales_end_date.insert(0, today.strftime('%d/%m/%Y'))
        self.sales_end_date.pack(side="left")

        btn_generate = ctk.CTkButton(date_frame, text="GERAR", command=self.load_sales_report, **theme.btn_primary())
        btn_generate.pack(side="left", padx=10)

        columns = ("FORMA DE PAGAMENTO", "Nº DE VENDAS", "VALOR TOTAL")
        self.sales_table = TableComponent(tab, columns)
        self.sales_table.column("FORMA DE PAGAMENTO", width=300, anchor="w")
        self.sales_table.column("Nº DE VENDAS", width=200, anchor="c")
        self.sales_table.column("VALOR TOTAL", width=200, anchor="e")
        self.sales_table.pack(fill="both", expand=True, padx=10, pady=10)

        self.load_sales_report()

    def load_productivity_report(self):
        try:
            start_date_str = self.prod_start_date.get()
            end_date_str = self.prod_end_date.get()
            start_date = datetime.strptime(start_date_str, '%d/%m/%Y')
            end_date = datetime.strptime(end_date_str, '%d/%m/%Y')
        except ValueError:
            messagebox.showerror("Erro de Formato", "Por favor, insira as datas no formato DD/MM/AAAA.")
            return

        for item in self.productivity_table.get_children():
            self.productivity_table.delete(item)

        report_data = reports_service.get_technician_productivity(start_date, end_date)

        total_geral = 0.0
        for row in report_data:
            total_geral += row['total_value']
            self.productivity_table.insert("", "end", values=(
                row['technician_name'].upper(),
                row['total_items'],
                f"R$ {row['total_value']:.2f}"
            ))

        self.productivity_table.insert("", "end", values=("---", "---", "---"))
        self.productivity_table.insert("", "end", values=("TOTAL GERAL", "", f"R$ {total_geral:.2f}"), tags=("total",))
        self.productivity_table.tag_configure("total", font=theme.font_bold(14), foreground=theme.PRIMARY)

    def load_suggestions_report(self):
        for item in self.suggestions_table.get_children():
            self.suggestions_table.delete(item)

        suggestions = product_service.get_purchase_suggestions()

        for row in suggestions:
            suggestion_qty = (row['estoque_minimo'] or 0) - (row['estoque_atual'] or 0)
            suggestion_qty = max(0, suggestion_qty)
            self.suggestions_table.insert("", "end", values=(
                row['nome'],
                row['sku'],
                f"{row['estoque_atual'] or 0:.2f}",
                f"{row['estoque_minimo'] or 0:.2f}",
                f"{suggestion_qty:.2f} unidades"
            ), tags=("critical",))

    def load_sales_report(self):
        try:
            start_date_str = self.sales_start_date.get()
            end_date_str = self.sales_end_date.get()
            start_date = datetime.strptime(start_date_str, '%d/%m/%Y')
            end_date = datetime.strptime(end_date_str, '%d/%m/%Y')
        except ValueError:
            messagebox.showerror("Erro de Formato", "Por favor, insira as datas no formato DD/MM/AAAA.")
            return

        for item in self.sales_table.get_children():
            self.sales_table.delete(item)

        report_data = reports_service.get_sales_by_period(start_date, end_date)

        total_geral = 0.0
        for row in report_data:
            total_geral += row['total_value']
            self.sales_table.insert("", "end", values=(
                row['forma_pagamento'].upper(),
                row['total_sales'],
                f"R$ {row['total_value']:.2f}"
            ))

        self.sales_table.insert("", "end", values=("---", "---", "---"))
        self.sales_table.insert("", "end", values=("TOTAL GERAL", "", f"R$ {total_geral:.2f}"), tags=("total",))
        self.sales_table.tag_configure("total", font=theme.font_bold(14), foreground=theme.PRIMARY)
