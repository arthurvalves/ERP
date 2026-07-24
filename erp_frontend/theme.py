"""
Design system central do miniERP (customtkinter).

Paleta e tokens extraídos do protótipo de referência (Next.js + Tailwind,
tema dark com destaque âmbar). Todas as telas devem importar as constantes
daqui em vez de usar hex-codes soltos, para manter consistência visual e
facilitar manutenção futura.
"""

# --- Paleta base (dark mode) ---------------------------------------------
BG = "#1e1e1e"                 # fundo geral das telas
SIDEBAR_BG = "#161616"         # fundo da navegação lateral
CARD = "#2a2a2a"               # cards / painéis / cabeçalhos de tabela
CARD_ALT = "#232323"           # variação de card (tabelas, linhas)
SECONDARY = "#404040"          # bordas, superfícies secundárias, top bar
INPUT_BG = "#2a2a2a"

PRIMARY = "#F5B800"            # cor de marca / destaque (âmbar)
PRIMARY_HOVER = "#d9a400"
PRIMARY_FOREGROUND = "#161616" # texto sobre a cor primária

TEXT = "#ffffff"
TEXT_MUTED = "#a0a0a0"

SUCCESS = "#22c55e"
SUCCESS_HOVER = "#16a34a"
DANGER = "#ef4444"
DANGER_HOVER = "#dc2626"
WARNING = "#F5B800"
INFO = "#3b82f6"

# Cores usadas em badges (fundo translúcido simulado com tom sólido escuro
# + texto colorido, já que customtkinter não suporta opacidade real)
BADGE_SUCCESS_BG = "#14321f"
BADGE_SUCCESS_FG = "#4ade80"
BADGE_WARNING_BG = "#332a05"
BADGE_WARNING_FG = "#F5B800"
BADGE_DANGER_BG = "#3a1414"
BADGE_DANGER_FG = "#f87171"
BADGE_INFO_BG = "#132234"
BADGE_INFO_FG = "#60a5fa"
BADGE_PENDING_BG = "#333333"
BADGE_PENDING_FG = "#a0a0a0"

# --- Tipografia ------------------------------------------------------------
FONT_FAMILY = "Roboto"
FONT_MONO = "Consolas"

def font_title(size=28):
    return (FONT_FAMILY, size, "bold")

def font_heading(size=18):
    return (FONT_FAMILY, size, "bold")

def font_body(size=14):
    return (FONT_FAMILY, size)

def font_bold(size=14):
    return (FONT_FAMILY, size, "bold")

def font_mono(size=16):
    return (FONT_MONO, size, "bold")

# --- Raios / espaçamento padrão --------------------------------------------
RADIUS = 8
RADIUS_LG = 12

# --- Helpers de botão -------------------------------------------------------
# Uso: ctk.CTkButton(parent, text="SALVAR", **btn_primary())
def btn_primary(**overrides):
    cfg = dict(
        fg_color=PRIMARY,
        hover_color=PRIMARY_HOVER,
        text_color=PRIMARY_FOREGROUND,
        font=font_bold(14),
        corner_radius=RADIUS,
    )
    cfg.update(overrides)
    return cfg

def btn_success(**overrides):
    cfg = dict(
        fg_color=SUCCESS,
        hover_color=SUCCESS_HOVER,
        text_color="#0b1f12",
        font=font_bold(14),
        corner_radius=RADIUS,
    )
    cfg.update(overrides)
    return cfg

def btn_danger(**overrides):
    cfg = dict(
        fg_color=DANGER,
        hover_color=DANGER_HOVER,
        text_color="#ffffff",
        font=font_bold(14),
        corner_radius=RADIUS,
    )
    cfg.update(overrides)
    return cfg

def btn_secondary(**overrides):
    cfg = dict(
        fg_color=SECONDARY,
        hover_color="#4d4d4d",
        text_color=TEXT,
        font=font_bold(14),
        corner_radius=RADIUS,
    )
    cfg.update(overrides)
    return cfg

def btn_outline(**overrides):
    cfg = dict(
        fg_color="transparent",
        hover_color=CARD,
        text_color=TEXT_MUTED,
        border_width=2,
        border_color=SECONDARY,
        font=font_bold(13),
        corner_radius=RADIUS,
    )
    cfg.update(overrides)
    return cfg

def card_frame_kwargs(border_color=None, **overrides):
    cfg = dict(
        fg_color=CARD,
        corner_radius=RADIUS_LG,
        border_width=2,
        border_color=border_color or SECONDARY,
    )
    cfg.update(overrides)
    return cfg

def badge_colors(kind: str):
    """Retorna (fundo, texto) para uma badge de status.
    kind: 'success' | 'warning' | 'danger' | 'info' | 'pending'
    """
    return {
        "success": (BADGE_SUCCESS_BG, BADGE_SUCCESS_FG),
        "warning": (BADGE_WARNING_BG, BADGE_WARNING_FG),
        "danger": (BADGE_DANGER_BG, BADGE_DANGER_FG),
        "info": (BADGE_INFO_BG, BADGE_INFO_FG),
        "pending": (BADGE_PENDING_BG, BADGE_PENDING_FG),
    }.get(kind, (BADGE_PENDING_BG, BADGE_PENDING_FG))
