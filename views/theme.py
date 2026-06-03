import tkinter as tk
from pathlib import Path
from tkinter import ttk

from utils.helpers import ASSETS_DIR


BRAND_GREEN = "#1F9D55"
BRAND_GREEN_DARK = "#0B4F2A"
BRAND_GREEN_DEEP = "#073B22"
BRAND_GREEN_SOFT = "#EAF7EF"
BRAND_GREEN_PALE = "#F4FBF6"
ACCENT = "#46C97A"
WHITE = "#FFFFFF"
SURFACE = "#F5F7FA"
INK = "#17202A"
MUTED = "#667085"
LINE = "#D9E2EC"
ERROR = "#C2413A"
WARNING = "#B7791F"
SUCCESS = "#18834B"
FONT = "Segoe UI"


def configure_styles(root: tk.Tk):
    style = ttk.Style(root)
    style.theme_use("clam")
    root.configure(bg=SURFACE)
    root.option_add("*Font", (FONT, 10))

    style.configure("TFrame", background=WHITE)
    style.configure("App.TFrame", background=SURFACE)
    style.configure("Card.TFrame", background=WHITE, relief="flat")
    style.configure("Soft.TFrame", background=BRAND_GREEN_SOFT)
    style.configure("Header.TFrame", background=WHITE)
    style.configure("Sidebar.TFrame", background=BRAND_GREEN_DEEP)

    style.configure("TLabel", background=WHITE, foreground=INK, font=(FONT, 10))
    style.configure("App.TLabel", background=SURFACE, foreground=INK)
    style.configure("Muted.TLabel", background=WHITE, foreground=MUTED, font=(FONT, 9))
    style.configure("Soft.TLabel", background=BRAND_GREEN_SOFT, foreground=BRAND_GREEN_DARK)
    style.configure("Header.TLabel", background=WHITE, foreground=INK)
    style.configure("Eyebrow.TLabel", background=WHITE, foreground=BRAND_GREEN, font=(FONT, 9, "bold"))
    style.configure("Title.TLabel", background=WHITE, foreground=INK, font=(FONT, 20, "bold"))
    style.configure("PageTitle.TLabel", background=SURFACE, foreground=INK, font=(FONT, 22, "bold"))
    style.configure("Subtitle.TLabel", background=WHITE, foreground=MUTED, font=(FONT, 10))
    style.configure("PageSubtitle.TLabel", background=SURFACE, foreground=MUTED, font=(FONT, 10))
    style.configure("Metric.TLabel", background=WHITE, foreground=BRAND_GREEN_DARK, font=(FONT, 20, "bold"))
    style.configure("SmallMetric.TLabel", background=WHITE, foreground=BRAND_GREEN_DARK, font=(FONT, 14, "bold"))

    style.configure(
        "TEntry",
        fieldbackground=WHITE,
        background=WHITE,
        foreground=INK,
        bordercolor=LINE,
        lightcolor=LINE,
        darkcolor=LINE,
        padding=(10, 7),
        relief="flat",
    )
    style.map("TEntry", bordercolor=[("focus", BRAND_GREEN)])
    style.configure(
        "TCombobox",
        fieldbackground=WHITE,
        background=WHITE,
        foreground=INK,
        bordercolor=LINE,
        lightcolor=LINE,
        darkcolor=LINE,
        padding=(10, 7),
        relief="flat",
    )
    style.map("TCombobox", bordercolor=[("focus", BRAND_GREEN)])
    style.configure("TSpinbox", padding=(8, 6), bordercolor=LINE)

    _button_style(style, "TButton", WHITE, INK, "#EEF2F6")
    _button_style(style, "Primary.TButton", BRAND_GREEN, WHITE, "#178646")
    _button_style(style, "Success.TButton", SUCCESS, WHITE, "#136C3D")
    _button_style(style, "Secondary.TButton", BRAND_GREEN_SOFT, BRAND_GREEN_DARK, "#DDF3E6")
    _button_style(style, "Danger.TButton", "#FDECEC", ERROR, "#FAD2D2")
    _button_style(style, "Ghost.TButton", SURFACE, INK, "#E8EEF3")

    style.configure(
        "Modern.Treeview",
        rowheight=31,
        fieldbackground=WHITE,
        background=WHITE,
        foreground=INK,
        borderwidth=0,
        relief="flat",
        font=(FONT, 9),
    )
    style.configure(
        "Modern.Treeview.Heading",
        background=BRAND_GREEN_PALE,
        foreground=BRAND_GREEN_DARK,
        font=(FONT, 9, "bold"),
        borderwidth=0,
        relief="flat",
        padding=(8, 8),
    )
    style.map(
        "Modern.Treeview",
        background=[("selected", BRAND_GREEN)],
        foreground=[("selected", WHITE)],
    )
    style.configure("Vertical.TScrollbar", background=BRAND_GREEN_SOFT, troughcolor=SURFACE)

    style.configure("TNotebook", background=WHITE, borderwidth=0)
    style.configure("TNotebook.Tab", padding=(16, 10), background="#EEF2F6", foreground=MUTED)
    style.map("TNotebook.Tab", background=[("selected", WHITE)], foreground=[("selected", BRAND_GREEN_DARK)])


def _button_style(style: ttk.Style, name: str, bg: str, fg: str, active_bg: str):
    style.configure(
        name,
        padding=(16, 10),
        background=bg,
        foreground=fg,
        borderwidth=0,
        focusthickness=0,
        relief="flat",
        font=(FONT, 10, "bold"),
    )
    style.map(name, background=[("active", active_bg), ("pressed", active_bg)], foreground=[("disabled", MUTED)])


def clear(container):
    for child in container.winfo_children():
        child.destroy()


def logo_image(subsample: int = 5):
    path = Path(ASSETS_DIR) / "logo.png"
    if not path.exists():
        return None
    image = tk.PhotoImage(file=str(path))
    return image.subsample(subsample, subsample)


def make_card(parent, padding=18):
    outer = tk.Frame(parent, bg=WHITE, highlightbackground=LINE, highlightthickness=1, bd=0)
    inner = ttk.Frame(outer, padding=padding, style="Card.TFrame")
    inner.pack(fill="both", expand=True)
    return outer, inner


def make_toolbar(parent, padding=14):
    outer, inner = make_card(parent, padding=padding)
    outer.pack(fill="x", pady=(0, 12))
    return inner


def make_tree(parent, columns, headings, stretch_last=True):
    tree = ttk.Treeview(parent, columns=columns, show="headings", selectmode="browse", style="Modern.Treeview")
    for index, column in enumerate(columns):
        tree.heading(column, text=headings.get(column, column))
        width = headings.get(f"{column}_width", 120)
        anchor = headings.get(f"{column}_anchor", "w")
        tree.column(column, width=width, anchor=anchor, stretch=stretch_last and index == len(columns) - 1)
    scrollbar = ttk.Scrollbar(parent, orient="vertical", command=tree.yview, style="Vertical.TScrollbar")
    tree.configure(yscrollcommand=scrollbar.set)
    return tree, scrollbar


def nav_button(parent, text, command, active=False):
    bg = BRAND_GREEN if active else BRAND_GREEN_DEEP
    fg = WHITE if active else "#D9FBE5"
    btn = tk.Button(
        parent,
        text=text,
        anchor="w",
        command=command,
        relief="flat",
        bd=0,
        bg=bg,
        fg=fg,
        activebackground=BRAND_GREEN,
        activeforeground=WHITE,
        padx=16,
        pady=10,
        font=(FONT, 10, "bold"),
        cursor="hand2",
    )
    return btn

