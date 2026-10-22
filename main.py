from decimal import Decimal, ROUND_HALF_UP
import tkinter as tk
from tkinter import ttk, messagebox

MENU = {
    "Кофе": Decimal("3.50"),
    "Чай": Decimal("2.50"),
    "Бургер": Decimal("7.00"),
    "БургердеЛюкс": Decimal("9.00"),
    "Двойная картошка фри": Decimal("5.00"),
    "Мокачано": Decimal("6.00"),
    "Хот Дог": Decimal("4.00"),
    "Золотой Бургер XL Делюкс": Decimal("156.00"),
    "Картошка фри": Decimal("3.00"),
    "Лимонад": Decimal("2.00"),
    "Мороженное": Decimal("10.00")
}

PROMO_CODE = "TEEN10"
DISCOUNT_RATE = Decimal("0.10")

TIP_RATES = {
    "0%": Decimal("0"),
    "5%": Decimal("0.05"),
    "10%": Decimal("0.10"),
    "15%": Decimal("0.15"),
    "100%": Decimal("100"),
}


def money(amount):
    return amount.quantize(Decimal("0.01"), rounding=ROUND_HALF_UP)


class CafeApp:
    def __init__(self, root):
        self.root = root
        self.root.title("Касса кофейни")
        self.root.geometry("650x520")
        self.order = {}

        main_frame = ttk.Frame(root, padding=15)
        main_frame.pack(fill="both", expand=True)

        ttk.Label(
            main_frame,
            text="Касса кофейни",
            font=("Arial", 20, "bold"),
        ).pack(pady=(0, 12))

        content = ttk.Frame(main_frame)
        content.pack(fill="both", expand=True)

        menu_frame = ttk.LabelFrame(content, text="Меню", padding=10)
        menu_frame.pack(side="left", fill="y", padx=(0, 10))

        for item, price in MENU.items():
            row = ttk.Frame(menu_frame)
            row.pack(fill="x", pady=4)

            ttk.Label(row, text=f"{item} — {price:.2f} BYN").pack(side="left")
            ttk.Button(
                row,
                text="Добавить",
                command=lambda name=item: self.add_item(name),
            ).pack(side="right", padx=(10, 0))

        order_frame = ttk.LabelFrame(content, text="Заказ", padding=10)
        order_frame.pack(side="left", fill="both", expand=True)

        self.order_list = tk.Listbox(order_frame, height=12)
        self.order_list.pack(fill="both", expand=True)

        ttk.Button(
            order_frame,
            text="Убрать выбранное",
            command=self.remove_item,
        ).pack(fill="x", pady=(8, 0))

        options = ttk.Frame(main_frame)
        options.pack(fill="x", pady=12)

        ttk.Label(options, text="Промокод:").grid(
            row=0, column=0, sticky="w"
        )
        self.promo_entry = ttk.Entry(options, width=18)
        self.promo_entry.grid(row=0, column=1, padx=8, sticky="w")

        ttk.Label(options, text="Чаевые:").grid(
            row=0, column=2, padx=(15, 0)
        )
        self.tip_box = ttk.Combobox(
            options,
            values=list(TIP_RATES.keys()),
            state="readonly",
            width=7,
        )
        self.tip_box.set("0%")
        self.tip_box.grid(row=0, column=3, padx=8)

        ttk.Button(
            options,
            text="Рассчитать чек",
            command=self.show_receipt,
        ).grid(row=0, column=4, padx=(15, 0))

        self.total_label = ttk.Label(
            main_frame,
            text="Сумма заказа: 0.00 BYN",
            font=("Arial", 14, "bold"),
        )
        self.total_label.pack(anchor="e")

    def add_item(self, item):
        self.order[item] = self.order.get(item, 0) + 1
        self.refresh_order()

    def remove_item(self):
        selection = self.order_list.curselection()

        if not selection:
            messagebox.showinfo("Заказ", "Сначала выберите блюдо в списке.")
            return

        item = list(self.order.keys())[selection[0]]

        if self.order[item] > 1:
            self.order[item] -= 1
        else:
            del self.order[item]

        self.refresh_order()

    def refresh_order(self):
        self.order_list.delete(0, tk.END)
        subtotal = Decimal("0")

        for item, quantity in self.order.items():
            line_total = MENU[item] * quantity
            subtotal += line_total
            self.order_list.insert(
                tk.END,
                f"{item} × {quantity} — {line_total:.2f} BYN",
            )

        self.total_label.config(
            text=f"Сумма заказа: {money(subtotal):.2f} BYN"
        )

    def show_receipt(self):
        if not self.order:
            messagebox.showinfo("Чек", "Сначала добавьте что-нибудь в заказ.")
            return

        subtotal = sum(
            (
                MENU[item] * quantity
                for item, quantity in self.order.items()
            ),
            Decimal("0"),
        )

        promo = self.promo_entry.get().strip().upper()

        if promo == PROMO_CODE:
            discount = subtotal * DISCOUNT_RATE
        else:
            discount = Decimal("0")

        after_discount = subtotal - discount
        tip_rate = TIP_RATES[self.tip_box.get()]
        tips = after_discount * tip_rate
        total = money(after_discount + tips)

        receipt_items = [
            f"{item} × {quantity} — "
            f"{MENU[item] * quantity:.2f} BYN"
            for item, quantity in self.order.items()
        ]

        receipt = "\n".join(receipt_items)
        receipt += (
            f"\n\nСумма: {money(subtotal):.2f} BYN"
            f"\nСкидка: {money(discount):.2f} BYN"
            f"\nЧаевые: {money(tips):.2f} BYN"
            f"\nИтого: {total:.2f} BYN"
        )

        messagebox.showinfo("Чек", receipt)


if __name__ == "__main__":
    root = tk.Tk()
    app = CafeApp(root)
    root.mainloop()
