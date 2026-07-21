import customtkinter as ctk
from tkinter import filedialog, messagebox
import difflib
import xml.etree.ElementTree as ET

from erp_frontend.components.table import TableComponent
from erp_backend.utils.db import get_connection

from erp_backend.services.matching_service import find_product_match
# IMPORTAÇÕES DEFINITIVAS - Sem try/except
from erp_backend.core.nfe_processor import process_nfe_xml
from erp_backend.core.nfe.nfe_xml_parser import parse_nfe_xml


class NFeView(ctk.CTkFrame):
    def __init__(self, master, app_window, **kwargs):
        super().__init__(master, fg_color="#1e1e1e", **kwargs)
        self.app_window = app_window
        self.current_xml_content = None
        self.current_parsed_data = None
        self.simulated_stats = {}
        self.step = 0  # 0: Inicial, 1: Selecionado, 2: Validado, 3: Simulado
        
        self.setup_ui()
        self.bind_shortcuts()
        
    def setup_ui(self):
        self.header = ctk.CTkFrame(self, fg_color="#2b2b2b", corner_radius=10)
        self.header.pack(fill="x", padx=20, pady=10)
        
        title = ctk.CTkLabel(self.header, text="VALIDAÇÃO DE NF-e", font=("Roboto", 24, "bold"))
        title.pack(side="left")
        
        btn_select = ctk.CTkButton(self.header, text="[F5] Selecionar XML", font=("Roboto", 14), command=self.select_file)
        btn_select.pack(side="right")
        
        self.info_frame = ctk.CTkFrame(self.header, fg_color="transparent")
        self.info_frame.pack(side="left", padx=40)
        
        self.lbl_fornecedor = ctk.CTkLabel(self.info_frame, text="FORNECEDOR: --", font=("Roboto", 14), text_color="#aaaaaa")
        self.lbl_fornecedor.pack(anchor="w")
        self.lbl_chave = ctk.CTkLabel(self.info_frame, text="CHAVE: --", font=("Roboto", 14), text_color="#aaaaaa")
        self.lbl_chave.pack(anchor="w")
        self.lbl_totais = ctk.CTkLabel(self.info_frame, text="EMISSÃO: --  |  TOTAL: --", font=("Roboto", 14), text_color="#aaaaaa")
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
        
        # Configuração de Cores (Tags da Tabela)
        self.table.tag_configure("ok", foreground="#2ecc71")
        self.table.tag_configure("novo", foreground="#f1c40f")
        self.table.tag_configure("divergente", foreground="#e74c3c")
        self.table.tag_configure("revisao", foreground="#e67e22") # <-- NOVA COR LARANJA
        
        self.table.pack(fill="both", expand=True, padx=20, pady=10)
        self.table.bind("<Double-1>", lambda e: self.edit_item())
        self.table.bind("<Return>", lambda e: self.edit_item())
        
        # Painel de Resumo (Oculto até Simulação)
        self.summary_frame = ctk.CTkFrame(self, fg_color="#1a1a1a", border_width=1, border_color="#333333")
        self.summary_frame.pack(fill="x", padx=20, pady=10)
        
        self.lbl_sum_items = ctk.CTkLabel(self.summary_frame, text="TOTAL DE ITENS: 0", font=("Roboto", 14, "bold"))
        self.lbl_sum_items.grid(row=0, column=0, padx=20, pady=10)
        
        self.lbl_sum_stock = ctk.CTkLabel(self.summary_frame, text="IMPACTO ESTOQUE: +0 un", font=("Roboto", 14, "bold"), text_color="#3498db")
        self.lbl_sum_stock.grid(row=0, column=1, padx=20, pady=10)
        
        self.lbl_sum_new = ctk.CTkLabel(self.summary_frame, text="NOVOS PRODUTOS: 0", font=("Roboto", 14, "bold"), text_color="#f1c40f")
        self.lbl_sum_new.grid(row=0, column=2, padx=20, pady=10)
        
        self.lbl_sum_div = ctk.CTkLabel(self.summary_frame, text="DIVERGÊNCIAS: 0", font=("Roboto", 14, "bold"), text_color="#e74c3c")
        self.lbl_sum_div.grid(row=0, column=3, padx=20, pady=10)
        
        # Botões de Ação
        self.footer = ctk.CTkFrame(self, fg_color="transparent")
        self.footer.pack(fill="x", padx=20, pady=(0, 20))
        
        self.btn_import = ctk.CTkButton(self.footer, text="[F10] IMPORTAR FINAL", font=("Roboto", 16, "bold"), fg_color="#2ecc71", hover_color="#27ae60", command=self.import_nfe, state="disabled")
        self.btn_import.pack(side="right", padx=10)
        
        self.btn_simulate = ctk.CTkButton(self.footer, text="[F9] SIMULAR IMPACTO", font=("Roboto", 16, "bold"), fg_color="#f39c12", hover_color="#d68910", command=self.run_simulation, state="disabled")
        self.btn_simulate.pack(side="right", padx=10)
        
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
                
                self.lbl_fornecedor.configure(text=f"FORNECEDOR: {supplier.get('razao_social', 'Desconhecido')}", text_color="white")
                self.lbl_chave.configure(text=f"CHAVE: {header.get('chave_acesso', 'Não encontrada')}", text_color="white")
                self.lbl_totais.configure(text=f"EMISSÃO: {header.get('data_emissao', '--')}  |  TOTAL: R$ {header.get('valor_total', 0):.2f}", text_color="#2ecc71")
                
                self.step = 1
                self.btn_simulate.configure(state="disabled")
                self.btn_import.configure(state="disabled")
                
                # Aciona validação automática
                self.run_validation()
            except Exception as e:
                messagebox.showerror("Erro", f"Erro ao ler XML: {e}")

    def _normalize_string(self, s: str) -> str:
        return s.strip().upper() if s else ""

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
            
            if matched and conf >= 85:
                status, tag = "OK", "ok"
                item_iid = f"matched_{matched['id']}"
                desc = matched['nome']
                
                old_cost = matched['custo']
                if old_cost and old_cost > 0:
                    if abs(v_un - old_cost) / old_cost > 0.15:
                        status, tag = "DIVERGENTE", "divergente"
                        self.simulated_stats['div'] += 1
                pv = matched['preco_venda']
                if pv and pv > 0:
                    margem = f"{((pv - v_un) / pv) * 100:.1f}%"
                    
            elif matched and conf >= 60:
                # SE CAIU AQUI, é uma quase correspondência
                status, tag = "REVISÃO", "revisao"
                item_iid = f"revisao_{idx}_{matched['id']}"
                desc = f"⚠️ PARECIDO COM: {matched['nome']} ({conf}%)"
                self.simulated_stats['revisao'] = self.simulated_stats.get('revisao', 0) + 1
                
            else:
                status, tag = "NOVO", "novo"
                item_iid = f"novo_{idx}"
                desc = f"NOVO: {item['xProd']}"
                self.simulated_stats['new'] += 1

            self.table.insert("", "end", iid=item_iid, values=(
                desc, item['cEAN'] or item['cProd'], f"{q_com:.2f}",
                f"R$ {v_un:.2f}", f"R$ {(v_un * q_com):.2f}",
                status, f"{conf}%", margem
            ), tags=(tag,))

        self.step = 2
        self.btn_simulate.configure(state="normal")

    def run_simulation(self):
        if self.step < 2: return
        
        if self.simulated_stats.get('revisao', 0) > 0:
            messagebox.showwarning("Ação Obrigatória", 
                                   f"Existem {self.simulated_stats['revisao']} produtos pendentes de REVISÃO (linhas laranja).\n\n"
                                   f"O sistema encontrou produtos muito parecidos. Dê um duplo-clique neles para confirmar se é o mesmo produto ou se deve ser registado como novo.")
            return
        
        if self.simulated_stats['new'] > 0:
            messagebox.showwarning("Ação Obrigatória", 
                                   f"Existem {self.simulated_stats['new']} produtos NOVOS não mapeados.\n\n"
                                   f"Para AutoCenters, é obrigatório registrar o Preço de Varejo de todas as peças antes de concluir a importação.\n\n"
                                   f"Dê um duplo-clique nas linhas amarelas na tabela para cadastrá-las.")
            return
            
        self.lbl_sum_items.configure(text=f"TOTAL DE ITENS: {self.simulated_stats['items']}")
        self.lbl_sum_stock.configure(text=f"IMPACTO ESTOQUE: +{self.simulated_stats['stock']} un")
        self.lbl_sum_new.configure(text=f"NOVOS PRODUTOS: {self.simulated_stats['new']}")
        self.lbl_sum_div.configure(text=f"DIVERGÊNCIAS: {self.simulated_stats['div']}")
        
        self.step = 3
        self.btn_import.configure(state="normal")
        
    def edit_item(self, event=None):
        if self.step < 2: return
        selected = self.table.selection()
        if not selected: return
        item_iid = selected[0]
        
        from erp_frontend.products_view import ProductModal
        
        if item_iid.startswith("matched_"):
            prod_id = int(item_iid.split("_")[1])
            ProductModal(self, product_id=prod_id, on_save=self.run_validation)
        elif item_iid.startswith("novo_"):
            idx = int(item_iid.split("_")[1])
            item_data = self.current_parsed_data['items'][idx]
            ean = item_data['cEAN'] if item_data['cEAN'] and 'SEM GTIN' not in item_data['cEAN'].upper() else ""
            init_data = {
                'nome': item_data['xProd'], 'sku': item_data['cProd'],
                'codigo_barras': ean,
                'cfop_padrao': item_data.get('CFOP', ''),
                'custo': float(item_data['vUnCom']) }
            ProductModal(self, initial_data=init_data, on_save=self.run_validation)
        elif item_iid.startswith("revisao_"):
            parts = item_iid.split("_")
            xml_item_idx = int(parts[1])
            matched_prod_id = int(parts[2])
            
            if messagebox.askyesno("Confirmar Correspondência",
                                   f"O item da nota fiscal corresponde ao produto existente ID {matched_prod_id}?\n\n"
                                   f"Clique em 'Sim' para confirmar ou 'Não' para cadastrá-lo como um novo produto."):
                # Futuramente, aqui poderia haver uma lógica para associar o item da NF-e ao produto existente.
                # Por ora, vamos apenas remover o item da revisão para desbloquear a importação.
                self.table.delete(item_iid)
                self.simulated_stats['revisao'] -= 1
                self.run_simulation() # Re-check conditions

    def import_nfe(self):
        if self.step < 3 or not self.current_xml_content: return
        try:
            process_nfe_xml(self.current_xml_content)
            messagebox.showinfo("Sucesso", "NF-e importada com sucesso!")
            self.reset_state()
            
            from erp_frontend.products_view import ProductsView
            self.app_window.show_view(ProductsView)
        except Exception as e:
            messagebox.showerror("Erro na Importação", str(e))

    def reset_state(self):
        self.current_xml_content = None
        self.current_parsed_data = None
        self.step = 0
        for item in self.table.get_children(): self.table.delete(item)
        self.lbl_fornecedor.configure(text="FORNECEDOR: --", text_color="#aaaaaa")
        self.lbl_chave.configure(text="CHAVE: --", text_color="#aaaaaa")
        self.lbl_totais.configure(text="EMISSÃO: --  |  TOTAL: --", text_color="#aaaaaa")
        self.btn_simulate.configure(state="disabled")
        self.btn_import.configure(state="disabled")