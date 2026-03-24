# PDForge — Theme System
# Red + Dark — Premium Dark UI

COLORS = {
    # Backgrounds
    "bg_primary":     "#0D0D0D",   # deepest background
    "bg_secondary":   "#141414",   # sidebar
    "bg_card":        "#1A1A1A",   # cards / panels
    "bg_hover":       "#222222",   # hover state
    "bg_active":      "#2A1515",   # active/selected item

    # Accent — Red family
    "accent":         "#E8272A",   # primary red
    "accent_hover":   "#FF3D40",   # brighter on hover
    "accent_muted":   "#7A1416",   # muted/secondary red
    "accent_subtle":  "#2A1215",   # very subtle red tint bg

    # Text
    "text_primary":   "#F0F0F0",   # main text
    "text_secondary": "#9A9A9A",   # secondary / labels
    "text_muted":     "#555555",   # disabled / placeholder
    "text_accent":    "#E8272A",   # accent text

    # Borders
    "border":         "#2A2A2A",   # default border
    "border_focus":   "#E8272A",   # focused input border
    "border_subtle":  "#1E1E1E",   # very subtle separator

    # Status
    "success":        "#22C55E",
    "warning":        "#F59E0B",
    "error":          "#EF4444",
    "info":           "#3B82F6",
    # Solid panel tints (6-digit only — Tk/Windows rejects #RRGGBBAA)
    "success_soft":   "#0F2918",
    "error_soft":     "#2C1214",
    "warning_soft":   "#2A2210",
    "info_soft":      "#121E2E",

    # Progress
    "progress_bg":    "#2A2A2A",
    "progress_fill":  "#E8272A",

    # Scrollbar
    "scrollbar":      "#333333",
    "scrollbar_hover":"#555555",
}

FONTS = {
    "display":      ("Segoe UI", 28, "bold"),
    "heading":      ("Segoe UI", 18, "bold"),
    "subheading":   ("Segoe UI", 14, "bold"),
    "body":         ("Segoe UI", 13),
    "body_bold":    ("Segoe UI", 13, "bold"),
    "small":        ("Segoe UI", 11),
    "small_bold":   ("Segoe UI", 11, "bold"),
    "caption":      ("Segoe UI", 10),
    "mono":         ("Consolas", 12),
}

RADIUS = {
    "sm":   4,
    "md":   8,
    "lg":   12,
    "xl":   16,
    "full": 999,
}

SPACING = {
    "xs":  4,
    "sm":  8,
    "md":  16,
    "lg":  24,
    "xl":  32,
    "xxl": 48,
}

SIDEBAR_WIDTH  = 260
TOOLBAR_HEIGHT = 56
MIN_WIDTH      = 1100
MIN_HEIGHT     = 700
