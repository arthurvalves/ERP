import urllib.parse
import webbrowser
from datetime import datetime

def send_os_whatsapp(telefone: str, os_id: int):
    """
    Abre o WhatsApp Web/Desktop gerando o link encurtado com a mensagem padrão.
    """
    # Formata número de telefone removendo tudo que não for dígito
    phone_digits = "".join(filter(str.isdigit, telefone))
    if len(phone_digits) in [10, 11]:  # Se enviou só o celular com DDD
        phone_digits = "55" + phone_digits
        
    msg = f"Olá! Segue sua Ordem de Serviço Nº {os_id:05d}.\n\n"
    msg += "O documento completo pode ser consultado em nossa oficina.\nQualquer dúvida, estamos à disposição."
    
    encoded_msg = urllib.parse.quote(msg)
    url = f"https://api.whatsapp.com/send?phone={phone_digits}&text={encoded_msg}"
    
    webbrowser.open(url)

def send_installment_due_date_whatsapp(telefone: str, customer_name: str, due_date: datetime, amount: float, installment_str: str):
    """
    Envia um lembrete de vencimento de parcela via WhatsApp.
    """
    phone_digits = "".join(filter(str.isdigit, telefone))
    if len(phone_digits) in [10, 11]:
        phone_digits = "55" + phone_digits

    first_name = customer_name.split(" ")[0]
    due_date_formatted = due_date.strftime("%d/%m/%Y")

    msg = f"Olá, {first_name}! Passando para lembrar sobre sua parcela ({installment_str}) no valor de R$ {amount:.2f}, com vencimento em {due_date_formatted}.\n\n"
    msg += "Agradecemos a sua preferência!"

    encoded_msg = urllib.parse.quote(msg)
    url = f"https://api.whatsapp.com/send?phone={phone_digits}&text={encoded_msg}"
    webbrowser.open(url)

def send_maintenance_alert_whatsapp(telefone: str, customer_name: str, vehicle_plate: str, vehicle_model: str):
    """
    Envia um alerta de manutenção preventiva via WhatsApp.
    """
    phone_digits = "".join(filter(str.isdigit, telefone))
    if len(phone_digits) in [10, 11]:
        phone_digits = "55" + phone_digits

    first_name = customer_name.split(" ")[0]

    msg = f"Olá, {first_name}! Tudo bem?\n\n"
    msg += f"Notamos que a revisão periódica do seu {vehicle_model} (placa {vehicle_plate}) está próxima.\n\n"
    msg += "Gostaria de agendar um horário conosco para garantir que seu veículo continue rodando com segurança? Estamos à disposição!"

    encoded_msg = urllib.parse.quote(msg)
    url = f"https://api.whatsapp.com/send?phone={phone_digits}&text={encoded_msg}"
    webbrowser.open(url)