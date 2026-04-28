import tkinter as tk
from tkinter import ttk, messagebox
import threading

from calorie_calculator import ACTIVITY_LEVELS, GOALS
from meal_planner import generate_meal_plan, get_meal_breakdown

# ── Colour palette ────────────────────────────────────────────────────────────
BG          = "#0f1a0f"   # near-black green
CARD        = "#162416"   # card background
CARD2       = "#1c2e1c"   # slightly lighter card
BORDER      = "#2a3d2a"   # subtle border
ACCENT      = "#7ec44f"   # fresh lime green
ACCENT2     = "#a8d876"   # lighter lime
MUTED       = "#4a6b3a"   # muted green text
TEXT        = "#e8f0e0"   # warm cream text
TEXT2       = "#b0c4a0"   # secondary text
DANGER      = "#e05c5c"   # red for warnings
GOLD        = "#d4a843"   # warm gold for highlights

FONT_HEAD   = ("Georgia", 26, "bold")
FONT_SUB    = ("Georgia", 13, "italic")
FONT_LABEL  = ("Trebuchet MS", 10, "bold")
FONT_BODY   = ("Trebuchet MS", 10)
FONT_SMALL  = ("Trebuchet MS", 9)
FONT_MONO   = ("Courier New", 9)
FONT_BIG    = ("Georgia", 15, "bold")
FONT_NUM    = ("Courier New", 18, "bold")


