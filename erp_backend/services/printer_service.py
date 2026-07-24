import json
import os
import datetime

CONFIG_FILE = "printer_config.json"

def get_default_printer() -> str:
    if os.path.exists(CONFIG_FILE):
        try:
            with open(CONFIG_FILE, 'r', encoding='utf-8') as f:
                return json.load(f).get("printer", "PDF (Salvar arquivo)")
        except Exception:
            pass
    return "PDF (Salvar arquivo)"

def set_default_printer(printer_name: str):
    with open(CONFIG_FILE, 'w', encoding='utf-8') as f:
        json.dump({"printer": printer_name}, f)

def get_available_printers() -> list:
    # Em um ambiente real Windows, usaríamos win32print.EnumPrinters
    # Aqui vamos mockar impressoras clássicas de balcão e a opção virtual PDF
    return [
        "PDF (Salvar arquivo)",
        "LPT1 (ESC/POS Direto)",
        "COM1 (ESC/POS Serial)",
        "Impressora Termica USB 80mm",
        "Microsoft Print to PDF"
    ]

def format_line(left: str, right: str, width: int = 40) -> str:
    spaces = width - len(left) - len(right)
    if spaces < 0:
        left = left[:width - len(right) - 1]
        spaces = 1
    return f"{left}{' ' * spaces}{right}"

def generate_os_receipt_text(os_id: int, os_data: dict, items: list) -> str:
    now = datetime.datetime.now().strftime("%d/%m/%Y %H:%M")
    
    lines = []
    lines.append("ODAIR AUTOCENTER".center(40))
    lines.append("52.487.021/0001-8".center(40))
    lines.append("RODOVIA AL-430 S/N.º".center(40))
    lines.append("NOVA FLEXEIRAS - 57995-000".center(40))
    lines.append("ORDEM DE SERVICO".center(40))
    lines.append("-" * 40)
    lines.append(format_line(f"OS NUM: {os_id:05d}", now))
    lines.append(format_line(f"PLACA: {os_data.get('placa','')[:10]}", f"STATUS: {os_data.get('status','')[:10]}"))
    lines.append(f"VEICULO: {os_data.get('veiculo','')[:30]}")
    lines.append("-" * 40)
    lines.append(format_line("QTD  DESCRICAO", "SUBTOTAL"))
    lines.append("-" * 40)
    
    for item in items:
        qtd = float(item['quantidade'])
        vu = float(item['preco_unitario'])
        subt = (qtd * vu) - float(item.get('desconto_item', 0.0))
        nome = str(item.get('nome', ''))[:28].upper()
        
        # Linha principal do item
        lines.append(format_line(f"{qtd:.2f}x {nome}", f"R$ {subt:.2f}"))
        
    lines.append("-" * 40)
    lines.append(format_line("TOTAL PECAS:", f"R$ {os_data.get('total_pecas',0):.2f}"))
    lines.append(format_line("TOTAL M.O.:", f"R$ {os_data.get('total_servicos',0):.2f}"))
    lines.append("-" * 40)
    lines.append(format_line("TOTAL GERAL:", f"R$ {os_data.get('total_geral',0):.2f}"))
    lines.append("=" * 40)
    lines.append("ASSINATURA DO CLIENTE".center(40))
    lines.append("")
    lines.append("_________________________________".center(40))
    lines.append("=" * 40)
    return "\n".join(lines)

def generate_receipt_text(sale_id: int, cart: list, total: float, payment_method: str, desconto_total: float = 0.0) -> str:
    now = datetime.datetime.now().strftime("%d/%m/%Y %H:%M")
    
    lines = ["ODAIR AUTOCENTER".center(40)]
    lines.append("52.487.021/0001-8".center(40))
    lines.append("RODOVIA AL-430 S/N.º".center(40))
    lines.append("NOVA FLEXEIRAS - 57995-000".center(40))
    lines.append("FONE: (82) 99970-5526".center(40))
    lines.append("-" * 40)
    lines.append(format_line("VENDA / CUPOM", now))
    lines.append(format_line(f"DOC: {sale_id:06d}", "OPERADOR: CAIXA 01"))
    lines.append("-" * 40)
    lines.append("CLIENTE: CONSUMIDOR FINAL")
    lines.append("CPF/CNPJ: NAO INFORMADO")
    lines.append("-" * 40)
    
    for item in cart:
        prod = item['product']
        qtd = float(item['quantidade'])
        vu = float(item['preco_unitario'])
        desc_item = float(item.get('desconto_item', 0.0))
        subt = (qtd * vu) - desc_item
        
        nome = (prod.nome or "PRODUTO").upper()[:30]
        sku = (prod.sku or "0000")[:6]
        
        lines.append(f"{sku}  {nome}")
        left_line = f"       {qtd:.2f} X {vu:.2f}"
        right_line = f"SUBTOTAL: {subt:.2f}"
        lines.append(format_line(left_line, right_line))
        if desc_item > 0:
            lines.append(format_line("       DESC. ITEM:", f"-{desc_item:.2f}"))
        
    lines.append("-" * 40)
    subtotal_geral = total + desconto_total
    lines.append(format_line("SUBTOTAL:", f"{subtotal_geral:.2f}"))
    lines.append(format_line("DESCONTO TOTAL:", f"{desconto_total:.2f}"))
    lines.append("-" * 40)
    lines.append(format_line("TOTAL:", f"{total:.2f}"))
    lines.append(format_line("PAGAMENTO:", payment_method.upper()))
    lines.append("=" * 40)
    lines.append("OBRIGADO PELA PREFERENCIA".center(40))
    lines.append("VOLTE SEMPRE!".center(40))
    lines.append("=" * 40)
    
    return "\n".join(lines)

def save_receipt_pdf(text: str, filepath: str):
    from reportlab.pdfgen import canvas
    from reportlab.lib.pagesizes import mm
    
    width = 80 * mm
    lines = text.split('\n')
    height = (len(lines) * 12) + 40 
    c = canvas.Canvas(filepath, pagesize=(width, height))
    c.setFont("Courier-Bold", 9)
    y = height - 20
    for line in lines:
        c.drawString(10, y, line)
        y -= 12
    c.save()

def save_receipt_txt(text: str, filepath: str):
    """Salva o texto do cupom em um arquivo .txt simples, ideal para impressoras térmicas."""
    try:
        with open(filepath, 'w', encoding='utf-8') as f:
            f.write(text)
    except IOError as e:
        raise IOError(f"Não foi possível salvar o arquivo de texto do cupom: {e}") from e