import customtkinter as ctk
from tkinter import filedialog, messagebox
import difflib
import xml.etree.ElementTree as ET

from erp_frontend.components.table import TableComponent
from erp_backend.utils.db import get_connection

from erp_backend.services.matching_service import find_product_match
from erp_backend.core.nfe_processor import process_nfe_xml
from erp_backend.core.nfe.nfe_xml_parser import parse_nfe_xml
from erp_frontend.products_view import ProductModal
from erp_frontend import theme


class NFeView(ctk.CTkFrame):
    def __init__(self, master, app_window, **kwargs):
        super().__init__(master, fg_color=theme.BG, **kwargs)
        self.app_window = app_window
        self.current_xml_content = None
        self.current_parsed_data = None
        self.simulated_stats = {}
        self.step = 0  # 0: Inicial, 1: Selecionado, 2: Validado, 3: Simulado

        self.setup_ui()
        self.bind_shortcuts()

    def setup_ui(self):
        self.header = ctk.CTkFrame(self, **theme.card_frame_kwargs(border_color=theme.PRIMARY))
        self.header.pack(fill="x", padx=20, pady=10)

        title = ctk.CTkLabel(self.header, text="VALIDAÇÃO DE NF-e", font=theme.font_title(24), text_color=theme.PRIMARY)
        title.pack(side="left")

        btn_select = ctk.CTkButton(self.header, text="[F5] Selecionar XML", command=self.select_file, **theme.btn_primary())
        btn_select.pack(side="right")

        self.info_frame = ctk.CTkFrame(self.header, fg_color="transparent")
        self.info_frame.pack(side="left", padx=40)

        self.lbl_fornecedor = ctk.CTkLabel(self.info_frame, text="FORNECEDOR: --", font=theme.font_body(14), text_color=theme.TEXT_MUTED)
        self.lbl_fornecedor.pack(anchor="w")
        self.lbl_chave = ctk.CTkLabel(self.info_frame, text="CHAVE: --", font=theme.font_body(14), text_color=theme.TEXT_MUTED)
        self.lbl_chave.pack(anchor="w")
        self.lbl_totais = ctk.CTkLabel(self.info_frame, text="EMISSÃO: --  |  TOTAL: --", font=theme.font_body(14), text_color=theme.TEXT_MUTED)
        self.lbl_totais.pack(anchor="w")

        columns = ("PRODUTO", "CÓDIGO", "QTD", "CUSTO UN.", "CUSTO TOT.", "STATUS", "CONF.", "MARGEM")
        self.table = TableComponent(self, columns)
        self.table.column("PRODUTO", width=300, anchor="w")
        self.table.column("CÓDIGO", width=100)
        self.table.column("QTD", width=60)
        self.table.column("CUSTO UN.", width=100)
        self.table.column("CUSTO TOT.", width=100)
        self.table.column("STATUS", width=120)
        self.table.column("CONF.", width=60)
        self.table.column("MARGEM", width=80)

        self.table.tag_configure("ok", foreground=theme.SUCCESS)
        self.table.tag_configure("novo", foreground=theme.PRIMARY)
        self.table.tag_configure("divergente", foreground=theme.DANGER)
        self.table.tag_configure("revisao", foreground="#e67e22")

        self.table.pack(fill="both", expand=True, padx=20, pady=10)
        self.table.bind("<Double-1>", lambda e: self.edit_item())
        self.table.bind("<Return>", lambda e: self.edit_item())

        self.summary_frame = ctk.CTkFrame(self, **theme.card_frame_kwargs())
        self.summary_frame.pack(fill="x", padx=20, pady=10)

        self.lbl_sum_items = ctk.CTkLabel(self.summary_frame, text="TOTAL DE ITENS: 0", font=theme.font_bold(14), text_color=theme.TEXT)
        self.lbl_sum_items.grid(row=0, column=0, padx=20, pady=10)

        self.lbl_sum_stock = ctk.CTkLabel(self.summary_frame, text="IMPACTO ESTOQUE: +0 un", font=theme.font_bold(14), text_color=theme.INFO)
        self.lbl_sum_stock.grid(row=0, column=1, padx=20, pady=10)

        self.lbl_sum_new = ctk.CTkLabel(self.summary_frame, text="NOVOS PRODUTOS: 0", font=theme.font_bold(14), text_color=theme.PRIMARY)
        self.lbl_sum_new.grid(row=0, column=2, padx=20, pady=10)

        self.lbl_sum_div = ctk.CTkLabel(self.summary_frame, text="DIVERGÊNCIAS: 0", font=theme.font_bold(14), text_color=theme.DANGER)
        self.lbl_sum_div.grid(row=0, column=3, padx=20, pady=10)

        self.footer = ctk.CTkFrame(self, fg_color="transparent")
        self.footer.pack(fill="x", padx=20, pady=(0, 20))

        self.btn_import = ctk.CTkButton(self.footer, text="[F10] IMPORTAR FINAL", command=self.import_nfe, state="disabled",
                                         **theme.btn_success(font=theme.font_bold(16)))
        self.btn_import.pack(side="right", padx=10)

        self.btn_simulate = ctk.CTkButton(self.footer, text="[F9] SIMULAR IMPACTO", command=self.run_simulation, state="disabled",
                                           **theme.btn_primary(font=theme.font_bold(16)))
        self.btn_simulate.pack(side="right", padx=10)

    def import_nfe(self, event=None):
        if self.step < 2 or not self.current_xml_content:
            messagebox.showwarning("Ação Inválida", "Selecione e valide um arquivo XML primeiro.")
            return
        try:
            result = process_nfe_xml(self.current_xml_content)
            messagebox.showinfo("Sucesso", f"NF-e importada com sucesso!\nStatus: {result.get('status')}")
            self.reset_state()
        except Exception as e:
            messagebox.showerror("Erro na Importação", f"Ocorreu um erro crítico: {e}")

    def edit_item(self):
        selected = self.table.selection()
        if not selected:
            return

        item_index = int(selected[0])
        if self.current_parsed_data and item_index < len(self.current_parsed_data['items']):
            item_data = self.current_parsed_data['items'][item_index]

            initial_data = {
                'nome': item_data.get('xProd'),
                'sku': item_data.get('cProd'),
                'codigo_barras': item_data.get('cEAN'),
                'custo': float(item_data.get('vUnCom', 0.0)),
                'cfop_padrao': item_data.get('CFOP'),
            }
            ProductModal(self, initial_data=initial_data, on_save=self.run_validation)

    def import_nfe(self, event=None):
        if self.step < 2 or not self.current_xml_content:
            messagebox.showwarning("Ação Inválida", "Selecione e valide um arquivo XML primeiro.")
            return
        try:
            result = process_nfe_xml(self.current_xml_content)
            messagebox.showinfo("Sucesso", f"NF-e importada com sucesso!\nStatus: {result.get('status')}")
            self.reset_state()
        except Exception as e:
            messagebox.showerror("Erro na Importação", f"Ocorreu um erro crítico: {e}")

    def bind_shortcuts(self):
        self.app_window.bind("<F5>", lambda e: self.select_file())
        self.app_window.bind("<F9>", lambda e: self.run_simulation())
        self.app_window.bind("<F10>", lambda e: self.import_nfe())
        self.app_window.bind("<Return>", lambda e: self.next_step())
        self.app_window.bind("<Escape>", lambda e: self.reset_state())

    def unbind_shortcuts(self):
        self.app_window.unbind("<F5>")
        self.app_window.unbind("<F9>")
        self.app_window.unbind("<F10>")
        self.app_window.unbind("<Return>")
        self.app_window.unbind("<Escape>")

    def destroy(self):
        self.unbind_shortcuts()
        super().destroy()

    def next_step(self):
        if self.step == 0 and self.current_xml_content: pass
        elif self.step == 1: self.run_validation()
        elif self.step == 2: self.run_simulation()
        elif self.step == 3: self.import_nfe()

    def select_file(self, event=None):
        path = filedialog.askopenfilename(filetypes=[("XML files", "*.xml")])
        if path:
            try:
                with open(path, 'r', encoding='utf-8') as f:
                    self.current_xml_content = f.read()

                self.current_parsed_data = parse_nfe_xml(self.current_xml_content)
                header = self.current_parsed_data['header']
                supplier = self.current_parsed_data['supplier']

                self.lbl_fornecedor.configure(text=f"FORNECEDOR: {supplier.get('razao_social', 'Desconhecido')}", text_color=theme.TEXT)
                self.lbl_chave.configure(text=f"CHAVE: {header.get('chave_acesso', 'Não encontrada')}", text_color=theme.TEXT)
                self.lbl_totais.configure(text=f"EMISSÃO: {header.get('data_emissao', '--')}  |  TOTAL: R$ {header.get('valor_total', 0):.2f}", text_color=theme.SUCCESS)

                self.step = 1
                self.btn_simulate.configure(state="disabled")
                self.btn_import.configure(state="disabled")

                self.run_validation()
            except Exception as e:
                messagebox.showerror("Erro", f"Erro ao ler XML: {e}")

    def _normalize_string(self, s: str) -> str:
        return s.strip().upper() if s else ""

    def run_simulation(self, event=None):
        if self.step < 1:
            return

        self.lbl_sum_items.configure(text=f"TOTAL DE ITENS: {self.simulated_stats.get('items', 0)}")
        self.lbl_sum_stock.configure(text=f"IMPACTO ESTOQUE: +{self.simulated_stats.get('stock', 0):.2f} un")
        self.lbl_sum_new.configure(text=f"NOVOS PRODUTOS: {self.simulated_stats.get('new', 0)}")
        self.lbl_sum_div.configure(text=f"DIVERGÊNCIAS: {self.simulated_stats.get('div', 0)}")

        self.step = 3
        self.btn_import.configure(state="normal")
        self.btn_simulate.configure(state="disabled")
        messagebox.showinfo("Simulação Concluída", "Impacto da NF-e simulado. Verifique os totais e os status dos itens. Pressione [F10] para confirmar a importação.")

    def run_validation(self):
        if self.step < 1 or not self.current_parsed_data: return
        conn = get_connection()
        cur = conn.cursor()
        cur.execute("SELECT id, nome, nome_normalizado, codigo_barras, ncm, referencia, fornecedor_id, custo, estoque_atual, preco_venda FROM products")
        all_products = [dict(row) for row in cur.fetchall()]
        cnpj = self.current_parsed_data['supplier']['cnpj']
        cur.execute("SELECT id FROM suppliers WHERE cnpj = ?", (cnpj,))
        sup = cur.fetchone()
        supplier_id = sup['id'] if sup else None
        conn.close()
        for item in self.table.get_children(): self.table.delete(item)
        self.simulated_stats = {'items': 0, 'stock': 0, 'new': 0, 'div': 0, 'total_value': 0.0}

        for idx, item in enumerate(self.current_parsed_data['items']):
            match_result = find_product_match(item, all_products, supplier_id)
            matched = match_result['product']
            conf = match_result['confidence']

            v_un = float(item['vUnCom'])
            q_com = float(item['qCom'])
            margem = "--"

            self.simulated_stats['items'] += 1
            self.simulated_stats['stock'] += q_com
            
            # --- LÓGICA DE STATUS E TAGS PARA A TABELA ---
            if not matched:
                status, tag = "NOVO", "novo"
                self.simulated_stats['new'] += 1
            elif conf < 100:
                status, tag = "REVISAR", "revisao"
                self.simulated_stats['div'] += 1
            else:
                status, tag = "OK", "ok"

            # --- INSERÇÃO DO ITEM NA TABELA (CORREÇÃO) ---
            self.table.insert("", "end", iid=str(idx), values=(
                item['xProd'],
                item['cProd'],
                f"{q_com:.2f}",
                f"R$ {v_un:.2f}",
                f"R$ {v_un * q_com:.2f}",
                status,
                f"{conf}%",
                margem
            ), tags=(tag,))

        self.btn_simulate.configure(state="normal")

    def reset_state(self):
        self.current_xml_content = None
        self.current_parsed_data = None
        self.step = 0