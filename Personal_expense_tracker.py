"""
╔══════════════════════════════════════════════════════════════════╗
║           PERSONAL EXPENSE TRACKER - GUI Application             ║
║     Features: Tkinter GUI | JSON Storage | Charts | Budget       ║
╚══════════════════════════════════════════════════════════════════╝
Requirements:
    pip install matplotlib tkcalendar
"""

import tkinter as tk
from tkinter import ttk, messagebox, filedialog
import json
import os
from datetime import datetime, date
import matplotlib.pyplot as plt
import matplotlib.patches as mpatches
from matplotlib.backends.backend_tkagg import FigureCanvasTkAgg
from matplotlib.figure import Figure
import calendar

# ─────────────────────────────────────────────────────────────────
#  CONSTANTS & CONFIG
# ─────────────────────────────────────────────────────────────────
DATA_FILE = "expenses.json"
BUDGET_FILE = "budget.json"

CATEGORIES = [
    "🍔 Food & Dining",
    "🚗 Transport",
    "🏠 Housing & Rent",
    "💡 Utilities",
    "🎬 Entertainment",
    "🛍️ Shopping",
    "💊 Healthcare",
    "📚 Education",
    "✈️ Travel",
    "💼 Business",
    "🎁 Gifts",
    "📦 Other",
]

CATEGORY_COLORS = {
    "🍔 Food & Dining":   "#FF6B6B",
    "🚗 Transport":       "#4ECDC4",
    "🏠 Housing & Rent":  "#45B7D1",
    "💡 Utilities":       "#96CEB4",
    "🎬 Entertainment":   "#FFEAA7",
    "🛍️ Shopping":        "#DDA0DD",
    "💊 Healthcare":      "#98FB98",
    "📚 Education":       "#F0E68C",
    "✈️ Travel":          "#87CEEB",
    "💼 Business":        "#FFA07A",
    "🎁 Gifts":           "#FFB6C1",
    "📦 Other":           "#C0C0C0",
}

# ─────────────────────────────────────────────────────────────────
#  DARK THEME PALETTE
# ─────────────────────────────────────────────────────────────────
BG_DARK    = "#0F1117"
BG_CARD    = "#1A1D2E"
BG_SURFACE = "#252842"
ACCENT     = "#6C63FF"
ACCENT2    = "#FF6584"
TEXT_PRI   = "#EAEAEA"
TEXT_SEC   = "#8B8FA8"
SUCCESS    = "#43D9A2"
WARNING    = "#FFB74D"
DANGER     = "#FF5252"
BORDER     = "#2E3150"


# ─────────────────────────────────────────────────────────────────
#  DATA MANAGER
# ─────────────────────────────────────────────────────────────────
class DataManager:
    def __init__(self):
        self.expenses = []
        self.budgets = {}
        self.load_expenses()
        self.load_budgets()

    def load_expenses(self):
        if os.path.exists(DATA_FILE):
            try:
                with open(DATA_FILE, "r") as f:
                    self.expenses = json.load(f)
            except (json.JSONDecodeError, IOError):
                self.expenses = []
        else:
            self.expenses = []

    def save_expenses(self):
        with open(DATA_FILE, "w") as f:
            json.dump(self.expenses, f, indent=4)

    def load_budgets(self):
        if os.path.exists(BUDGET_FILE):
            try:
                with open(BUDGET_FILE, "r") as f:
                    self.budgets = json.load(f)
            except (json.JSONDecodeError, IOError):
                self.budgets = {}
        else:
            self.budgets = {}

    def save_budgets(self):
        with open(BUDGET_FILE, "w") as f:
            json.dump(self.budgets, f, indent=4)

    def add_expense(self, amount, category, description, date_str):
        expense = {
            "id": int(datetime.now().timestamp() * 1000),
            "amount": float(amount),
            "category": category,
            "description": description,
            "date": date_str,
            "created_at": datetime.now().isoformat()
        }
        self.expenses.append(expense)
        self.save_expenses()
        return expense

    def delete_expense(self, expense_id):
        self.expenses = [e for e in self.expenses if e["id"] != expense_id]
        self.save_expenses()

    def update_expense(self, expense_id, amount, category, description, date_str):
        for e in self.expenses:
            if e["id"] == expense_id:
                e["amount"] = float(amount)
                e["category"] = category
                e["description"] = description
                e["date"] = date_str
                break
        self.save_expenses()

    def get_today_expenses(self):
        today = date.today().isoformat()
        return [e for e in self.expenses if e["date"] == today]

    def get_month_expenses(self, year=None, month=None):
        if year is None:
            year = date.today().year
        if month is None:
            month = date.today().month
        prefix = f"{year:04d}-{month:02d}"
        return [e for e in self.expenses if e["date"].startswith(prefix)]

    def get_expenses_by_date_range(self, start, end):
        return [e for e in self.expenses if start <= e["date"] <= end]

    def get_total(self, expense_list):
        return sum(e["amount"] for e in expense_list)

    def get_category_totals(self, expense_list):
        totals = {}
        for e in expense_list:
            cat = e["category"]
            totals[cat] = totals.get(cat, 0) + e["amount"]
        return totals

    def set_budget(self, category, amount):
        self.budgets[category] = float(amount)
        self.save_budgets()

    def get_budget(self, category):
        return self.budgets.get(category, 0.0)

    def export_to_json(self, filepath):
        with open(filepath, "w") as f:
            json.dump({
                "expenses": self.expenses,
                "budgets": self.budgets,
                "exported_at": datetime.now().isoformat()
            }, f, indent=4)


# ─────────────────────────────────────────────────────────────────
#  STYLED WIDGETS
# ─────────────────────────────────────────────────────────────────
def styled_frame(parent, **kwargs):
    defaults = {"bg": BG_CARD, "relief": "flat", "bd": 0}
    defaults.update(kwargs)
    return tk.Frame(parent, **defaults)

