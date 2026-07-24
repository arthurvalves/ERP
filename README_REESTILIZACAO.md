# Novo visual do miniERP (convertido do protótipo Next.js/Tailwind)

Este pacote é um **drop-in replacement** da pasta `erp_frontend/` do seu projeto.
Nenhuma lógica de negócio foi alterada: todas as chamadas a `erp_backend`,
validações, atalhos de teclado e fluxos de tela continuam exatamente iguais.
Só o visual (cores, tipografia, navegação, tabelas, botões) foi convertido para
customtkinter seguindo o design system extraído do protótipo `sistema-erp-pdv`
(Next.js + Tailwind, tema dark com destaque âmbar).

## Como aplicar
1. Faça backup da sua pasta `erp_frontend/` atual.
2. Substitua-a inteiramente pela pasta `erp_frontend/` deste pacote.
3. Nada muda em `erp_backend/`, `start.py`, `run_demo.py` ou no banco de dados
   — não é necessário migrar nada.
4. Rode normalmente com `python start.py`.

## O que mudou

- **`erp_frontend/theme.py`** (novo arquivo): fonte única de verdade para
  cores, fontes, raios de borda e helpers de botão (`btn_primary`,
  `btn_success`, `btn_danger`, `btn_secondary`, `card_frame_kwargs`, etc.).
  Qualquer ajuste futuro de paleta é feito só aqui.
- **`main_window.py`**: layout novo com barra lateral fixa (estilo
  `SystemNav` do protótipo: PDV, NF-e, Dashboard, Produtos, Operacional,
  Suporte) + barra superior com dropdowns (Cadastros, Operacional, Análise,
  Financeiro, Administrativo), relógio ao vivo e usuário logado — igual à
  `TopBar` do protótipo. Todas as telas antigas continuam acessíveis, só
  reorganizadas nesses menus.
- **`components/table.py`**: tabelas (Treeview) redesenhadas — fundo escuro,
  cabeçalho em destaque, seleção de linha na cor primária (âmbar).
- **`dashboard_view.py`**: cards de métricas com borda colorida, número
  grande e ícone, no mesmo estilo do protótipo.
- Demais telas (`products_view.py`, `pdv_view.py`, `os_view.py`, `nfe_view.py`,
  `customers_view.py`, `quotes_view.py`, modais, etc.) foram recoloridas para
  o mesmo padrão: fundo `#1e1e1e`, cards `#2a2a2a`, bordas `#404040`, botão de
  ação principal em âmbar (`#F5B800`), sucesso em verde, destrutivo em
  vermelho — mantendo 100% da lógica original.

## Paleta de referência

| Token              | Cor       |
|---------------------|-----------|
| Fundo               | `#1e1e1e` |
| Sidebar             | `#161616` |
| Card                | `#2a2a2a` |
| Borda/Secundário    | `#404040` |
| Primária (âmbar)    | `#F5B800` |
| Sucesso             | `#22c55e` |
| Destrutivo          | `#ef4444` |
| Info                | `#3b82f6` |

## Observações

- `login_view.py` e `categories_view.py` já estavam vazios no projeto
  original (sem conteúdo/lógica) e foram mantidos assim — nada foi inventado
  além do que já existia.
- Como o customtkinter não roda em modo headless neste ambiente, a validação
  foi feita via checagem de sintaxe (`py_compile`) em todos os arquivos e
  checagem cruzada de que todo uso de `theme.X` corresponde a algo realmente
  definido em `theme.py`. Recomendo abrir o app localmente para um ajuste
  fino de espaçamentos se algo parecer apertado na sua resolução de tela.
