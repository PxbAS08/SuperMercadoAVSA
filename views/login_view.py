import tkinter as tk
from tkinter import messagebox, ttk

from config.db_config import describe_config
from controllers.auth_controller import AuthController
from database.connection import DatabaseError
from views.theme import (
    BRAND_GREEN,
    BRAND_GREEN_DARK,
    BRAND_GREEN_DEEP,
    FONT,
    WHITE,
    configure_styles,
    logo_image,
    make_card,
)


class AVSAwareApp(tk.Tk):
    def __init__(self):
        super().__init__()
        self.title("AVSAware / SuperMercado ONIX")
        self.geometry("1220x760")
        self.minsize(1080, 680)
        configure_styles(self)
        self.show_login()

    def set_screen(self, frame_cls, *args):
        for child in self.winfo_children():
            child.destroy()
        frame = frame_cls(self, *args)
        frame.pack(fill="both", expand=True)

    def show_login(self):
        self.set_screen(LoginView)

    def show_admin(self, user: dict):
        from views.admin_dashboard import AdminDashboard

        self.set_screen(AdminDashboard, user, self.show_login)

    def show_client(self, user: dict):
        from views.cliente_home import ClienteHome

        self.set_screen(ClienteHome, user, self.show_login)


class LoginView(ttk.Frame):
    def __init__(self, master: AVSAwareApp):
        super().__init__(master, style="App.TFrame")
        self.auth = AuthController()
        self.username = tk.StringVar()
        self.password = tk.StringVar()
        self.status = tk.StringVar(value=f"Conexion configurada: {describe_config()}")
        self.logo = None
        self._build()

    def _build(self):
        wrapper = ttk.Frame(self, style="App.TFrame")
        wrapper.pack(fill="both", expand=True, padx=34, pady=34)

        hero = tk.Frame(wrapper, bg=BRAND_GREEN_DEEP, bd=0)
        hero.pack(side="left", fill="both", expand=True)
        hero_inner = tk.Frame(hero, bg=BRAND_GREEN_DEEP)
        hero_inner.place(relx=0.5, rely=0.5, anchor="center", relwidth=0.82)

        tk.Label(
            hero_inner,
            text="SuperMercado ONIX",
            bg=BRAND_GREEN_DEEP,
            fg="#B9F6D0",
            font=(FONT, 12, "bold"),
        ).pack(anchor="w", pady=(0, 18))
        tk.Label(
            hero_inner,
            text="Acceso seguro al sistema de gestion.",
            bg=BRAND_GREEN_DEEP,
            fg=WHITE,
            wraplength=430,
            justify="left",
            font=(FONT, 31, "bold"),
        ).pack(anchor="w")
        tk.Label(
            hero_inner,
            text="AVSAware centraliza la operacion diaria del supermercado con una interfaz limpia y profesional.",
            bg=BRAND_GREEN_DEEP,
            fg="#DDFBE8",
            wraplength=430,
            justify="left",
            font=(FONT, 12),
        ).pack(anchor="w", pady=(18, 28))

        stats = tk.Frame(hero_inner, bg=BRAND_GREEN_DEEP)
        stats.pack(fill="x")
        for value, label in [("MySQL", "Base local"), ("ONIX", "Supermercado"), ("AVSAware", "Sistema de gestion")]:
            chip = tk.Frame(stats, bg="#0F6B3B")
            chip.pack(side="left", padx=(0, 10), ipadx=14, ipady=10)
            tk.Label(chip, text=value, bg="#0F6B3B", fg=WHITE, font=(FONT, 13, "bold")).pack(anchor="w")
            tk.Label(chip, text=label, bg="#0F6B3B", fg="#CFF6DD", font=(FONT, 9)).pack(anchor="w")

        panel = ttk.Frame(wrapper, style="App.TFrame")
        panel.pack(side="left", fill="both", expand=True, padx=(26, 0))

        card_outer, card = make_card(panel, padding=34)
        card_outer.place(relx=0.5, rely=0.5, anchor="center", width=465, height=590)

        self.logo = logo_image(subsample=4)
        if self.logo:
            ttk.Label(card, image=self.logo).pack(anchor="w", pady=(0, 12))

        ttk.Label(card, text="Acceso al sistema", style="Title.TLabel").pack(anchor="w")
        ttk.Label(
            card,
            text="Ingresa con tu usuario para abrir el modulo correspondiente a tu rol.",
            style="Subtitle.TLabel",
            wraplength=380,
        ).pack(anchor="w", pady=(4, 24))

        ttk.Label(card, text="Usuario", style="Eyebrow.TLabel").pack(anchor="w")
        ttk.Entry(card, textvariable=self.username).pack(fill="x", pady=(6, 16))
        ttk.Label(card, text="Contrasena", style="Eyebrow.TLabel").pack(anchor="w")
        ttk.Entry(card, textvariable=self.password, show="*").pack(fill="x", pady=(6, 22))

        ttk.Button(card, text="Iniciar sesion", style="Primary.TButton", command=self.login).pack(fill="x")
        ttk.Button(card, text="Crear cuenta de cliente", style="Secondary.TButton", command=self.register_client).pack(
            fill="x",
            pady=(10, 0),
        )

        ttk.Label(
            card,
            textvariable=self.status,
            style="Muted.TLabel",
            wraplength=380,
            justify="left",
        ).pack(side="bottom", anchor="w", pady=(18, 0))

    def login(self):
        username = self.username.get().strip()
        password = self.password.get()
        if not username or not password:
            self.status.set("Ingresa usuario y contrasena.")
            return
        try:
            user = self.auth.login(username, password)
        except DatabaseError as exc:
            messagebox.showerror("Conexion MySQL", str(exc))
            self.status.set("MySQL no esta listo. Importa la base y revisa config/db_config.py.")
            return
        except Exception as exc:
            messagebox.showerror("Inicio de sesion", str(exc))
            return

        if not user:
            self.status.set("Usuario o contrasena incorrectos.")
            return
        if user["rol"] == "CLIENTE":
            self.master.show_client(user)
        else:
            self.master.show_admin(user)

    def register_client(self):
        username = self.username.get().strip()
        password = self.password.get()
        if len(username) < 4 or len(password) < 4:
            self.status.set("Usuario y contrasena deben tener al menos 4 caracteres.")
            return
        try:
            self.auth.register_client(username, password)
            self.status.set("Cliente registrado. Ya puedes iniciar sesion.")
            self.password.set("")
        except Exception as exc:
            messagebox.showerror("Registro", str(exc))
