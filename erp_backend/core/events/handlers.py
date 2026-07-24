from .event_bus import subscribe
import logging

logger = logging.getLogger(__name__)

def _handle_nfe_imported(payload: dict):
    """
    Handler acionado APÓS o processamento transacional da NF-e.
    
    Atenção: Toda a lógica de persistência (compras, fornecedores, produtos e 
    reconciliação de stock) já foi executada de forma segura no nfe_processor.py.
    
    Este handler destina-se APENAS a tratar reações secundárias, tais como:
    - Atualização em tempo real do Dashboard via WebSockets
    - Notificações de sistema ("Novos produtos adicionados")
    - Acionamento automático do serviço de impressão de etiquetas
    - Atualização do motor de busca
    """
    # O novo nfe_processor.py emite o evento com 'chave_acesso' e 'purchase_id'
    chave = payload.get('chave_acesso') or payload.get('chave', 'Desconhecida')
    purchase_id = payload.get('purchase_id', 'N/A')
    
    # 1. Registo de Log do Evento
    logger.info(f"[EVENT BUS] Evento NFeImported processado. Chave: {chave} | Purchase ID: {purchase_id}")
    
    # 2. (Exemplo) Aqui poderíamos adicionar lógicas futuras não-críticas:
    # try:
    #     from erp_backend.services.printer_service import print_product_labels
    #     print_product_labels(purchase_id)
    # except Exception as e:
    #     logger.error(f"Erro ao imprimir etiquetas da NF-e {chave}: {e}")

# Subscrição dos eventos do sistema
subscribe('NFeImported', _handle_nfe_imported)

# (Outros handlers, como 'SaleCompleted' ou 'ProductCreated' podem ser adicionados abaixo)