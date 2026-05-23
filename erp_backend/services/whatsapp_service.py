import urllib.parse
import webbrowser

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