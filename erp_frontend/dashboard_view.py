import customtkinter as ctk
import sqlite3

from erp_backend.utils.db import get_connection
<<<<<<< HEAD
from erp_frontend import theme
=======
>>>>>>> b8696156ad077242d2bbfc43a202beb2b9ea5c18


class DashboardView(ctk.CTkFrame):
    def __init__(self, master, app_window, **kwargs):
<<<<<<< HEAD
        super().__init__(master, fg_color=theme.BG, **kwargs)
=======
        super().__init__(master, fg_color="#1e1e1e", **kwargs)
>>>>>>> b8696156ad077242d2bbfc43a202beb2b9ea5c18
        self.app_window = app_window
        self.setup_ui()
        self.refresh()

    def setup_ui(self):
        header = ctk.CTkFrame(self, fg_color="transparent")
<<<<<<< HEAD
        header.pack(fill="x", padx=32, pady=(32, 8))

        title = ctk.CTkLabel(
            header, text="DASHBOARD", font=theme.font_title(32), text_color=theme.PRIMARY,
        )
        title.pack(side="left", anchor="w")

        refresh_btn = ctk.CTkButton(
            header, text="ATUALIZAR", width=130, height=38,
            command=self.refresh, **theme.btn_primary(),
        )
        refresh_btn.pack(side="right")

        subtitle = ctk.CTkLabel(
            self, text="Visão geral do autocenter", font=theme.font_body(13),
            text_color=theme.TEXT_MUTED,
        )
        subtitle.pack(anchor="w", padx=32, pady=(0, 20))

        self.cards_frame = ctk.CTkFrame(self, fg_color="transparent")
        self.cards_frame.pack(fill="x", padx=32, pady=(0, 20))
        self.cards_frame.grid_columnconfigure((0, 1, 2, 3), weight=1)

        self.metric_sales = self._create_card(
            self.cards_frame, 0, "Vendas Hoje", "R$ 0,00", theme.PRIMARY, "💰",
            subtitle_text="Faturamento do dia",
        )
        self.metric_low_stock = self._create_card(
            self.cards_frame, 1, "Estoque Baixo", "0 itens", theme.DANGER, "⚠️",
            subtitle_text="Produtos que requerem atenção",
        )
        self.metric_pending_nfe = self._create_card(
            self.cards_frame, 2, "NF-e Processadas", "0", theme.PRIMARY, "📄",
            subtitle_text="Notas importadas",
        )
        self.metric_products = self._create_card(
            self.cards_frame, 3, "Produtos", "0", theme.INFO, "📦",
            subtitle_text="Cadastrados no sistema",
        )

        # Painel inferior (placeholder de análise, no estilo do protótipo)
        bottom = ctk.CTkFrame(self, **theme.card_frame_kwargs())
        bottom.pack(fill="both", expand=True, padx=32, pady=(0, 32))
        ctk.CTkLabel(
            bottom, text="RESUMO OPERACIONAL", font=theme.font_heading(15),
            text_color=theme.TEXT,
        ).pack(anchor="w", padx=24, pady=(20, 10))
        ctk.CTkLabel(
            bottom,
            text="Use o menu lateral para acessar PDV, NF-e, Produtos, Operacional e Suporte.",
            font=theme.font_body(13), text_color=theme.TEXT_MUTED,
        ).pack(anchor="w", padx=24, pady=(0, 20))

    def _create_card(self, parent, column, label_text, value_text, accent_color, icon, subtitle_text=""):
        card = ctk.CTkFrame(parent, **theme.card_frame_kwargs(border_color=accent_color))
        card.grid(row=0, column=column, sticky="nsew", padx=8, pady=8)

        top = ctk.CTkFrame(card, fg_color="transparent")
        top.pack(fill="x", padx=20, pady=(18, 4))

        text_col = ctk.CTkFrame(top, fg_color="transparent")
        text_col.pack(side="left", fill="x", expand=True)

        label = ctk.CTkLabel(
            text_col, text=label_text.upper(), font=(theme.FONT_FAMILY, 12, "bold"),
            text_color=theme.TEXT_MUTED,
        )
        label.pack(anchor="w")

        value = ctk.CTkLabel(
            text_col, text=value_text, font=theme.font_title(30), text_color=accent_color,
        )
        value.pack(anchor="w", pady=(4, 0))

        icon_lbl = ctk.CTkLabel(
            top, text=icon, font=(theme.FONT_FAMILY, 26),
            fg_color=theme.CARD_ALT, text_color=accent_color,
            corner_radius=theme.RADIUS, width=48, height=48,
        )
        icon_lbl.pack(side="right")

        ctk.CTkLabel(
            card, text=subtitle_text, font=(theme.FONT_FAMILY, 11, "bold"),
            text_color=theme.TEXT_MUTED,
        ).pack(anchor="w", padx=20, pady=(0, 18))
