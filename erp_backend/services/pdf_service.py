from fpdf import FPDF
import os

def generate_os_pdf(filepath: str, os_data: dict, items: list):
    # Força o modo de página estrito para evitar margens desalinhadas
    pdf = FPDF(format='A4')
    pdf.add_page()
    
    # 1. MARGENS E FONTE
    pdf.set_margins(15, 15, 15)
    pdf.set_auto_page_break(auto=True, margin=20)
    
    # 2. CABEÇALHO
    pdf.set_xy(15, 15)
    pdf.set_font('Helvetica', 'B', 14)
    pdf.cell(110, 10, "MINIERP SISTEMAS LTDA - AUTOCENTER", border=0, ln=0, align='L')
    
    # Bloco com fundo cinza claro à direita
    pdf.set_fill_color(240, 240, 240)
    pdf.rect(125, 15, 70, 14, style='F') # Aumentado para 14 para dar respiro

    pdf.set_font('Helvetica', 'B', 10)
    pdf.set_xy(125, 17)
    pdf.cell(70, 4, f"O.S. N°: {os_data.get('id', 0):05d}", border=0, ln=1, align='C')
    pdf.set_font('Helvetica', '', 10)
    pdf.set_xy(125, 22)
    pdf.cell(70, 4, f"Status: {os_data.get('status', 'N/A')}", border=0, ln=1, align='C')
    
    # --- 3. BLOCOS DELIMITADOS (DADOS DO VEÍCULO) ---
    pdf.set_xy(15, 75)
    pdf.set_font('Helvetica', 'B', 10)
    pdf.cell(0, 6, "Dados do Veículo", border=0, ln=1)
    
    # Desenha o box com altura calculada para envelopar o texto perfeitamente
    y_box_veiculo = pdf.get_y()
    pdf.rect(15, y_box_veiculo, 180, 12)
    # Linha divisória no meio do box (15 + 90 = 105)
    pdf.line(105, y_box_veiculo, 105, y_box_veiculo + 12)

    pdf.set_font('Helvetica', '', 10)
    veiculo = os_data.get('veiculo', '')
    placa = os_data.get('placa', '')
    pdf.set_xy(17, y_box_veiculo + 4) # Alinhamento interno com margem de 2mm
    pdf.cell(85, 4, f"Veículo: {veiculo}")
    pdf.set_xy(108, y_box_veiculo + 4) # Posicionamento exato para a placa
    pdf.cell(85, 4, f"Placa: {placa}", ln=1)
    
    # --- BLOCO DIAGNÓSTICO (ALTURA DINÂMICA COMPORTADA) --- 
    pdf.set_xy(15, y_box_veiculo + 28)
    pdf.set_font('Helvetica', 'B', 10)
    pdf.cell(0, 6, "Diagnóstico / Relato do Cliente", border=0, ln=1)
    
    desc = os_data.get('descricao_problema', '')
    
    # Técnica Sênior: Retângulo fixo visual na base, mas conteúdo elástico por dentro
    y_box_desc = pdf.get_y()
    pdf.set_font('Helvetica', '', 10)

    # Calcula quantas linhas o texto vai ocupar para setar a altura mínima do Box em 20mm
    num_linhas = len(pdf.multi_cell(176, 5, desc, split_only=True))
    altura_calculada = max(20, (num_linhas * 5) + 6)

    # Desenha o contorno perfeito
    pdf.rect(15, y_box_desc, 180, altura_calculada)
    pdf.set_xy(18, y_box_desc + 3)
    pdf.multi_cell(174, 5, desc, border=0) # Escreve o texto sem borda interna redundante

    # Posiciona o cursor de forma segura após o término do bloco elástico
    pdf.set_xy(15, y_box_desc + altura_calculada + 15)
    
    # --- 4. TABELA DE ITENS --- 
    pdf.set_font('Helvetica', 'B', 10)
    pdf.set_fill_color(40, 40, 40) # Fundo escuro conforme o prompt de melhoria
    pdf.set_text_color(255, 255, 255) # Texto branco

    pdf.cell(130, 8, "  Descrição", border=0, fill=True)
    pdf.cell(20, 8, "Qtd", border=0, align='C', fill=True)
    pdf.cell(30, 8, "Subtotal  ", border=0, align='R', fill=True, ln=1)
    
    # Reseta cores para listagem dos itens
    pdf.set_text_color(0, 0, 0)
    pdf.set_font('Helvetica', '', 10)
    
    for it in items:
        t = it.get('tipo', 'peca').upper()
        q = float(it.get('quantidade', 0))
        vu = float(it.get('preco_unitario', 0.0))
        sub = (q * vu) - float(it.get('desconto_item', 0.0))
        nome = f" [{t}] {it.get('nome', '')}"
        
        # Alinhamento elegante usando linhas finas inferiores ('B')
        pdf.cell(130, 8, nome[:70], border='B')
        pdf.cell(20, 8, f"{q:.2f}", border='B', align='C')
        pdf.cell(30, 8, f"R$ {sub:.2f}", border='B', align='R', ln=1)
        
    pdf.ln(4)
    
    # --- 5. TOTALIZADORES ---
    pdf.set_font('Helvetica', '', 10)
    pdf.cell(150, 6, "Total Peças:", align='R')
    pdf.cell(30, 6, f"R$ {os_data.get('total_pecas', 0.0):.2f}", align='R', ln=1)
    
    pdf.cell(150, 6, "Total M.O.:", align='R')
    pdf.cell(30, 6, f"R$ {os_data.get('total_servicos', 0.0):.2f}", align='R', ln=1)
    
    pdf.set_font('Helvetica', 'B', 11)
    pdf.cell(150, 8, "TOTAL GERAL:", align='R')
    pdf.cell(30, 8, f"R$ {os_data.get('total_geral', 0.0):.2f}", align='R', ln=1)
    
    # --- 6. ASSINATURAS (BLINDADAS CONTRA QUEBRA DE PÁGINA) --- 
    # Se o cursor atual estiver muito perto da base, joga as assinaturas para a próxima folha
    if pdf.get_y() > 240:
        pdf.add_page()
        
    pdf.set_y(-30) # Força o posicionamento no rodapé da página vigente com segurança
    pdf.set_font('Helvetica', '', 10)
    
    y_line = pdf.get_y()
    pdf.line(25, y_line, 85, y_line) # Linha da assinatura do cliente
    pdf.line(125, y_line, 185, y_line) # Linha da assinatura do técnico
    
    pdf.set_y(y_line + 2)
    pdf.cell(10, 5, "", border=0)
    pdf.cell(60, 5, "Assinatura Cliente", align='C')
    pdf.cell(40, 5, "", border=0)
    pdf.cell(60, 5, "Assinatura Técnico", align='C', ln=1)
    
    # Emissão final do documento faturado
    pdf.output(filepath)