def styled_label(parent, text="", font_size=11, bold=False, color=TEXT_PRI, **kwargs):
    weight = "bold" if bold else "normal"
    defaults = {"bg": BG_CARD, "fg": color,
                "font": ("Segoe UI", font_size, weight), "text": text}
    defaults.update(kwargs)
    return tk.Label(parent, **defaults)

def styled_entry(parent, **kwargs):
    e = tk.Entry(parent,
                 bg=BG_SURFACE, fg=TEXT_PRI,
                 insertbackground=TEXT_PRI,
                 relief="flat", bd=8,
                 font=("Segoe UI", 11),
                 **kwargs)
    return e

def styled_button(parent, text, command, color=ACCENT, text_color="white",
                  width=None, font_size=10):
    btn_kwargs = dict(
        text=text, command=command,
        bg=color, fg=text_color,
        relief="flat", bd=0,
        font=("Segoe UI", font_size, "bold"),
        cursor="hand2",
        activebackground=color,
        activeforeground=text_color,
        padx=16, pady=8,
    )
    if width:
        btn_kwargs["width"] = width
    btn = tk.Button(parent, **btn_kwargs)

    def on_enter(e):
        btn.config(bg=_lighten(color))
    def on_leave(e):
        btn.config(bg=color)

    btn.bind("<Enter>", on_enter)
    btn.bind("<Leave>", on_leave)
    return btn

def _lighten(hex_color):
    """Return slightly lighter version of a hex color."""
    try:
        h = hex_color.lstrip("#")
        r, g, b = int(h[0:2],16), int(h[2:4],16), int(h[4:6],16)
        r = min(255, r + 30)
        g = min(255, g + 30)
        b = min(255, b + 30)
        return f"#{r:02x}{g:02x}{b:02x}"
    except Exception:
        return hex_color