=======
        header.pack(fill="x", padx=20, pady=(20, 10))

        title = ctk.CTkLabel(
            header,
            text="DASHBOARD",
            font=("Roboto", 30, "bold"),
            text_color="#ffffff",
        )
        title.pack(side="left")

        refresh_btn = ctk.CTkButton(
            header,
            text="ATUALIZAR",
            width=120,
            command=self.refresh,
        )
        refresh_btn.pack(side="right")

        self.cards_frame = ctk.CTkFrame(self, fg_color="transparent")
        self.cards_frame.pack(fill="both", expand=True, padx=20, pady=20)
        self.cards_frame.grid_columnconfigure((0, 1), weight=1)
        self.cards_frame.grid_rowconfigure((0, 1), weight=1)

        self.metric_sales = self._create_card(self.cards_frame, 0, 0, "Vendas hoje", "R$ 0,00", "#2ecc71")
        self.metric_pending_nfe = self._create_card(self.cards_frame, 0, 1, "NF-e pendentes", "0", "#3498db")
        self.metric_low_stock = self._create_card(self.cards_frame, 1, 0, "Estoque baixo", "0 itens", "#e67e22")
        self.metric_products = self._create_card(self.cards_frame, 1, 1, "Produtos cadastrados", "0", "#9b59b6")

    def _create_card(self, parent, row, column, label_text, value_text, accent_color):
        card = ctk.CTkFrame(parent, corner_radius=16, fg_color="#232323", border_width=1, border_color="#2f2f2f")
        card.grid(row=row, column=column, sticky="nsew", padx=10, pady=10)

        label = ctk.CTkLabel(card, text=label_text, font=("Roboto", 18, "bold"), text_color="#cfcfcf")
        label.pack(anchor="w", padx=20, pady=(18, 6))

        value = ctk.CTkLabel(card, text=value_text, font=("Roboto", 34, "bold"), text_color=accent_color)
        value.pack(anchor="w", padx=20, pady=(0, 18))
>>>>>>> b8696156ad077242d2bbfc43a202beb2b9ea5c18

        return value

    def refresh(self):
        total_sales = 0
        pending_nfe = 0
        low_stock = 0
        total_products = 0

        conn = get_connection()
        cur = conn.cursor()
        try:
            cur.execute("SELECT COALESCE(SUM(total), 0) AS total_sales FROM sales WHERE date(data) = date('now')")
            total_sales = cur.fetchone()["total_sales"] or 0

            cur.execute("SELECT COUNT(*) AS pending FROM purchases WHERE chave_acesso IS NOT NULL")
            pending_nfe = cur.fetchone()["pending"] or 0

            cur.execute("SELECT COUNT(*) AS low_stock FROM products WHERE estoque_atual <= 5")
            low_stock = cur.fetchone()["low_stock"] or 0

            cur.execute("SELECT COUNT(*) AS total_products FROM products")
            total_products = cur.fetchone()["total_products"] or 0
        except sqlite3.OperationalError:
            # O schema ainda pode estar sendo inicializado na primeira execução.
            pass
        finally:
            conn.close()

        self.metric_sales.configure(text=f"R$ {total_sales:.2f}")
        self.metric_pending_nfe.configure(text=str(pending_nfe))
        self.metric_low_stock.configure(text=f"{low_stock} itens")
<<<<<<< HEAD
        self.metric_products.configure(text=str(total_products))
=======
        self.metric_products.configure(text=str(total_products))
>>>>>>> b8696156ad077242d2bbfc43a202beb2b9ea5c18