class NutriGenApp(tk.Tk):
    def __init__(self):
        super().__init__()
        self.title("NutriGen — AI Diet Planner")
        self.geometry("900x680")
        self.minsize(860, 620)
        self.configure(bg=BG)
        self.resizable(True, True)

        # shared state
        self.result      = None
        self.ga_running  = False

        self._style()
        self._build_header()
        self._build_body()
        self._show_welcome()

    # ── Global ttk style ──────────────────────────────────────────────────────
    def _style(self):
        s = ttk.Style(self)
        s.theme_use("clam")
        s.configure("TFrame",       background=BG)
        s.configure("Card.TFrame",  background=CARD)
        s.configure("Card2.TFrame", background=CARD2)
        s.configure("TLabel",       background=BG,    foreground=TEXT,
                    font=FONT_BODY)
        s.configure("Card.TLabel",  background=CARD,  foreground=TEXT,
                    font=FONT_BODY)
        s.configure("Card2.TLabel", background=CARD2, foreground=TEXT,
                    font=FONT_BODY)
        s.configure("Accent.TLabel",background=BG,    foreground=ACCENT,
                    font=FONT_LABEL)
        s.configure("Muted.TLabel", background=CARD,  foreground=TEXT2,
                    font=FONT_SMALL)
        s.configure("TCombobox",    fieldbackground=CARD2, background=CARD2,
                    foreground=TEXT, selectbackground=MUTED,
                    selectforeground=TEXT)
        s.map("TCombobox",
              fieldbackground=[("readonly", CARD2)],
              foreground=[("readonly", TEXT)],
              selectbackground=[("readonly", MUTED)])
        s.configure("Horizontal.TScale", background=CARD,
                    troughcolor=BORDER, sliderthickness=16)
        s.configure("green.Horizontal.TProgressbar",
                    troughcolor=BORDER, background=ACCENT,
                    thickness=8)

    # ── Fixed header bar ──────────────────────────────────────────────────────
    def _build_header(self):
        bar = tk.Frame(self, bg=CARD, height=54)
        bar.pack(fill="x", side="top")
        bar.pack_propagate(False)

        tk.Label(bar, text="✦ NutriGen", bg=CARD, fg=ACCENT,
                 font=("Georgia", 16, "bold")).pack(side="left", padx=20, pady=12)
        tk.Label(bar, text="AI-Powered Halal Diet Planner", bg=CARD, fg=TEXT2,
                 font=FONT_SMALL).pack(side="left", padx=4, pady=12)

        self.nav_frame = tk.Frame(bar, bg=CARD)
        self.nav_frame.pack(side="right", padx=16)

        self.btn_home   = self._nav_btn("Home",    self._show_welcome)
        self.btn_form   = self._nav_btn("Plan",    self._show_form)
        self.btn_result = self._nav_btn("Results", self._show_results)
        self.btn_result.config(state="disabled")

        # divider
        tk.Frame(self, bg=BORDER, height=1).pack(fill="x")

    def _nav_btn(self, text, cmd):
        b = tk.Button(self.nav_frame, text=text, command=cmd,
                      bg=CARD, fg=TEXT2, font=FONT_SMALL,
                      relief="flat", bd=0, padx=12, pady=6,
                      activebackground=CARD2, activeforeground=ACCENT,
                      cursor="hand2")
        b.pack(side="left", padx=2)
        return b

    # ── Scrollable body area ──────────────────────────────────────────────────
    def _build_body(self):
        self.body = tk.Frame(self, bg=BG)
        self.body.pack(fill="both", expand=True)

    def _clear_body(self):
        for w in self.body.winfo_children():
            w.destroy()

    # ═══════════════════════════════════════════════════════════════════════════
    #  SCREEN 1 — WELCOME
    # ═══════════════════════════════════════════════════════════════════════════
    def _show_welcome(self):
        self._clear_body()
        self._set_nav(0)

        outer = tk.Frame(self.body, bg=BG)
        outer.place(relx=0.5, rely=0.5, anchor="center")

        # leaf decoration line
        tk.Label(outer, text="─── ✦ ───", bg=BG, fg=MUTED,
                 font=("Georgia", 14)).pack(pady=(0, 10))

        tk.Label(outer, text="NutriGen", bg=BG, fg=ACCENT,
                 font=("Georgia", 46, "bold")).pack()

        tk.Label(outer, text="Your AI-powered halal meal planner",
                 bg=BG, fg=TEXT2, font=FONT_SUB).pack(pady=(4, 6))

        tk.Label(outer, text="─── ✦ ───", bg=BG, fg=MUTED,
                 font=("Georgia", 14)).pack(pady=(0, 28))

        # three feature pills
        pill_row = tk.Frame(outer, bg=BG)
        pill_row.pack(pady=(0, 36))
        for txt in ["  ◈  Genetic Algorithm  ", "  ◈  182 Halal Foods  ", "  ◈  Macro Optimised  "]:
            tk.Label(pill_row, text=txt, bg=CARD, fg=ACCENT2,
                     font=FONT_SMALL, padx=10, pady=6,
                     relief="flat").pack(side="left", padx=6)

        self._green_btn(outer, "Generate My Diet Plan →", self._show_form,
                        big=True).pack(pady=4)

        tk.Label(outer, text="Powered by Genetic Algorithm optimisation",
                 bg=BG, fg=MUTED, font=FONT_SMALL).pack(pady=(14, 0))

    # ═══════════════════════════════════════════════════════════════════════════
    #  SCREEN 2 — INPUT FORM
    # ═══════════════════════════════════════════════════════════════════════════
    def _show_form(self):
        self._clear_body()
        self._set_nav(1)

        # scrollable canvas
        canvas = tk.Canvas(self.body, bg=BG, bd=0, highlightthickness=0)
        scroll = tk.Scrollbar(self.body, orient="vertical", command=canvas.yview)
        canvas.configure(yscrollcommand=scroll.set)
        scroll.pack(side="right", fill="y")
        canvas.pack(side="left", fill="both", expand=True)

        inner = tk.Frame(canvas, bg=BG)
        win_id = canvas.create_window((0, 0), window=inner, anchor="nw")

        def _resize(e):
            canvas.itemconfig(win_id, width=e.width)
        canvas.bind("<Configure>", _resize)
        inner.bind("<Configure>", lambda e: canvas.configure(
            scrollregion=canvas.bbox("all")))
        canvas.bind_all("<MouseWheel>",
                        lambda e: canvas.yview_scroll(-1*(e.delta//120), "units"))

        pad = tk.Frame(inner, bg=BG)
        pad.pack(fill="both", expand=True, padx=60, pady=24)

        self._section_title(pad, "◈  Personal Details")

        row1 = tk.Frame(pad, bg=BG)
        row1.pack(fill="x", pady=(0, 12))

        # Age
        age_card = self._card(row1)
        age_card.pack(side="left", fill="both", expand=True, padx=(0, 8))
        tk.Label(age_card, text="AGE  (years)", bg=CARD, fg=MUTED,
                 font=FONT_LABEL).pack(anchor="w", padx=14, pady=(12, 2))
        self.age_var = tk.IntVar(value=25)
        self.age_disp = tk.Label(age_card, textvariable=self.age_var,
                                  bg=CARD, fg=ACCENT, font=FONT_NUM)
        self.age_disp.pack(anchor="w", padx=14)
        ttk.Scale(age_card, from_=10, to=80, variable=self.age_var,
                  orient="horizontal",
                  command=lambda v: self.age_var.set(int(float(v)))
                  ).pack(fill="x", padx=14, pady=(0, 14))

        # Weight
        wt_card = self._card(row1)
        wt_card.pack(side="left", fill="both", expand=True, padx=(0, 8))
        tk.Label(wt_card, text="WEIGHT  (kg)", bg=CARD, fg=MUTED,
                 font=FONT_LABEL).pack(anchor="w", padx=14, pady=(12, 2))
        self.weight_var = tk.IntVar(value=70)
        tk.Label(wt_card, textvariable=self.weight_var,
                 bg=CARD, fg=ACCENT, font=FONT_NUM).pack(anchor="w", padx=14)
        ttk.Scale(wt_card, from_=30, to=180, variable=self.weight_var,
                  orient="horizontal",
                  command=lambda v: self.weight_var.set(int(float(v)))
                  ).pack(fill="x", padx=14, pady=(0, 14))

        # Height
        ht_card = self._card(row1)
        ht_card.pack(side="left", fill="both", expand=True)
        tk.Label(ht_card, text="HEIGHT  (cm)", bg=CARD, fg=MUTED,
                 font=FONT_LABEL).pack(anchor="w", padx=14, pady=(12, 2))
        self.height_var = tk.IntVar(value=170)
        tk.Label(ht_card, textvariable=self.height_var,
                 bg=CARD, fg=ACCENT, font=FONT_NUM).pack(anchor="w", padx=14)
        ttk.Scale(ht_card, from_=120, to=220, variable=self.height_var,
                  orient="horizontal",
                  command=lambda v: self.height_var.set(int(float(v)))
                  ).pack(fill="x", padx=14, pady=(0, 14))

        # Gender + Goal row
        self._section_title(pad, "◈  Goals & Activity")
        row2 = tk.Frame(pad, bg=BG)
        row2.pack(fill="x", pady=(0, 12))

        gc = self._card(row2)
        gc.pack(side="left", fill="both", expand=True, padx=(0, 8))
        tk.Label(gc, text="GENDER", bg=CARD, fg=MUTED,
                 font=FONT_LABEL).pack(anchor="w", padx=14, pady=(12, 6))
        self.gender_var = tk.StringVar(value="Male")
        gf = tk.Frame(gc, bg=CARD)
        gf.pack(anchor="w", padx=14, pady=(0, 14))
        for g in ("Male", "Female"):
            tk.Radiobutton(gf, text=g, variable=self.gender_var, value=g,
                           bg=CARD, fg=TEXT, selectcolor=MUTED,
                           activebackground=CARD, activeforeground=ACCENT,
                           font=FONT_BODY).pack(side="left", padx=(0, 16))

        goalc = self._card(row2)
        goalc.pack(side="left", fill="both", expand=True, padx=(0, 8))
        tk.Label(goalc, text="FITNESS GOAL", bg=CARD, fg=MUTED,
                 font=FONT_LABEL).pack(anchor="w", padx=14, pady=(12, 6))
        self.goal_var = tk.StringVar(value="Weight Loss")
        goal_cb = ttk.Combobox(goalc, textvariable=self.goal_var,
                               values=list(GOALS.keys()),
                               state="readonly", font=FONT_BODY)
        goal_cb.pack(fill="x", padx=14, pady=(0, 14))

        actc = self._card(row2)
        actc.pack(side="left", fill="both", expand=True)
        tk.Label(actc, text="ACTIVITY LEVEL", bg=CARD, fg=MUTED,
                 font=FONT_LABEL).pack(anchor="w", padx=14, pady=(12, 6))
        self.activity_var = tk.StringVar(
            value="Moderately Active (exercise 3-5 days/week)")
        act_cb = ttk.Combobox(actc, textvariable=self.activity_var,
                              values=list(ACTIVITY_LEVELS.keys()),
                              state="readonly", font=FONT_BODY, width=32)
        act_cb.pack(fill="x", padx=14, pady=(0, 14))

        # Food exclusions
        self._section_title(pad, "◈  Food Exclusions  (optional)")
        exc_card = self._card(pad)
        exc_card.pack(fill="x", pady=(0, 12))
        tk.Label(exc_card,
                 text="Enter food names to exclude, separated by commas  "
                      "(e.g.  Garlic, Bitter Gourd / Karela)",
                 bg=CARD, fg=TEXT2, font=FONT_SMALL
                 ).pack(anchor="w", padx=14, pady=(10, 4))
        self.excl_var = tk.StringVar()
        tk.Entry(exc_card, textvariable=self.excl_var,
                 bg=CARD2, fg=TEXT, insertbackground=ACCENT,
                 relief="flat", font=FONT_BODY,
                 highlightthickness=1, highlightbackground=BORDER,
                 highlightcolor=ACCENT
                 ).pack(fill="x", padx=14, pady=(0, 14))

        # GA settings
        self._section_title(pad, "◈  Algorithm Settings")
        row3 = tk.Frame(pad, bg=BG)
        row3.pack(fill="x", pady=(0, 20))

        gc2 = self._card(row3)
        gc2.pack(side="left", fill="both", expand=True, padx=(0, 8))
        tk.Label(gc2, text="GENERATIONS", bg=CARD, fg=MUTED,
                 font=FONT_LABEL).pack(anchor="w", padx=14, pady=(12, 2))
        self.gen_var = tk.IntVar(value=100)
        tk.Label(gc2, textvariable=self.gen_var,
                 bg=CARD, fg=ACCENT, font=FONT_NUM).pack(anchor="w", padx=14)
        ttk.Scale(gc2, from_=40, to=200, variable=self.gen_var,
                  orient="horizontal",
                  command=lambda v: self.gen_var.set(int(float(v)))
                  ).pack(fill="x", padx=14, pady=(0, 14))

        pc = self._card(row3)
        pc.pack(side="left", fill="both", expand=True)
        tk.Label(pc, text="POPULATION SIZE", bg=CARD, fg=MUTED,
                 font=FONT_LABEL).pack(anchor="w", padx=14, pady=(12, 2))
        self.pop_var = tk.IntVar(value=50)
        tk.Label(pc, textvariable=self.pop_var,
                 bg=CARD, fg=ACCENT, font=FONT_NUM).pack(anchor="w", padx=14)
        ttk.Scale(pc, from_=20, to=150, variable=self.pop_var,
                  orient="horizontal",
                  command=lambda v: self.pop_var.set(int(float(v)))
                  ).pack(fill="x", padx=14, pady=(0, 14))

        # Generate button
        self.gen_btn = self._green_btn(pad, "  ◈  Generate My Plan  ", self._run_ga,
                                       big=True)
        self.gen_btn.pack(pady=8)

        self.status_var = tk.StringVar(value="")
        tk.Label(pad, textvariable=self.status_var, bg=BG, fg=TEXT2,
                 font=FONT_SMALL).pack()

        self.progress = ttk.Progressbar(pad, style="green.Horizontal.TProgressbar",
                                        mode="indeterminate", length=320)

    # ═══════════════════════════════════════════════════════════════════════════
    #  GA runner (background thread)
    # ═══════════════════════════════════════════════════════════════════════════
    def _run_ga(self):
        if self.ga_running:
            return

        # validate
        try:
            age    = int(self.age_var.get())
            weight = int(self.weight_var.get())
            height = int(self.height_var.get())
        except Exception:
            messagebox.showerror("Input Error", "Please check your inputs.")
            return

        excl_raw = self.excl_var.get().strip()
        excluded = [x.strip() for x in excl_raw.split(",") if x.strip()] \
                   if excl_raw else []

        self.ga_running = True
        self.gen_btn.config(state="disabled", text="  Running…  ")
        self.status_var.set("Initialising population…")
        self.progress.pack(pady=(4, 12))
        self.progress.start(12)

        def _worker():
            def _cb(gen, fit, _):
                pct = int((gen / self.gen_var.get()) * 100)
                self.status_var.set(
                    f"Generation {gen}/{self.gen_var.get()}  —  "
                    f"best fit: {fit:.4f}  ({pct}%)")

            self.result = generate_meal_plan(
                weight_kg      = weight,
                height_cm      = height,
                age            = age,
                gender         = self.gender_var.get(),
                activity_level = self.activity_var.get(),
                goal           = self.goal_var.get(),
                excluded_foods = excluded,
                population_size= int(self.pop_var.get()),
                generations    = int(self.gen_var.get()),
                callback       = _cb,
            )
            self.after(0, self._on_ga_done)

        threading.Thread(target=_worker, daemon=True).start()

    def _on_ga_done(self):
        self.progress.stop()
        self.progress.pack_forget()
        self.ga_running = False
        self.gen_btn.config(state="normal", text="  ◈  Generate My Plan  ")
        self.status_var.set("✦  Plan ready!")
        self.btn_result.config(state="normal")
        self._show_results()

    # ═══════════════════════════════════════════════════════════════════════════
    #  SCREEN 3 — RESULTS
    # ═══════════════════════════════════════════════════════════════════════════
    def _show_results(self):
        if not self.result:
            messagebox.showinfo("No Plan Yet", "Generate a plan first.")
            self._show_form()
            return
        self._clear_body()
        self._set_nav(2)

        canvas = tk.Canvas(self.body, bg=BG, bd=0, highlightthickness=0)
        scroll = tk.Scrollbar(self.body, orient="vertical", command=canvas.yview)
        canvas.configure(yscrollcommand=scroll.set)
        scroll.pack(side="right", fill="y")
        canvas.pack(side="left", fill="both", expand=True)

        inner = tk.Frame(canvas, bg=BG)
        win_id = canvas.create_window((0, 0), window=inner, anchor="nw")

        def _resize(e):
            canvas.itemconfig(win_id, width=e.width)
        canvas.bind("<Configure>", _resize)
        inner.bind("<Configure>", lambda e: canvas.configure(
            scrollregion=canvas.bbox("all")))
        canvas.bind_all("<MouseWheel>",
                        lambda e: canvas.yview_scroll(-1*(e.delta//120), "units"))

        pad = tk.Frame(inner, bg=BG)
        pad.pack(fill="both", expand=True, padx=50, pady=20)

        profile   = self.result["profile"]
        totals    = self.result["totals"]
        score     = self.result["fitness_score"]
        breakdown = get_meal_breakdown(self.result)

        # ── Top stats row ─────────────────────────────────────────────────────
        self._section_title(pad, "◈  Your Daily Targets")
        stat_row = tk.Frame(pad, bg=BG)
        stat_row.pack(fill="x", pady=(0, 14))

        stats = [
            ("CALORIES",  f"{profile['target_calories']}", "kcal"),
            ("PROTEIN",   f"{profile['protein_g']}",       "g"),
            ("CARBS",     f"{profile['carbs_g']}",         "g"),
            ("FATS",      f"{profile['fats_g']}",          "g"),
            ("BMI",       f"{profile['bmi']}",             profile['bmi_category']),
            ("MATCH",     f"{round(score*100,1)}",         "%"),
        ]
        for label, val, unit in stats:
            c = self._card(stat_row)
            c.pack(side="left", fill="both", expand=True, padx=3)
            tk.Label(c, text=label, bg=CARD, fg=MUTED,
                     font=FONT_LABEL).pack(pady=(10, 0))
            tk.Label(c, text=val, bg=CARD, fg=ACCENT,
                     font=("Courier New", 15, "bold")).pack()
            tk.Label(c, text=unit, bg=CARD, fg=TEXT2,
                     font=FONT_SMALL).pack(pady=(0, 10))

        # ── Achieved vs target row ────────────────────────────────────────────
        self._section_title(pad, "◈  Achieved vs Target")
        ach_card = self._card(pad)
        ach_card.pack(fill="x", pady=(0, 14))

        macros = [
            ("Calories", totals["calories"], profile["target_calories"], "kcal"),
            ("Protein",  totals["protein"],  profile["protein_g"],       "g"),
            ("Carbs",    totals["carbs"],    profile["carbs_g"],         "g"),
            ("Fats",     totals["fats"],     profile["fats_g"],          "g"),
        ]
        for name, achieved, target, unit in macros:
            row = tk.Frame(ach_card, bg=CARD)
            row.pack(fill="x", padx=14, pady=4)
            tk.Label(row, text=f"{name}", bg=CARD, fg=TEXT2,
                     font=FONT_LABEL, width=10, anchor="w").pack(side="left")
            tk.Label(row, text=f"{achieved} / {target} {unit}",
                     bg=CARD, fg=TEXT, font=FONT_BODY, width=22,
                     anchor="w").pack(side="left")
            pct = min(achieved / target, 1.2) if target else 0
            bar_bg = tk.Frame(row, bg=BORDER, height=8, width=260)
            bar_bg.pack(side="left", padx=8)
            bar_bg.pack_propagate(False)
            fill_w = int(260 * min(pct, 1.0))
            color  = ACCENT if pct <= 1.05 else DANGER
            tk.Frame(bar_bg, bg=color, height=8, width=fill_w).place(x=0, y=0)

        tk.Frame(ach_card, bg=BG, height=10).pack()

        # ── Meal cards ────────────────────────────────────────────────────────
        self._section_title(pad, "◈  Your Meal Plan")

        meal_colors = {
            "Breakfast": "#1a2e14",
            "Lunch":     "#142414",
            "Dinner":    "#14201a",
            "Snack 1":   "#1e2814",
            "Snack 2":   "#1e2814",
        }

        for meal, data in breakdown.items():
            mc = tk.Frame(pad, bg=meal_colors.get(meal, CARD),
                          highlightthickness=1, highlightbackground=BORDER)
            mc.pack(fill="x", pady=5)

            # meal header
            hdr = tk.Frame(mc, bg=meal_colors.get(meal, CARD))
            hdr.pack(fill="x", padx=16, pady=(12, 6))
            tk.Label(hdr, text=meal.upper(), bg=meal_colors.get(meal, CARD),
                     fg=ACCENT, font=FONT_BIG).pack(side="left")
            tk.Label(hdr, text=f"{data['calories']} kcal  ·  "
                                f"P {data['protein']}g  ·  "
                                f"C {data['carbs']}g  ·  "
                                f"F {data['fats']}g",
                     bg=meal_colors.get(meal, CARD), fg=TEXT2,
                     font=FONT_SMALL).pack(side="right")

            # divider
            tk.Frame(mc, bg=BORDER, height=1).pack(fill="x", padx=16)

            # food rows
            for item in data["items"]:
                row = tk.Frame(mc, bg=meal_colors.get(meal, CARD))
                row.pack(fill="x", padx=16, pady=3)
                tk.Label(row, text=f"  {item['name']}",
                         bg=meal_colors.get(meal, CARD), fg=TEXT,
                         font=FONT_BODY, anchor="w", width=38).pack(side="left")
                tk.Label(row, text=f"{item['grams']}g",
                         bg=meal_colors.get(meal, CARD), fg=MUTED,
                         font=FONT_MONO, width=6).pack(side="left")
                tk.Label(row, text=f"{item['calories']} kcal",
                         bg=meal_colors.get(meal, CARD), fg=ACCENT2,
                         font=FONT_MONO, width=10).pack(side="left")
                tk.Label(row, text=f"P:{item['protein']}g  "
                                   f"C:{item['carbs']}g  "
                                   f"F:{item['fats']}g",
                         bg=meal_colors.get(meal, CARD), fg=TEXT2,
                         font=FONT_SMALL).pack(side="left", padx=8)

            tk.Frame(mc, bg=BG, height=8).pack()

        # ── Regenerate button ─────────────────────────────────────────────────
        btn_row = tk.Frame(pad, bg=BG)
        btn_row.pack(pady=20)
        self._green_btn(btn_row, "  ◈  Regenerate Plan  ", self._show_form
                        ).pack(side="left", padx=8)
        self._outline_btn(btn_row, "  View Visualisation  ",
                          self._open_viz).pack(side="left", padx=8)

    # ═══════════════════════════════════════════════════════════════════════════
    #  Visualization launcher
    # ═══════════════════════════════════════════════════════════════════════════
    def _open_viz(self):
        if not self.result:
            return
        try:
            from visualization import show_visualization
            show_visualization(self.result)
        except Exception as e:
            messagebox.showerror("Visualisation Error", str(e))

    # ═══════════════════════════════════════════════════════════════════════════
    #  Reusable widget helpers
    # ═══════════════════════════════════════════════════════════════════════════
    def _card(self, parent):
        f = tk.Frame(parent, bg=CARD,
                     highlightthickness=1, highlightbackground=BORDER)
        return f

    def _section_title(self, parent, text):
        tk.Label(parent, text=text, bg=BG, fg=ACCENT2,
                 font=("Trebuchet MS", 11, "bold")).pack(anchor="w",
                                                         pady=(14, 6))

    def _green_btn(self, parent, text, cmd, big=False):
        font = ("Trebuchet MS", 11, "bold") if big else FONT_LABEL
        b = tk.Button(parent, text=text, command=cmd,
                      bg=ACCENT, fg="#0f1a0f", font=font,
                      relief="flat", bd=0, padx=20, pady=10,
                      activebackground=ACCENT2, activeforeground=BG,
                      cursor="hand2")
        return b

    def _outline_btn(self, parent, text, cmd):
        b = tk.Button(parent, text=text, command=cmd,
                      bg=BG, fg=ACCENT, font=FONT_LABEL,
                      relief="flat", bd=0, padx=20, pady=10,
                      highlightthickness=1, highlightbackground=ACCENT,
                      activebackground=CARD, activeforeground=ACCENT2,
                      cursor="hand2")
        return b

    def _set_nav(self, active):
        for i, b in enumerate([self.btn_home, self.btn_form, self.btn_result]):
            if b["state"] == "disabled":
                continue
            b.config(fg=ACCENT if i == active else TEXT2)