# ─────────────────────────────────────────────────────────────────
#  MAIN APPLICATION
# ─────────────────────────────────────────────────────────────────
class ExpenseTrackerApp:
    def __init__(self, root):
        self.root = root
        self.root.title("💰 Personal Expense Tracker")
        self.root.geometry("1280x800")
        self.root.minsize(1100, 700)
        self.root.configure(bg=BG_DARK)

        self.data = DataManager()
        self.selected_expense_id = None

        self._configure_styles()
        self._build_ui()
        self._refresh_all()

    # ── TTK Styles ──────────────────────────────────────────────
    def _configure_styles(self):
        style = ttk.Style()
        style.theme_use("clam")

        style.configure("Dark.TNotebook",
                        background=BG_DARK, borderwidth=0)
        style.configure("Dark.TNotebook.Tab",
                        background=BG_SURFACE, foreground=TEXT_SEC,
                        padding=[20, 10], font=("Segoe UI", 10, "bold"),
                        borderwidth=0)
        style.map("Dark.TNotebook.Tab",
                  background=[("selected", ACCENT)],
                  foreground=[("selected", "white")])

        style.configure("Treeview",
                        background=BG_SURFACE, fieldbackground=BG_SURFACE,
                        foreground=TEXT_PRI, rowheight=32,
                        font=("Segoe UI", 10), borderwidth=0)
        style.configure("Treeview.Heading",
                        background=BG_DARK, foreground=ACCENT,
                        font=("Segoe UI", 10, "bold"), relief="flat")
        style.map("Treeview",
                  background=[("selected", ACCENT)],
                  foreground=[("selected", "white")])

        style.configure("TCombobox",
                        fieldbackground=BG_SURFACE, background=BG_SURFACE,
                        foreground=TEXT_PRI, arrowcolor=ACCENT,
                        borderwidth=0, relief="flat",
                        font=("Segoe UI", 11))
        style.map("TCombobox",
                  fieldbackground=[("readonly", BG_SURFACE)],
                  selectbackground=[("readonly", BG_SURFACE)],
                  selectforeground=[("readonly", TEXT_PRI)])

        style.configure("Vertical.TScrollbar",
                        background=BG_SURFACE, troughcolor=BG_DARK,
                        arrowcolor=ACCENT, borderwidth=0)
        style.configure("Horizontal.TProgressbar",
                        background=ACCENT, troughcolor=BG_SURFACE,
                        borderwidth=0, thickness=12)
        style.configure("Warning.Horizontal.TProgressbar",
                        background=WARNING, troughcolor=BG_SURFACE,
                        borderwidth=0, thickness=12)
        style.configure("Danger.Horizontal.TProgressbar",
                        background=DANGER, troughcolor=BG_SURFACE,
                        borderwidth=0, thickness=12)

    # ── Master Layout ─────────────────────────────────────────────
    def _build_ui(self):
        # ── Top Header ──
        header = tk.Frame(self.root, bg=BG_CARD, height=64)
        header.pack(fill="x", side="top")
        header.pack_propagate(False)

        tk.Label(header, text="💰 Personal Expense Tracker",
                 bg=BG_CARD, fg=TEXT_PRI,
                 font=("Segoe UI", 18, "bold")).pack(side="left", padx=24, pady=12)

        # Today's total in header
        self.header_today_var = tk.StringVar(value="Today: $0.00")
        tk.Label(header, textvariable=self.header_today_var,
                 bg=BG_CARD, fg=SUCCESS,
                 font=("Segoe UI", 12, "bold")).pack(side="right", padx=20)

        self.header_month_var = tk.StringVar(value="This Month: $0.00")
        tk.Label(header, textvariable=self.header_month_var,
                 bg=BG_CARD, fg=ACCENT,
                 font=("Segoe UI", 12, "bold")).pack(side="right", padx=20)

        # ── Notebook (Tabs) ──
        self.notebook = ttk.Notebook(self.root, style="Dark.TNotebook")
        self.notebook.pack(fill="both", expand=True, padx=10, pady=(6, 10))

        # Tab pages
        self.tab_dashboard  = tk.Frame(self.notebook, bg=BG_DARK)
        self.tab_add        = tk.Frame(self.notebook, bg=BG_DARK)
        self.tab_list       = tk.Frame(self.notebook, bg=BG_DARK)
        self.tab_charts     = tk.Frame(self.notebook, bg=BG_DARK)
        self.tab_budget     = tk.Frame(self.notebook, bg=BG_DARK)

        self.notebook.add(self.tab_dashboard, text="  📊 Dashboard  ")
        self.notebook.add(self.tab_add,       text="  ➕ Add Expense  ")
        self.notebook.add(self.tab_list,      text="  📋 All Expenses  ")
        self.notebook.add(self.tab_charts,    text="  📈 Charts  ")
        self.notebook.add(self.tab_budget,    text="  🎯 Budget  ")

        self.notebook.bind("<<NotebookTabChanged>>", self._on_tab_change)

        self._build_dashboard()
        self._build_add_tab()
        self._build_list_tab()
        self._build_charts_tab()
        self._build_budget_tab()

    # ─────────────────────────────────────────────────────────────
    #  TAB 1 – DASHBOARD
    # ─────────────────────────────────────────────────────────────
    def _build_dashboard(self):
        p = self.tab_dashboard
        p.columnconfigure(0, weight=1)
        p.columnconfigure(1, weight=1)
        p.columnconfigure(2, weight=1)
        p.rowconfigure(1, weight=1)

        # ── Summary Cards Row ──
        cards_frame = tk.Frame(p, bg=BG_DARK)
        cards_frame.grid(row=0, column=0, columnspan=3, sticky="ew", padx=16, pady=(16,8))
        for i in range(4):
            cards_frame.columnconfigure(i, weight=1)

        card_data = [
            ("Today's Spending",   "self.dash_today_var",    ACCENT2, "📅"),
            ("This Month",         "self.dash_month_var",    ACCENT,  "📆"),
            ("Total Expenses",     "self.dash_total_var",    SUCCESS, "💳"),
            ("Largest Today",      "self.dash_largest_var",  WARNING, "🔝"),
        ]

        self.dash_today_var   = tk.StringVar(value="$0.00")
        self.dash_month_var   = tk.StringVar(value="$0.00")
        self.dash_total_var   = tk.StringVar(value="$0.00")
        self.dash_largest_var = tk.StringVar(value="$0.00")

        vars_list = [self.dash_today_var, self.dash_month_var,
                     self.dash_total_var, self.dash_largest_var]

        for i, (title, _, color, icon) in enumerate(card_data):
            card = tk.Frame(cards_frame, bg=BG_CARD, relief="flat")
            card.grid(row=0, column=i, sticky="nsew", padx=6, pady=4)
            card.columnconfigure(0, weight=1)

            tk.Label(card, text=icon + "  " + title,
                     bg=BG_CARD, fg=TEXT_SEC,
                     font=("Segoe UI", 9, "bold")).grid(row=0, column=0, sticky="w", padx=16, pady=(14,0))
            tk.Label(card, textvariable=vars_list[i],
                     bg=BG_CARD, fg=color,
                     font=("Segoe UI", 22, "bold")).grid(row=1, column=0, sticky="w", padx=16, pady=(4,14))

        # ── Today's Expenses Table ──
        left_card = tk.Frame(p, bg=BG_CARD)
        left_card.grid(row=1, column=0, columnspan=2, sticky="nsew", padx=(16,6), pady=8)
        left_card.rowconfigure(1, weight=1)
        left_card.columnconfigure(0, weight=1)

        tk.Label(left_card, text="📅  Today's Expenses",
                 bg=BG_CARD, fg=TEXT_PRI,
                 font=("Segoe UI", 12, "bold")).grid(row=0, column=0, sticky="w", padx=16, pady=(14,6))

        cols = ("Time", "Category", "Description", "Amount")
        self.today_tree = ttk.Treeview(left_card, columns=cols, show="headings",
                                        selectmode="browse", height=12)
        for col in cols:
            self.today_tree.heading(col, text=col)
        self.today_tree.column("Time",        width=80,  anchor="center")
        self.today_tree.column("Category",    width=160, anchor="w")
        self.today_tree.column("Description", width=220, anchor="w")
        self.today_tree.column("Amount",      width=100, anchor="e")
        self.today_tree.grid(row=1, column=0, sticky="nsew", padx=10, pady=(0,10))

        sb = ttk.Scrollbar(left_card, orient="vertical", command=self.today_tree.yview)
        sb.grid(row=1, column=1, sticky="ns", pady=(0,10))
        self.today_tree.configure(yscrollcommand=sb.set)

        # ── Mini Pie Chart ──
        right_card = tk.Frame(p, bg=BG_CARD)
        right_card.grid(row=1, column=2, sticky="nsew", padx=(6,16), pady=8)
        right_card.rowconfigure(1, weight=1)
        right_card.columnconfigure(0, weight=1)

        tk.Label(right_card, text="📊  This Month by Category",
                 bg=BG_CARD, fg=TEXT_PRI,
                 font=("Segoe UI", 12, "bold")).grid(row=0, column=0, sticky="w", padx=16, pady=(14,6))

        self.dash_fig = Figure(figsize=(3.8, 3.8), facecolor=BG_CARD)
        self.dash_ax  = self.dash_fig.add_subplot(111)
        self.dash_canvas = FigureCanvasTkAgg(self.dash_fig, master=right_card)
        self.dash_canvas.get_tk_widget().grid(row=1, column=0, sticky="nsew", padx=8, pady=(0,8))

    # ─────────────────────────────────────────────────────────────
    #  TAB 2 – ADD / EDIT EXPENSE
    # ─────────────────────────────────────────────────────────────
    def _build_add_tab(self):
        p = self.tab_add

        # Scrollable canvas so nothing ever hides
        canvas = tk.Canvas(p, bg=BG_DARK, highlightthickness=0)
        canvas.pack(fill="both", expand=True)

        # Center card directly inside tab (no place/no scroll needed)
        card = tk.Frame(p, bg=BG_CARD, padx=40, pady=30)
        card.place(relx=0.5, rely=0.02, anchor="n")   # anchored to TOP so it never goes off screen

        # ── Title ──
        tk.Label(card, text="➕  Add New Expense",
                 bg=BG_CARD, fg=TEXT_PRI,
                 font=("Segoe UI", 16, "bold")).grid(row=0, column=0, columnspan=2,
                                                      sticky="w", pady=(0, 4))
        tk.Frame(card, bg=ACCENT, height=2, width=480).grid(row=1, column=0, columnspan=2,
                                                             sticky="ew", pady=(0, 18))

        # ── Helper to make a label+entry row ──
        def field_row(r, icon_label, widget):
            tk.Label(card, text=icon_label,
                     bg=BG_CARD, fg=TEXT_SEC,
                     font=("Segoe UI", 10, "bold"),
                     anchor="w", width=16).grid(row=r, column=0, sticky="w", pady=8)
            widget.grid(row=r, column=1, sticky="ew", pady=8, ipady=5)

        card.columnconfigure(1, weight=1, minsize=300)

        # Amount
        self.add_amount = styled_entry(card)
        field_row(2, "💵  Amount ($)", self.add_amount)

        # Category
        self.add_category = ttk.Combobox(card, values=CATEGORIES,
                                          state="readonly", font=("Segoe UI", 11))
        self.add_category.current(0)
        field_row(3, "🏷️   Category", self.add_category)

        # Description
        self.add_desc = styled_entry(card)
        field_row(4, "📝  Description", self.add_desc)

        # Date row
        tk.Label(card, text="📅  Date",
                 bg=BG_CARD, fg=TEXT_SEC,
                 font=("Segoe UI", 10, "bold"),
                 anchor="w", width=16).grid(row=5, column=0, sticky="w", pady=8)

        date_inner = tk.Frame(card, bg=BG_CARD)
        date_inner.grid(row=5, column=1, sticky="ew", pady=8)

        self.add_date = styled_entry(date_inner, width=14)
        self.add_date.insert(0, date.today().isoformat())
        self.add_date.pack(side="left", ipady=5)

        tk.Label(date_inner, text="  YYYY-MM-DD",
                 bg=BG_CARD, fg=TEXT_SEC,
                 font=("Segoe UI", 9)).pack(side="left")

        tk.Button(date_inner, text="📅 Today",
                  command=self._set_today_date,
                  bg=ACCENT, fg="white",
                  font=("Segoe UI", 9, "bold"),
                  relief="flat", cursor="hand2",
                  padx=10, pady=3).pack(side="left", padx=(10, 0))

        # Edit mode label
        self.edit_id = None
        self.add_mode_label = tk.StringVar(value="")
        tk.Label(card, textvariable=self.add_mode_label,
                 bg=BG_CARD, fg=WARNING,
                 font=("Segoe UI", 9)).grid(row=6, column=0, columnspan=2, pady=(4, 0))

        # ── SAVE & CLEAR BUTTONS ── always visible
        btn_frame = tk.Frame(card, bg=BG_CARD)
        btn_frame.grid(row=7, column=0, columnspan=2, sticky="ew", pady=(20, 0))

        self.save_btn = tk.Button(btn_frame,
                                   text="  💾  Save Expense  ",
                                   command=self._save_expense,
                                   bg=SUCCESS, fg=BG_DARK,
                                   font=("Segoe UI", 12, "bold"),
                                   relief="flat", cursor="hand2",
                                   padx=20, pady=12)
        self.save_btn.pack(side="left", padx=(0, 12))

        tk.Button(btn_frame,
                  text="  🗑️  Clear Form  ",
                  command=self._clear_add_form,
                  bg=BG_SURFACE, fg=TEXT_SEC,
                  font=("Segoe UI", 12, "bold"),
                  relief="flat", cursor="hand2",
                  padx=20, pady=12).pack(side="left")

    def _set_today_date(self):
        self.add_date.delete(0, tk.END)
        self.add_date.insert(0, date.today().isoformat())

    # ─────────────────────────────────────────────────────────────
    #  TAB 3 – ALL EXPENSES LIST
    # ─────────────────────────────────────────────────────────────
    def _build_list_tab(self):
        p = self.tab_list

        # ── Filter Bar ──
        filter_bar = tk.Frame(p, bg=BG_CARD)
        filter_bar.pack(fill="x", padx=12, pady=(12,0))

        tk.Label(filter_bar, text="🔍 Filter:", bg=BG_CARD, fg=TEXT_SEC,
                 font=("Segoe UI", 10, "bold")).pack(side="left", padx=(14,6), pady=10)

        tk.Label(filter_bar, text="From:", bg=BG_CARD, fg=TEXT_SEC,
                 font=("Segoe UI", 10)).pack(side="left")
        self.filter_from = styled_entry(filter_bar, width=12)
        self.filter_from.insert(0, f"{date.today().year}-01-01")
        self.filter_from.pack(side="left", padx=4, ipady=3)

        tk.Label(filter_bar, text="To:", bg=BG_CARD, fg=TEXT_SEC,
                 font=("Segoe UI", 10)).pack(side="left", padx=(8,0))
        self.filter_to = styled_entry(filter_bar, width=12)
        self.filter_to.insert(0, date.today().isoformat())
        self.filter_to.pack(side="left", padx=4, ipady=3)

        tk.Label(filter_bar, text="Category:", bg=BG_CARD, fg=TEXT_SEC,
                 font=("Segoe UI", 10)).pack(side="left", padx=(14,4))
        self.filter_cat = ttk.Combobox(filter_bar, values=["All"] + CATEGORIES,
                                        state="readonly", width=18,
                                        font=("Segoe UI", 10))
        self.filter_cat.current(0)
        self.filter_cat.pack(side="left", padx=4)

        styled_button(filter_bar, "  Apply Filter  ", self._apply_filter,
                      color=ACCENT, font_size=9).pack(side="left", padx=10)
        styled_button(filter_bar, "  Show All  ", self._load_all_expenses,
                      color=BG_SURFACE, text_color=TEXT_SEC, font_size=9).pack(side="left")

        # Export
        styled_button(filter_bar, "  📤 Export JSON  ", self._export_data,
                      color=BG_SURFACE, text_color=SUCCESS, font_size=9).pack(side="right", padx=14)

        # ── Treeview ──
        tree_frame = tk.Frame(p, bg=BG_DARK)
        tree_frame.pack(fill="both", expand=True, padx=12, pady=8)

        cols = ("ID", "Date", "Category", "Description", "Amount")
        self.list_tree = ttk.Treeview(tree_frame, columns=cols, show="headings",
                                       selectmode="browse")
        for col in cols:
            self.list_tree.heading(col, text=col,
                                   command=lambda c=col: self._sort_tree(c))
        self.list_tree.column("ID",          width=80,  anchor="center")
        self.list_tree.column("Date",        width=110, anchor="center")
        self.list_tree.column("Category",    width=180, anchor="w")
        self.list_tree.column("Description", width=300, anchor="w")
        self.list_tree.column("Amount",      width=110, anchor="e")

        vsb = ttk.Scrollbar(tree_frame, orient="vertical",   command=self.list_tree.yview)
        hsb = ttk.Scrollbar(tree_frame, orient="horizontal",  command=self.list_tree.xview)
        self.list_tree.configure(yscrollcommand=vsb.set, xscrollcommand=hsb.set)

        self.list_tree.grid(row=0, column=0, sticky="nsew")
        vsb.grid(row=0, column=1, sticky="ns")
        hsb.grid(row=1, column=0, sticky="ew")
        tree_frame.rowconfigure(0, weight=1)
        tree_frame.columnconfigure(0, weight=1)

        self.list_tree.bind("<<TreeviewSelect>>", self._on_list_select)

        # ── Action Bar ──
        action_bar = tk.Frame(p, bg=BG_CARD)
        action_bar.pack(fill="x", padx=12, pady=(0,10))

        styled_button(action_bar, "  ✏️ Edit Selected  ", self._edit_selected,
                      color=WARNING, text_color=BG_DARK, font_size=10).pack(side="left", padx=(14,8), pady=10)
        styled_button(action_bar, "  🗑️ Delete Selected  ", self._delete_selected,
                      color=DANGER, font_size=10).pack(side="left")

        self.list_total_var = tk.StringVar(value="Filtered Total: $0.00")
        tk.Label(action_bar, textvariable=self.list_total_var,
                 bg=BG_CARD, fg=SUCCESS,
                 font=("Segoe UI", 12, "bold")).pack(side="right", padx=20)

        self._sort_reverse = False
        self._sort_col = "Date"

    def _sort_tree(self, col):
        items = [(self.list_tree.set(k, col), k) for k in self.list_tree.get_children("")]
        try:
            items.sort(key=lambda x: float(x[0].replace("$","").replace(",","")),
                       reverse=self._sort_reverse)
        except ValueError:
            items.sort(reverse=self._sort_reverse)
        for idx, (_, k) in enumerate(items):
            self.list_tree.move(k, "", idx)
        self._sort_reverse = not self._sort_reverse

    # ─────────────────────────────────────────────────────────────
    #  TAB 4 – CHARTS
    # ─────────────────────────────────────────────────────────────
    def _build_charts_tab(self):
        p = self.tab_charts

        ctrl = tk.Frame(p, bg=BG_CARD)
        ctrl.pack(fill="x", padx=12, pady=(12,0))

        tk.Label(ctrl, text="📅 Month:", bg=BG_CARD, fg=TEXT_SEC,
                 font=("Segoe UI", 10, "bold")).pack(side="left", padx=(14,6), pady=10)

        months = [calendar.month_name[m] for m in range(1, 13)]
        self.chart_month = ttk.Combobox(ctrl, values=months, state="readonly", width=12)
        self.chart_month.current(date.today().month - 1)
        self.chart_month.pack(side="left", padx=4)

        years = [str(y) for y in range(date.today().year - 3, date.today().year + 1)]
        self.chart_year = ttk.Combobox(ctrl, values=years, state="readonly", width=8)
        self.chart_year.set(str(date.today().year))
        self.chart_year.pack(side="left", padx=4)

        styled_button(ctrl, "  🔄 Refresh Charts  ", self._refresh_charts,
                      color=ACCENT, font_size=9).pack(side="left", padx=12)

        # Chart area
        chart_frame = tk.Frame(p, bg=BG_DARK)
        chart_frame.pack(fill="both", expand=True, padx=12, pady=8)
        chart_frame.columnconfigure(0, weight=1)
        chart_frame.columnconfigure(1, weight=1)
        chart_frame.rowconfigure(0, weight=1)

        self.charts_fig = Figure(figsize=(13, 5.5), facecolor=BG_DARK)
        self.charts_canvas = FigureCanvasTkAgg(self.charts_fig, master=chart_frame)
        self.charts_canvas.get_tk_widget().pack(fill="both", expand=True)

    # ─────────────────────────────────────────────────────────────
    #  TAB 5 – BUDGET
    # ─────────────────────────────────────────────────────────────
    def _build_budget_tab(self):
        p = self.tab_budget

        header = tk.Frame(p, bg=BG_CARD)
        header.pack(fill="x", padx=12, pady=(12,0))
        tk.Label(header, text="🎯  Monthly Budget Planner",
                 bg=BG_CARD, fg=TEXT_PRI,
                 font=("Segoe UI", 14, "bold")).pack(side="left", padx=16, pady=12)
        tk.Label(header, text="Set spending limits per category and track your progress.",
                 bg=BG_CARD, fg=TEXT_SEC,
                 font=("Segoe UI", 10)).pack(side="left", padx=8)

        # Budget rows container
        canvas_frame = tk.Frame(p, bg=BG_DARK)
        canvas_frame.pack(fill="both", expand=True, padx=12, pady=8)

        canvas = tk.Canvas(canvas_frame, bg=BG_DARK, highlightthickness=0)
        scrollbar = ttk.Scrollbar(canvas_frame, orient="vertical", command=canvas.yview)
        self.budget_scroll_frame = tk.Frame(canvas, bg=BG_DARK)

        self.budget_scroll_frame.bind(
            "<Configure>",
            lambda e: canvas.configure(scrollregion=canvas.bbox("all"))
        )

        canvas.create_window((0, 0), window=self.budget_scroll_frame, anchor="nw")
        canvas.configure(yscrollcommand=scrollbar.set)

        canvas.pack(side="left", fill="both", expand=True)
        scrollbar.pack(side="right", fill="y")

        self.budget_widgets = {}
        self._build_budget_rows()

    def _build_budget_rows(self):
        for widget in self.budget_scroll_frame.winfo_children():
            widget.destroy()
        self.budget_widgets = {}

        for cat in CATEGORIES:
            color = CATEGORY_COLORS.get(cat, ACCENT)
            row_card = tk.Frame(self.budget_scroll_frame, bg=BG_CARD)
            row_card.pack(fill="x", padx=8, pady=4)
            row_card.columnconfigure(2, weight=1)

            # Category name
            tk.Label(row_card, text=cat,
                     bg=BG_CARD, fg=TEXT_PRI,
                     font=("Segoe UI", 10, "bold"),
                     width=22, anchor="w").grid(row=0, column=0, padx=(16,8), pady=12, sticky="w")

            # Budget entry
            entry = styled_entry(row_card, width=10)
            bval = self.data.get_budget(cat)
            entry.insert(0, f"{bval:.2f}" if bval else "")
            entry.grid(row=0, column=1, padx=8, pady=10, ipady=3)

            tk.Label(row_card, text="$", bg=BG_CARD, fg=TEXT_SEC,
                     font=("Segoe UI", 10)).grid(row=0, column=1, sticky="w", padx=(8,0))

            save_b = tk.Button(row_card, text="Set",
                               bg=ACCENT, fg="white",
                               font=("Segoe UI", 9, "bold"),
                               relief="flat", cursor="hand2",
                               padx=8, pady=3,
                               command=lambda c=cat, e=entry: self._set_budget(c, e))
            save_b.grid(row=0, column=2, padx=4, sticky="w")

            # Progress bar + labels
            spent = sum(e["amount"] for e in self.data.get_month_expenses()
                        if e["category"] == cat)
            budget = self.data.get_budget(cat)

            progress_frame = tk.Frame(row_card, bg=BG_CARD)
            progress_frame.grid(row=0, column=3, padx=16, sticky="ew")
            row_card.columnconfigure(3, weight=1)

            if budget > 0:
                pct = min(spent / budget, 1.0)
                pct_text = f"{pct*100:.0f}%"
                bar_style = ("Danger.Horizontal.TProgressbar" if pct >= 1.0
                             else "Warning.Horizontal.TProgressbar" if pct >= 0.8
                             else "Horizontal.TProgressbar")
                bar = ttk.Progressbar(progress_frame, length=200,
                                       maximum=budget,
                                       value=spent,
                                       style=bar_style)
                bar.pack(side="left", padx=(0,8))
                bar_color = (DANGER if pct >= 1.0 else WARNING if pct >= 0.8 else SUCCESS)
                tk.Label(progress_frame,
                         text=f"${spent:.2f} / ${budget:.2f}  ({pct_text})",
                         bg=BG_CARD, fg=bar_color,
                         font=("Segoe UI", 9, "bold")).pack(side="left")
            else:
                tk.Label(progress_frame,
                         text=f"${spent:.2f} spent  (no budget set)",
                         bg=BG_CARD, fg=TEXT_SEC,
                         font=("Segoe UI", 9)).pack(side="left")

            self.budget_widgets[cat] = entry

    # ─────────────────────────────────────────────────────────────
    #  ACTIONS
    # ─────────────────────────────────────────────────────────────
    def _save_expense(self):
        amt_str = self.add_amount.get().strip()
        cat     = self.add_category.get()
        desc    = self.add_desc.get().strip()
        dt      = self.add_date.get().strip()

        # Validate
        if not amt_str:
            messagebox.showerror("Validation Error", "Please enter an amount.")
            return
        try:
            amt = float(amt_str)
            if amt <= 0:
                raise ValueError
        except ValueError:
            messagebox.showerror("Validation Error", "Amount must be a positive number.")
            return

        try:
            datetime.strptime(dt, "%Y-%m-%d")
        except ValueError:
            messagebox.showerror("Validation Error", "Date must be in YYYY-MM-DD format.")
            return

        if self.edit_id is not None:
            self.data.update_expense(self.edit_id, amt, cat, desc, dt)
            messagebox.showinfo("Updated", "Expense updated successfully! ✅")
            self.edit_id = None
            self.add_mode_label.set("")
            self.save_btn.config(text="  💾 Save Expense  ")
        else:
            self.data.add_expense(amt, cat, desc, dt)
            messagebox.showinfo("Saved", "Expense added successfully! ✅")

        self._clear_add_form()
        self._refresh_all()

    def _clear_add_form(self):
        self.add_amount.delete(0, tk.END)
        self.add_category.current(0)
        self.add_desc.delete(0, tk.END)
        self.add_date.delete(0, tk.END)
        self.add_date.insert(0, date.today().isoformat())
        self.edit_id = None
        self.add_mode_label.set("")
        self.save_btn.config(text="  💾 Save Expense  ")

    def _apply_filter(self):
        start = self.filter_from.get().strip()
        end   = self.filter_to.get().strip()
        cat   = self.filter_cat.get()
        filtered = self.data.get_expenses_by_date_range(start, end)
        if cat != "All":
            filtered = [e for e in filtered if e["category"] == cat]
        self._populate_list_tree(filtered)

    def _load_all_expenses(self):
        self._populate_list_tree(self.data.expenses)

    def _populate_list_tree(self, expense_list):
        self.list_tree.delete(*self.list_tree.get_children())
        total = 0
        for e in sorted(expense_list, key=lambda x: x["date"], reverse=True):
            self.list_tree.insert("", "end",
                                   values=(e["id"], e["date"], e["category"],
                                           e.get("description",""),
                                           f"${e['amount']:.2f}"))
            total += e["amount"]
        self.list_total_var.set(f"Filtered Total: ${total:.2f}")

    def _on_list_select(self, event):
        pass  # Selection highlight is auto-handled

    def _edit_selected(self):
        sel = self.list_tree.selection()
        if not sel:
            messagebox.showwarning("No Selection", "Please select an expense to edit.")
            return
        item = self.list_tree.item(sel[0])
        eid = item["values"][0]
        expense = next((e for e in self.data.expenses if e["id"] == eid), None)
        if not expense:
            return

        self.edit_id = eid
        self.add_amount.delete(0, tk.END)
        self.add_amount.insert(0, str(expense["amount"]))
        if expense["category"] in CATEGORIES:
            self.add_category.current(CATEGORIES.index(expense["category"]))
        self.add_desc.delete(0, tk.END)
        self.add_desc.insert(0, expense.get("description", ""))
        self.add_date.delete(0, tk.END)
        self.add_date.insert(0, expense["date"])
        self.add_mode_label.set(f"✏️ Editing expense ID: {eid}")
        self.save_btn.config(text="  ✅ Update Expense  ")
        self.notebook.select(self.tab_add)

    def _delete_selected(self):
        sel = self.list_tree.selection()
        if not sel:
            messagebox.showwarning("No Selection", "Please select an expense to delete.")
            return
        item = self.list_tree.item(sel[0])
        eid = item["values"][0]
        if messagebox.askyesno("Confirm Delete",
                                f"Delete expense #{eid}?\nThis cannot be undone."):
            self.data.delete_expense(eid)
            self._refresh_all()

    def _set_budget(self, category, entry_widget):
        val = entry_widget.get().strip()
        try:
            amt = float(val)
            self.data.set_budget(category, amt)
            self._build_budget_rows()
        except ValueError:
            messagebox.showerror("Error", "Please enter a valid number for budget.")

    def _export_data(self):
        fp = filedialog.asksaveasfilename(
            defaultextension=".json",
            filetypes=[("JSON files", "*.json"), ("All files", "*.*")],
            title="Export Expenses"
        )
        if fp:
            self.data.export_to_json(fp)
            messagebox.showinfo("Exported", f"Data exported to:\n{fp}")

    # ─────────────────────────────────────────────────────────────
    #  REFRESH & CHARTS
    # ─────────────────────────────────────────────────────────────
    def _refresh_all(self):
        self._refresh_dashboard()
        self._populate_list_tree(self.data.expenses)
        self._build_budget_rows()
        self._refresh_charts()

    def _refresh_dashboard(self):
        today_exp  = self.data.get_today_expenses()
        month_exp  = self.data.get_month_expenses()
        all_exp    = self.data.expenses

        today_total = self.data.get_total(today_exp)
        month_total = self.data.get_total(month_exp)
        all_total   = self.data.get_total(all_exp)
        largest_today = max((e["amount"] for e in today_exp), default=0)

        self.dash_today_var.set(f"${today_total:.2f}")
        self.dash_month_var.set(f"${month_total:.2f}")
        self.dash_total_var.set(f"${all_total:.2f}")
        self.dash_largest_var.set(f"${largest_today:.2f}")

        self.header_today_var.set(f"Today: ${today_total:.2f}")
        self.header_month_var.set(f"This Month: ${month_total:.2f}")

        # Today's table
        self.today_tree.delete(*self.today_tree.get_children())
        for e in sorted(today_exp, key=lambda x: x.get("created_at",""), reverse=True):
            t = e.get("created_at","")[:19].replace("T"," ")[11:16] if e.get("created_at") else ""
            self.today_tree.insert("", "end",
                                    values=(t, e["category"],
                                            e.get("description",""),
                                            f"${e['amount']:.2f}"))

        # Mini pie chart
        self.dash_ax.clear()
        cat_totals = self.data.get_category_totals(month_exp)
        if cat_totals:
            labels = list(cat_totals.keys())
            sizes  = list(cat_totals.values())
            colors = [CATEGORY_COLORS.get(l, ACCENT) for l in labels]
            short_labels = [l.split(" ",1)[1] if " " in l else l for l in labels]
            wedges, _, autotexts = self.dash_ax.pie(
                sizes, labels=None, colors=colors,
                autopct="%1.0f%%", startangle=90,
                pctdistance=0.78,
                wedgeprops={"linewidth":2, "edgecolor": BG_CARD}
            )
            for at in autotexts:
                at.set_color(BG_DARK)
                at.set_fontsize(7)
                at.set_fontweight("bold")
            self.dash_ax.set_facecolor(BG_CARD)
            self.dash_ax.axis("equal")
            self.dash_fig.patch.set_facecolor(BG_CARD)

            legend_patches = [mpatches.Patch(color=c, label=sl)
                              for c, sl in zip(colors, short_labels)]
            self.dash_ax.legend(handles=legend_patches,
                                loc="upper left", bbox_to_anchor=(-0.35, 1.0),
                                frameon=False,
                                labelcolor=TEXT_SEC,
                                fontsize=7.5)
        else:
            self.dash_ax.text(0.5, 0.5, "No data\nthis month",
                              ha="center", va="center",
                              transform=self.dash_ax.transAxes,
                              color=TEXT_SEC, fontsize=12)
            self.dash_ax.set_facecolor(BG_CARD)
            self.dash_fig.patch.set_facecolor(BG_CARD)
            self.dash_ax.axis("off")

        self.dash_canvas.draw()

    def _refresh_charts(self):
        month_idx = self.chart_month.current() + 1
        year      = int(self.chart_year.get())
        expenses  = self.data.get_month_expenses(year, month_idx)

        self.charts_fig.clear()
        self.charts_fig.patch.set_facecolor(BG_DARK)

        if not expenses:
            ax = self.charts_fig.add_subplot(111)
            ax.set_facecolor(BG_DARK)
            ax.text(0.5, 0.5, "No expenses found for the selected period.",
                    ha="center", va="center",
                    color=TEXT_SEC, fontsize=14)
            ax.axis("off")
            self.charts_canvas.draw()
            return

        ax1 = self.charts_fig.add_subplot(131)  # Pie
        ax2 = self.charts_fig.add_subplot(132)  # Bar by category
        ax3 = self.charts_fig.add_subplot(133)  # Daily trend

        for ax in [ax1, ax2, ax3]:
            ax.set_facecolor(BG_CARD)

        cat_totals = self.data.get_category_totals(expenses)
        labels = list(cat_totals.keys())
        sizes  = list(cat_totals.values())
        colors = [CATEGORY_COLORS.get(l, ACCENT) for l in labels]
        short  = [l.split(" ",1)[1] if " " in l else l for l in labels]

        # Pie
        wedges, _, autotexts = ax1.pie(
            sizes, labels=None, colors=colors,
            autopct="%1.1f%%", startangle=90,
            wedgeprops={"linewidth":2, "edgecolor": BG_DARK}
        )
        for at in autotexts:
            at.set_color("white")
            at.set_fontsize(7)
        ax1.set_title(f"{calendar.month_name[month_idx]} {year}\nSpending by Category",
                      color=TEXT_PRI, fontsize=10, fontweight="bold", pad=14)
        ax1.legend(wedges, short, loc="lower center",
                   bbox_to_anchor=(0.5, -0.18), ncol=2,
                   frameon=False, labelcolor=TEXT_SEC, fontsize=7)

        # Bar by category
        sorted_cats = sorted(zip(sizes, short, colors), reverse=True)
        s_sizes, s_labels, s_colors = zip(*sorted_cats)
        bars = ax2.barh(s_labels, s_sizes, color=s_colors,
                        edgecolor=BG_DARK, linewidth=1.5)
        for bar, val in zip(bars, s_sizes):
            ax2.text(bar.get_width() + max(s_sizes)*0.01, bar.get_y() + bar.get_height()/2,
                     f"${val:.0f}", va="center", ha="left",
                     color=TEXT_SEC, fontsize=8)
        ax2.set_facecolor(BG_CARD)
        ax2.tick_params(colors=TEXT_SEC, labelsize=8)
        ax2.spines[:].set_color(BORDER)
        ax2.set_title("Category Breakdown", color=TEXT_PRI, fontsize=10, fontweight="bold")
        ax2.xaxis.label.set_color(TEXT_SEC)
        ax2.set_xlabel("Amount ($)", color=TEXT_SEC, fontsize=9)

        # Daily trend
        days_in_month = calendar.monthrange(year, month_idx)[1]
        daily = {}
        for e in expenses:
            d = int(e["date"].split("-")[2])
            daily[d] = daily.get(d, 0) + e["amount"]

        x = list(range(1, days_in_month + 1))
        y = [daily.get(d, 0) for d in x]

        ax3.fill_between(x, y, alpha=0.25, color=ACCENT)
        ax3.plot(x, y, color=ACCENT, linewidth=2, marker="o",
                 markersize=4, markerfacecolor=ACCENT2)
        ax3.set_facecolor(BG_CARD)
        ax3.tick_params(colors=TEXT_SEC, labelsize=8)
        ax3.spines[:].set_color(BORDER)
        ax3.set_title("Daily Spending Trend", color=TEXT_PRI, fontsize=10, fontweight="bold")
        ax3.set_xlabel("Day of Month", color=TEXT_SEC, fontsize=9)
        ax3.set_ylabel("Amount ($)", color=TEXT_SEC, fontsize=9)
        ax3.xaxis.label.set_color(TEXT_SEC)

        self.charts_fig.tight_layout(pad=2.5)
        self.charts_canvas.draw()

    def _on_tab_change(self, event):
        tab = self.notebook.index(self.notebook.select())
        if tab == 3:
            self._refresh_charts()

    # ─────────────────────────────────────────────────────────────
    #  ENTRY POINT
    # ─────────────────────────────────────────────────────────────
    def run(self):
        self.root.mainloop()


# ─────────────────────────────────────────────────────────────────
#  MAIN
# ─────────────────────────────────────────────────────────────────
if __name__ == "__main__":
    root = tk.Tk()

    # Center window
    root.update_idletasks()
    w, h = 1280, 800
    sw = root.winfo_screenwidth()
    sh = root.winfo_screenheight()
    root.geometry(f"{w}x{h}+{(sw-w)//2}+{(sh-h)//2}")

    app = ExpenseTrackerApp(root)
    app.run()