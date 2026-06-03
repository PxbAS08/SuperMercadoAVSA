import tkinter as tk
from tkinter import messagebox, ttk

from utils.helpers import money
from views.theme import BRAND_GREEN_DARK, FONT, MUTED, WHITE, make_card


class ClienteCarritoView(ttk.Frame):
    def __init__(self, master, checkout_callback):
        super().__init__(master, padding=8)
        self.checkout_callback = checkout_callback
        self.modality = tk.StringVar()
        self.payment = tk.StringVar()
        self.address = tk.StringVar()
        self.saved_card = tk.StringVar(value="Nueva tarjeta")
        self.card_number = tk.StringVar()
        self.card_holder = tk.StringVar()
        self.card_expiry = tk.StringVar()
        self.card_cvv = tk.StringVar()
        self.save_card = tk.BooleanVar(value=False)
        self.cart: dict[int, dict] = {}
        self.cards: list[dict] = []
        self._build()

    def _build(self):
        self.configure(style="App.TFrame")
        outer, card = make_card(self, padding=16)
        outer.pack(fill="both", expand=True)
        card.columnconfigure(0, weight=1)
        card.rowconfigure(2, weight=1)

        tk.Label(card, text="Carrito de compras", bg=WHITE, fg=BRAND_GREEN_DARK, font=(FONT, 17, "bold")).grid(row=0, column=0, sticky="w")
        tk.Label(card, text="Selecciona modalidad, pago y registra tu pedido.", bg=WHITE, fg=MUTED, font=(FONT, 9)).grid(row=1, column=0, sticky="w", pady=(2, 10))
        self.tree = ttk.Treeview(card, columns=("nombre", "cantidad", "total"), show="headings", height=6, style="Modern.Treeview")
        self.tree.heading("nombre", text="Producto")
        self.tree.heading("cantidad", text="Cant.")
        self.tree.heading("total", text="Total")
        self.tree.column("nombre", width=230)
        self.tree.grid(row=2, column=0, sticky="nsew", pady=(0, 10))

        form = ttk.Frame(card)
        form.grid(row=3, column=0, sticky="ew")
        ttk.Label(form, text="Modalidad", style="Eyebrow.TLabel").grid(row=0, column=0, sticky="w")
        ttk.Label(form, text="Pago", style="Eyebrow.TLabel").grid(row=0, column=1, sticky="w", padx=(8, 0))
        self.modality_combo = ttk.Combobox(form, textvariable=self.modality, state="readonly", width=21)
        self.payment_combo = ttk.Combobox(form, textvariable=self.payment, state="readonly", width=21)
        self.modality_combo.grid(row=1, column=0, sticky="ew")
        self.payment_combo.grid(row=1, column=1, sticky="ew", padx=(8, 0))
        ttk.Label(form, text="Direccion", style="Eyebrow.TLabel").grid(row=2, column=0, columnspan=2, sticky="w", pady=(8, 0))
        self.address_entry = ttk.Entry(form, textvariable=self.address)
        self.address_entry.grid(row=3, column=0, columnspan=2, sticky="ew")
        form.columnconfigure(0, weight=1)
        form.columnconfigure(1, weight=1)
        self.modality_combo.bind("<<ComboboxSelected>>", lambda _event: self._update_address_state())
        self.payment_combo.bind("<<ComboboxSelected>>", lambda _event: self._update_payment_state())

        self.card_frame = ttk.Frame(card)
        self.card_frame.grid(row=4, column=0, sticky="ew", pady=(8, 0))
        for column in range(2):
            self.card_frame.columnconfigure(column, weight=1)
        ttk.Label(self.card_frame, text="Tarjeta guardada", style="Eyebrow.TLabel").grid(row=0, column=0, sticky="w")
        self.saved_card_combo = ttk.Combobox(self.card_frame, textvariable=self.saved_card, state="readonly")
        self.saved_card_combo.grid(row=1, column=0, columnspan=2, sticky="ew", pady=(2, 8))
        self.saved_card_combo.bind("<<ComboboxSelected>>", lambda _event: self._load_selected_card())
        ttk.Label(self.card_frame, text="Numero de tarjeta", style="Eyebrow.TLabel").grid(row=2, column=0, sticky="w")
        ttk.Label(self.card_frame, text="Titular", style="Eyebrow.TLabel").grid(row=2, column=1, sticky="w", padx=(8, 0))
        ttk.Entry(self.card_frame, textvariable=self.card_number).grid(row=3, column=0, sticky="ew")
        ttk.Entry(self.card_frame, textvariable=self.card_holder).grid(row=3, column=1, sticky="ew", padx=(8, 0))
        ttk.Label(self.card_frame, text="Vencimiento", style="Eyebrow.TLabel").grid(row=4, column=0, sticky="w", pady=(8, 0))
        ttk.Label(self.card_frame, text="CVV", style="Eyebrow.TLabel").grid(row=4, column=1, sticky="w", padx=(8, 0), pady=(8, 0))
        ttk.Entry(self.card_frame, textvariable=self.card_expiry).grid(row=5, column=0, sticky="ew")
        ttk.Entry(self.card_frame, textvariable=self.card_cvv, show="*").grid(row=5, column=1, sticky="ew", padx=(8, 0))
        ttk.Checkbutton(self.card_frame, text="Guardar tarjeta para futuras compras", variable=self.save_card).grid(row=6, column=0, columnspan=2, sticky="w", pady=(8, 0))

        total_box = tk.Frame(card, bg="#F4FBF6")
        total_box.grid(row=5, column=0, sticky="ew", pady=8, ipadx=12, ipady=10)
        tk.Label(total_box, text="Total del pedido", bg="#F4FBF6", fg=MUTED, font=(FONT, 9, "bold")).pack(anchor="w", padx=10)
        self.total_label = tk.Label(total_box, text="$0.00", bg="#F4FBF6", fg=BRAND_GREEN_DARK, font=(FONT, 22, "bold"))
        self.total_label.pack(anchor="e", padx=10, pady=(4, 0))
        ttk.Button(card, text="Pagar pedido", style="Primary.TButton", command=self.checkout).grid(row=6, column=0, sticky="ew")
        self._update_payment_state()

    def set_options(self, modalities: list[str], payments: list[str]):
        self.modality_combo["values"] = modalities
        self.payment_combo["values"] = payments
        if modalities:
            self.modality.set(modalities[0])
        if payments:
            self.payment.set(payments[0])
        self._update_address_state()
        self._update_payment_state()

    def set_cards(self, cards: list[dict]):
        self.cards = cards
        labels = ["Nueva tarjeta"]
        labels.extend(f"{card['alias']} ({card['marca']} ****{card['ultimos4']})" for card in cards)
        self.saved_card_combo["values"] = labels
        self.saved_card.set(labels[0])

    def set_cart(self, cart: dict[int, dict]):
        self.cart = cart
        self.render()

    def render(self):
        for row in self.tree.get_children():
            self.tree.delete(row)
        total = 0
        for product_id, item in self.cart.items():
            line_total = item["cantidad"] * item["precio_venta"]
            total += line_total
            self.tree.insert("", "end", iid=str(product_id), values=(item["nombre"], item["cantidad"], money(line_total)))
        self.total_label.configure(text=money(total))

    def checkout(self):
        if self.modality.get() == "Pedido a domicilio" and not self.address.get().strip():
            messagebox.showwarning("Direccion requerida", "Ingresa una direccion para pedido a domicilio.")
            return
        payment_data = {}
        if self.payment.get() == "Tarjeta":
            selected_card_id = self._selected_card_id()
            clean_number = "".join(ch for ch in self.card_number.get() if ch.isdigit())
            if selected_card_id:
                if not self.card_cvv.get().strip():
                    messagebox.showwarning("Pago con tarjeta", "Ingresa el CVV de la tarjeta seleccionada.")
                    return
            elif len(clean_number) < 12 or not self.card_holder.get().strip() or not self.card_expiry.get().strip() or not self.card_cvv.get().strip():
                messagebox.showwarning("Pago con tarjeta", "Completa los datos de la tarjeta.")
                return
            payment_data = {
                "saved_card_id": selected_card_id,
                "numero": self.card_number.get().strip(),
                "titular": self.card_holder.get().strip(),
                "vencimiento": self.card_expiry.get().strip(),
                "cvv": self.card_cvv.get().strip(),
                "guardar": self.save_card.get() and not selected_card_id,
            }
        self.checkout_callback(self.modality.get(), self.payment.get(), self.address.get().strip(), payment_data)

    def _update_address_state(self):
        if self.modality.get() == "Pedido a domicilio":
            self.address_entry.configure(state="normal")
        else:
            self.address.set("")
            self.address_entry.configure(state="disabled")

    def _update_payment_state(self):
        if self.payment.get() == "Tarjeta":
            self.card_frame.grid()
        else:
            self.card_frame.grid_remove()

    def _selected_card_id(self):
        selected = self.saved_card.get()
        for card in self.cards:
            label = f"{card['alias']} ({card['marca']} ****{card['ultimos4']})"
            if selected == label:
                return card["id"]
        return None

    def _load_selected_card(self):
        selected = self.saved_card.get()
        if selected == "Nueva tarjeta":
            self.card_number.set("")
            self.card_holder.set("")
            self.card_expiry.set("")
            return
        for card in self.cards:
            label = f"{card['alias']} ({card['marca']} ****{card['ultimos4']})"
            if selected == label:
                self.card_number.set(f"**** **** **** {card['ultimos4']}")
                self.card_holder.set(card["titular"])
                self.card_expiry.set(card["vencimiento"])
                self.save_card.set(False)
                return
