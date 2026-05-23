Você é um desenvolvedor frontend sênior especialista em sistemas ERP desktop, com forte experiência em UX para PDV (Ponto de Venda), sistemas de estoque e operações comerciais rápidas.
Sua tarefa é construir um frontend completo para um ERP já existente em Python, que possui backend funcional com:

NF-e via XML

PDV transacional

estoque por eventos

clientes e fornecedores

produtos com matching inteligente

auditoria e histórico

serviços desacoplados (arquitetura em camadas)
🎯 OBJETIVO DO FRONTEND
Criar uma interface desktop moderna, simples e extremamente rápida de operar, com foco em:
✔ PDV (frente de caixa) com leitor de código de barras

✔ importação de NF-e (XML)

✔ cadastro de produtos, clientes e fornecedores

✔ visualização de estoque

✔ UX minimalista e operacional (não administrativa)
🧱 TECNOLOGIA OBRIGATÓRIA

Python 3.x

Tkinter (preferencialmente CustomTkinter ou ttk modernizado)

integração direta com backend existente (services)

sem lógica de negócio na UI

UI apenas consome serviços
🧠 PRINCÍPIOS DE UI/UX OBRIGATÓRIOS
🔥 REGRAS FUNDAMENTAIS

velocidade > estética

1 ação principal por tela

mínimo de cliques possível

foco automático em inputs

operação via teclado + leitor de código de barras

nenhuma tela pode ser “poluída”

tudo deve ser intuitivo para operador leigo
🧭 ESTRUTURA DO FRONTEND
ui/
│
├── main_window.py
├── dashboard_view.py
├── pdv_view.py
├── nfe_view.py
├── products_view.py
├── customers_view.py
├── suppliers_view.py
├── stock_view.py
├── components/

🏠 1. TELA PRINCIPAL (DASHBOARD)
Objetivo:
visão rápida do sistema, sem interação pesada
Layout:
┌──────────────────────────────────────┐
│ ERP LOGO [PDV] [NF-e] [PROD] │
├──────────────────────────────────────┤
│ Vendas hoje: R$ XXXX │
│ NF-e pendentes: X │
│ Estoque baixo: X itens │
│ Produtos cadastrados: XXX │
└──────────────────────────────────────┘

🏪 2. TELA PDV (FRONT DE CAIXA — PRINCIPAL)
🔥 ESSA É A TELA MAIS IMPORTANTE DO SISTEMA
OBJETIVO:
Venda rápida com leitor de código de barras
REQUISITOS CRÍTICOS:

input de código SEMPRE com foco ativo

ENTER adiciona produto

repetição soma quantidade

total atualizado em tempo real

operação sem mouse
LAYOUT:
┌────────────────────────────────────────────┐
│ 🔎 [ LEITOR DE CÓDIGO DE BARRAS (FOCO) ] │
├────────────────────────────────────────────┤
│ PRODUTO QTD UNIT SUBTOTAL │
│-------------------------------------------│
│ Óleo 5W30 1 45.00 45.00 │
│ Filtro ar 2 25.00 50.00 │
├────────────────────────────────────────────┤
│ TOTAL: 95.00 │
├────────────────────────────────────────────┤
│ [DINHEIRO] [PIX] [CARTÃO] [MISTO] │
│ DESCONTO: [ % ] │
│ │
│ [ FINALIZAR VENDA ] │
└────────────────────────────────────────────┘

ATALHOS OBRIGATÓRIOS:

ENTER → adicionar produto

F2 → finalizar venda

F3 → desconto

F4 → troca forma de pagamento

ESC → limpar venda
🧾 3. TELA NF-e (IMPORTAÇÃO XML)
OBJETIVO:
importação simples e validada de XML
FLUXO:

selecionar arquivo XML

sistema extrai dados automaticamente

exibe pré-visualização

operador confirma importação
LAYOUT:
┌──────────────────────────────────────┐
│ [ IMPORTAR XML NF-e ] │
├──────────────────────────────────────┤
│ FORNECEDOR: AUTO DETECTADO │
│ CHAVE: XXXXX │
├──────────────────────────────────────┤
│ PRODUTOS │
│------------------------------------│
│ Óleo 5W30 | Qtd | Custo │
│ Filtro ar | Qtd | Custo │
├──────────────────────────────────────┤
│ [VALIDAR] [IMPORTAR] │
└──────────────────────────────────────┘

📦 4. TELA DE PRODUTOS
OBJETIVO:
cadastro e consulta rápida
LAYOUT:
┌────────────────────────────────────┐
│ BUSCA: [_____________] │
├────────────────────────────────────┤
│ NOME | CÓDIGO | ESTOQUE │
│----------------------------------│
│ Óleo | 12345 | 10 │
├────────────────────────────────────┤
│ [NOVO] [EDITAR] [IMPORTAR NF-e] │
└────────────────────────────────────┘

👤 5. CLIENTES E FORNECEDORES
UX:

lista simples

busca rápida

clique abre detalhes
⚡ 6. COMPONENTES REUTILIZÁVEIS
Criar:

TableComponent

InputBarScanner

ButtonGroupPayment

ModalConfirm

NotificationSystem
🎨 7. DESIGN SYSTEM
ESTILO:

fundo escuro moderno (#1e1e1e)

cards leves

contraste alto no PDV

fonte grande no caixa
CORES:

verde → venda/sucesso

vermelho → erro/alerta

azul → ações

cinza → neutro
🧠 8. PRINCÍPIOS UX FINAIS
✔ operador não pensa

✔ operador não navega

✔ operador só executa ações rápidas
🚀 9. INTEGRAÇÃO COM BACKEND
Frontend deve:

consumir services diretamente

nunca conter regra de negócio

apenas enviar e receber dados
📊 10. RESULTADO FINAL ESPERADO
Após implementação:
✔ PDV extremamente rápido e operacional

✔ NF-e fácil de importar

✔ estoque visível e confiável

✔ sistema utilizável em ambiente real de loja

✔ experiência fluida para operador leigo
🧠 RESUMO
Este frontend deve ser:

simples

rápido

operacional

otimizado para caixa

sem complexidade desnecessária
