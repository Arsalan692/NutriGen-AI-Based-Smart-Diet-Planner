import tkinter as tk
from tkinter import ttk, messagebox
import threading

from calorie_calculator import ACTIVITY_LEVELS, GOALS
from meal_planner import generate_meal_plan, get_meal_breakdown

# ── Palette ───────────────────────────────────────────────────────────────────
BG      = "#0d1a0d"
CARD    = "#132213"
CARD2   = "#1a2e1a"
CARD3   = "#1f361f"
BORDER  = "#2e4a2e"
ACCENT  = "#6fcf3e"
ACC2    = "#9de065"
ACC3    = "#c8f09a"
MUTED   = "#3d6b2a"
TEXT    = "#edf5e5"
TEXT2   = "#99bb88"
TEXT3   = "#5a8045"
DANGER  = "#e05c5c"
GOLD    = "#e0b84a"
GOLD2   = "#f5d07a"

# ── Fonts ─────────────────────────────────────────────────────────────────────
F_LOGO    = ("Georgia",       32, "bold")
F_HERO    = ("Georgia",       52, "bold")
F_HERO_S  = ("Georgia",       15, "italic")
F_HEAD    = ("Georgia",       17, "bold")
F_SECTION = ("Trebuchet MS",  13, "bold")
F_LABEL   = ("Trebuchet MS",  11, "bold")
F_BODY    = ("Trebuchet MS",  12)
F_BODY_S  = ("Trebuchet MS",  11)
F_SMALL   = ("Trebuchet MS",  10)
F_NUM     = ("Courier New",   26, "bold")
F_NUM_S   = ("Courier New",   18, "bold")
F_MONO    = ("Courier New",   11)
F_NAV     = ("Trebuchet MS",  11, "bold")

MEAL_ACCENT = {
    "Breakfast": "#5dade2",
    "Lunch":     "#6fcf3e",
    "Dinner":    "#9de065",
    "Snack 1":   "#e0b84a",
    "Snack 2":   "#e07c5c",
}

MEAL_BG = {
    "Breakfast": "#111e2a",
    "Lunch":     "#132213",
    "Dinner":    "#141f18",
    "Snack 1":   "#1e1d10",
    "Snack 2":   "#1e1510",
}


class NutriGenApp(tk.Tk):
    def __init__(self):
        super().__init__()
        self.title("NutriGen — AI Diet Planner")
        self.geometry("1000x740")
        self.minsize(900, 660)
        self.configure(bg=BG)
        self.resizable(True, True)

        self.result     = None
        self.ga_running = False

        self._style()
        self._build_header()
        self._build_body()
        self._show_welcome()

    def _style(self):
        s = ttk.Style(self)
        s.theme_use("clam")
        s.configure("TFrame",      background=BG)
        s.configure("Card.TFrame", background=CARD)
        s.configure("TLabel",      background=BG,   foreground=TEXT,  font=F_BODY)
        s.configure("Card.TLabel", background=CARD, foreground=TEXT,  font=F_BODY)
        s.configure("TCombobox",
                    fieldbackground=CARD2, background=CARD2,
                    foreground=TEXT, selectbackground=MUTED,
                    selectforeground=TEXT, font=F_BODY)
        s.map("TCombobox",
              fieldbackground=[("readonly", CARD2)],
              foreground=[("readonly", TEXT)],
              selectbackground=[("readonly", MUTED)])
        s.configure("Horizontal.TScale",
                    background=CARD, troughcolor=BORDER, sliderthickness=20)
        s.configure("green.Horizontal.TProgressbar",
                    troughcolor=BORDER, background=ACCENT, thickness=6)

    def _build_header(self):
        bar = tk.Frame(self, bg=CARD, height=62)
        bar.pack(fill="x", side="top")
        bar.pack_propagate(False)

        left = tk.Frame(bar, bg=CARD)
        left.pack(side="left", padx=24, pady=0)
        tk.Label(left, text="✦ NutriGen", bg=CARD, fg=ACCENT,
                 font=F_LOGO).pack(side="left")
        tk.Label(left, text="  AI Halal Diet Planner", bg=CARD, fg=TEXT3,
                 font=("Trebuchet MS", 11)).pack(side="left", pady=6)

        self.nav_frame = tk.Frame(bar, bg=CARD)
        self.nav_frame.pack(side="right", padx=20)

        self.btn_home   = self._nav_btn("Home",    self._show_welcome)
        self.btn_form   = self._nav_btn("Plan",    self._show_form)
        self.btn_result = self._nav_btn("Results", self._show_results)
        self.btn_result.config(state="disabled")

        tk.Frame(self, bg=ACCENT, height=2).pack(fill="x")

    def _nav_btn(self, text, cmd):
        b = tk.Button(self.nav_frame, text=text, command=cmd,
                      bg=CARD, fg=TEXT2, font=F_NAV,
                      relief="flat", bd=0, padx=16, pady=8,
                      activebackground=CARD2, activeforeground=ACCENT,
                      cursor="hand2")
        b.pack(side="left", padx=2)
        return b

    def _build_body(self):
        self.body = tk.Frame(self, bg=BG)
        self.body.pack(fill="both", expand=True)

    def _clear_body(self):
        for w in self.body.winfo_children():
            w.destroy()

    # ── SCREEN 1 — WELCOME ────────────────────────────────────────────────────
    def _show_welcome(self):
        self._clear_body()
        self._set_nav(0)

        outer = tk.Frame(self.body, bg=BG)
        outer.place(relx=0.5, rely=0.46, anchor="center")

        tk.Label(outer, text="NutriGen", bg=BG, fg=ACCENT,
                 font=F_HERO).pack()

        tk.Label(outer, text="Your AI-powered halal meal planner",
                 bg=BG, fg=TEXT2, font=F_HERO_S).pack(pady=(6, 0))

        tk.Frame(outer, bg=ACCENT, height=2, width=120).pack(pady=20)

        pill_row = tk.Frame(outer, bg=BG)
        pill_row.pack(pady=(0, 34))
        pills = [
            ("🧬", "Genetic Algorithm"),
            ("🥗", "182 Halal Foods"),
            ("⚡", "Macro Optimised"),
        ]
        for icon, label in pills:
            pill = tk.Frame(pill_row, bg=CARD2,
                            highlightthickness=1, highlightbackground=BORDER)
            pill.pack(side="left", padx=8)
            tk.Label(pill, text=f" {icon}  {label} ", bg=CARD2, fg=ACC2,
                     font=("Trebuchet MS", 11), padx=10, pady=10).pack()

        btn = self._green_btn(outer, "  Generate My Diet Plan  →",
                              self._show_form, big=True)
        btn.pack(pady=6)

        tk.Label(outer, text="Powered by evolutionary optimisation",
                 bg=BG, fg=TEXT3, font=F_SMALL).pack(pady=(16, 0))

    # ── SCREEN 2 — INPUT FORM ─────────────────────────────────────────────────
    def _show_form(self):
        self._clear_body()
        self._set_nav(1)

        canvas = tk.Canvas(self.body, bg=BG, bd=0, highlightthickness=0)
        scroll = tk.Scrollbar(self.body, orient="vertical", command=canvas.yview)
        canvas.configure(yscrollcommand=scroll.set)
        scroll.pack(side="right", fill="y")
        canvas.pack(side="left", fill="both", expand=True)

        inner  = tk.Frame(canvas, bg=BG)
        win_id = canvas.create_window((0, 0), window=inner, anchor="nw")

        canvas.bind("<Configure>", lambda e: canvas.itemconfig(win_id, width=e.width))
        inner.bind("<Configure>",  lambda e: canvas.configure(scrollregion=canvas.bbox("all")))
        
        def on_mousewheel_form(e):
            canvas.yview_scroll(-1 * (e.delta // 120), "units")
        
        canvas.bind("<Enter>", lambda e: canvas.bind_all("<MouseWheel>", on_mousewheel_form))
        canvas.bind("<Leave>", lambda e: canvas.unbind_all("<MouseWheel>"))

        pad = tk.Frame(inner, bg=BG)
        pad.pack(fill="both", expand=True, padx=70, pady=30)

        # ── Personal Details ──────────────────────────────────────────────────
        self._section(pad, "Personal Details")

        row1 = tk.Frame(pad, bg=BG)
        row1.pack(fill="x", pady=(0, 16))

        self.age_var    = tk.IntVar(value=25)
        self.weight_var = tk.IntVar(value=70)
        self.height_var = tk.IntVar(value=170)

        self._slider_card(row1, "AGE",    "years", self.age_var,    10,  80).pack(side="left", fill="both", expand=True, padx=(0, 10))
        self._slider_card(row1, "WEIGHT", "kg",    self.weight_var, 30, 180).pack(side="left", fill="both", expand=True, padx=(0, 10))
        self._slider_card(row1, "HEIGHT", "cm",    self.height_var, 120, 220).pack(side="left", fill="both", expand=True)

        # ── Goals & Activity ──────────────────────────────────────────────────
        self._section(pad, "Goals & Activity")

        row2 = tk.Frame(pad, bg=BG)
        row2.pack(fill="x", pady=(0, 16))

        gc = self._card(row2)
        gc.pack(side="left", fill="both", expand=True, padx=(0, 10))
        tk.Label(gc, text="GENDER", bg=CARD, fg=TEXT3, font=F_LABEL).pack(anchor="w", padx=18, pady=(16, 8))
        self.gender_var = tk.StringVar(value="Male")
        gf = tk.Frame(gc, bg=CARD)
        gf.pack(anchor="w", padx=18, pady=(0, 18))
        for g in ("Male", "Female"):
            tk.Radiobutton(gf, text=g, variable=self.gender_var, value=g,
                           bg=CARD, fg=TEXT, selectcolor=CARD2,
                           activebackground=CARD, activeforeground=ACCENT,
                           font=F_BODY).pack(side="left", padx=(0, 20))

        goalc = self._card(row2)
        goalc.pack(side="left", fill="both", expand=True, padx=(0, 10))
        tk.Label(goalc, text="FITNESS GOAL", bg=CARD, fg=TEXT3, font=F_LABEL).pack(anchor="w", padx=18, pady=(16, 8))
        self.goal_var = tk.StringVar(value="Weight Loss")
        ttk.Combobox(goalc, textvariable=self.goal_var,
                     values=list(GOALS.keys()),
                     state="readonly", font=F_BODY
                     ).pack(fill="x", padx=18, pady=(0, 18))

        actc = self._card(row2)
        actc.pack(side="left", fill="both", expand=True)
        tk.Label(actc, text="ACTIVITY LEVEL", bg=CARD, fg=TEXT3, font=F_LABEL).pack(anchor="w", padx=18, pady=(16, 8))
        self.activity_var = tk.StringVar(value="Moderately Active (exercise 3-5 days/week)")
        ttk.Combobox(actc, textvariable=self.activity_var,
                     values=list(ACTIVITY_LEVELS.keys()),
                     state="readonly", font=F_BODY
                     ).pack(fill="x", padx=18, pady=(0, 18))

        # ── Food Exclusions ───────────────────────────────────────────────────
        self._section(pad, "Food Exclusions  (optional)")

        exc_card = self._card(pad)
        exc_card.pack(fill="x", pady=(0, 16))
        tk.Label(exc_card,
                 text="Comma-separated food names to skip  —  e.g.  Garlic, Bitter Gourd / Karela",
                 bg=CARD, fg=TEXT2, font=F_BODY_S
                 ).pack(anchor="w", padx=18, pady=(14, 6))
        self.excl_var = tk.StringVar()
        e = tk.Entry(exc_card, textvariable=self.excl_var,
                     bg=CARD2, fg=TEXT, insertbackground=ACCENT,
                     relief="flat", font=F_BODY,
                     highlightthickness=1, highlightbackground=BORDER,
                     highlightcolor=ACCENT)
        e.pack(fill="x", padx=18, pady=(0, 18), ipady=6)

        # ── Algorithm Settings ────────────────────────────────────────────────
        self._section(pad, "Algorithm Settings")

        row3 = tk.Frame(pad, bg=BG)
        row3.pack(fill="x", pady=(0, 24))

        self.gen_var = tk.IntVar(value=100)
        self.pop_var = tk.IntVar(value=50)

        self._slider_card(row3, "GENERATIONS",    "",  self.gen_var, 40,  200).pack(side="left", fill="both", expand=True, padx=(0, 10))
        self._slider_card(row3, "POPULATION SIZE", "", self.pop_var, 20, 150).pack(side="left", fill="both", expand=True)

        # ── Generate ──────────────────────────────────────────────────────────
        self.gen_btn = self._green_btn(pad, "  ◈  Generate My Plan  ", self._run_ga, big=True)
        self.gen_btn.pack(pady=6)

        self.status_var = tk.StringVar(value="")
        tk.Label(pad, textvariable=self.status_var, bg=BG, fg=TEXT2,
                 font=F_BODY_S).pack(pady=(4, 0))

        self.progress = ttk.Progressbar(pad, style="green.Horizontal.TProgressbar",
                                        mode="indeterminate", length=360)

    def _slider_card(self, parent, label, unit, var, lo, hi):
        c = self._card(parent)
        tk.Label(c, text=label, bg=CARD, fg=TEXT3,
                 font=F_LABEL).pack(anchor="w", padx=18, pady=(16, 4))

        val_row = tk.Frame(c, bg=CARD)
        val_row.pack(anchor="w", padx=18)
        tk.Label(val_row, textvariable=var, bg=CARD, fg=ACCENT,
                 font=F_NUM).pack(side="left")
        if unit:
            tk.Label(val_row, text=f"  {unit}", bg=CARD, fg=TEXT3,
                     font=F_BODY_S).pack(side="left", pady=(6, 0))

        ttk.Scale(c, from_=lo, to=hi, variable=var, orient="horizontal",
                  command=lambda v: var.set(int(float(v)))
                  ).pack(fill="x", padx=18, pady=(6, 18))
        return c

    def _run_ga(self):
        if self.ga_running:
            return
        try:
            age    = int(self.age_var.get())
            weight = int(self.weight_var.get())
            height = int(self.height_var.get())
        except Exception:
            messagebox.showerror("Input Error", "Please check your inputs.")
            return

        excl_raw = self.excl_var.get().strip()
        excluded = [x.strip() for x in excl_raw.split(",") if x.strip()] if excl_raw else []

        self.ga_running = True
        self.gen_btn.config(state="disabled", text="  Running…  ")
        self.status_var.set("Initialising population…")
        self.progress.pack(pady=(6, 14))
        self.progress.start(10)

        def worker():
            def cb(gen, fit, _):
                pct = int((gen / self.gen_var.get()) * 100)
                self.status_var.set(
                    f"Generation {gen} / {self.gen_var.get()}   ·   "
                    f"fitness  {fit:.4f}   ({pct}%)")

            self.result = generate_meal_plan(
                weight_kg       = weight,
                height_cm       = height,
                age             = age,
                gender          = self.gender_var.get(),
                activity_level  = self.activity_var.get(),
                goal            = self.goal_var.get(),
                excluded_foods  = excluded,
                population_size = int(self.pop_var.get()),
                generations     = int(self.gen_var.get()),
                callback        = cb,
            )
            self.after(0, self._on_ga_done)

        threading.Thread(target=worker, daemon=True).start()

    def _on_ga_done(self):
        self.progress.stop()
        self.progress.pack_forget()
        self.ga_running = False
        self.gen_btn.config(state="normal", text="  ◈  Generate My Plan  ")
        self.status_var.set("✦  Plan ready!")
        self.btn_result.config(state="normal")
        self._show_results()

    # ── SCREEN 3 — RESULTS ────────────────────────────────────────────────────
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

        inner  = tk.Frame(canvas, bg=BG)
        win_id = canvas.create_window((0, 0), window=inner, anchor="nw")

        canvas.bind("<Configure>", lambda e: canvas.itemconfig(win_id, width=e.width))
        inner.bind("<Configure>",  lambda e: canvas.configure(scrollregion=canvas.bbox("all")))
        
        def on_mousewheel_results(e):
            canvas.yview_scroll(-1 * (e.delta // 120), "units")
        
        canvas.bind("<Enter>", lambda e: canvas.bind_all("<MouseWheel>", on_mousewheel_results))
        canvas.bind("<Leave>", lambda e: canvas.unbind_all("<MouseWheel>"))

        pad = tk.Frame(inner, bg=BG)
        pad.pack(fill="both", expand=True, padx=56, pady=28)

        profile   = self.result["profile"]
        totals    = self.result["totals"]
        score     = self.result["fitness_score"]
        breakdown = get_meal_breakdown(self.result)

        # ── Stat cards ────────────────────────────────────────────────────────
        self._section(pad, "Daily Targets")

        stat_row = tk.Frame(pad, bg=BG)
        stat_row.pack(fill="x", pady=(0, 18))

        stats = [
            ("CALORIES", f"{profile['target_calories']}", "kcal"),
            ("PROTEIN",  f"{profile['protein_g']}",       "g"),
            ("CARBS",    f"{profile['carbs_g']}",         "g"),
            ("FATS",     f"{profile['fats_g']}",          "g"),
            ("BMI",      f"{profile['bmi']}",             profile["bmi_category"]),
            ("MATCH",    f"{round(score * 100, 1)}",      "%"),
        ]
        for label, val, unit in stats:
            c = self._card(stat_row)
            c.pack(side="left", fill="both", expand=True, padx=3)
            tk.Label(c, text=label, bg=CARD, fg=TEXT3,
                     font=F_LABEL).pack(pady=(14, 2))
            tk.Label(c, text=val, bg=CARD, fg=ACCENT,
                     font=F_NUM_S).pack()
            tk.Label(c, text=unit, bg=CARD, fg=TEXT2,
                     font=F_BODY_S).pack(pady=(2, 14))

        # ── Progress bars ─────────────────────────────────────────────────────
        self._section(pad, "Achieved vs Target")

        ach_card = self._card(pad)
        ach_card.pack(fill="x", pady=(0, 18))

        macros = [
            ("Calories", totals["calories"], profile["target_calories"], "kcal"),
            ("Protein",  totals["protein"],  profile["protein_g"],       "g"),
            ("Carbs",    totals["carbs"],    profile["carbs_g"],         "g"),
            ("Fats",     totals["fats"],     profile["fats_g"],          "g"),
        ]
        for name, achieved, target, unit in macros:
            row = tk.Frame(ach_card, bg=CARD)
            row.pack(fill="x", padx=20, pady=8)

            info = tk.Frame(row, bg=CARD)
            info.pack(fill="x")
            tk.Label(info, text=name, bg=CARD, fg=TEXT,
                     font=F_LABEL, width=10, anchor="w").pack(side="left")
            tk.Label(info, text=f"{achieved}  /  {target} {unit}",
                     bg=CARD, fg=TEXT2, font=F_BODY).pack(side="left")
            pct = achieved / target if target else 0
            tk.Label(info, text=f"{round(pct * 100)}%",
                     bg=CARD, fg=ACCENT if pct <= 1.05 else DANGER,
                     font=F_LABEL).pack(side="right")

            bar_bg = tk.Frame(row, bg=BORDER, height=10)
            bar_bg.pack(fill="x", pady=(6, 0))
            bar_bg.update_idletasks()

            def draw_bar(b=bar_bg, p=min(pct, 1.0), ok=(pct <= 1.05)):
                w = int(b.winfo_width() * p)
                color = ACCENT if ok else DANGER
                tk.Frame(b, bg=color, height=10, width=w).place(x=0, y=0)

            bar_bg.after(50, draw_bar)

        tk.Frame(ach_card, bg=BG, height=6).pack()

        # ── Meal cards ────────────────────────────────────────────────────────
        self._section(pad, "Your Meal Plan")

        for meal, data in breakdown.items():
            bg   = MEAL_BG.get(meal, CARD)
            acc  = MEAL_ACCENT.get(meal, ACCENT)

            mc = tk.Frame(pad, bg=bg,
                          highlightthickness=1, highlightbackground=BORDER)
            mc.pack(fill="x", pady=6)

            hdr = tk.Frame(mc, bg=bg)
            hdr.pack(fill="x", padx=20, pady=(16, 10))

            tk.Label(hdr, text=meal.upper(), bg=bg, fg=acc,
                     font=F_HEAD).pack(side="left")

            macro_txt = (f"{data['calories']} kcal   ·   "
                         f"P {data['protein']}g   ·   "
                         f"C {data['carbs']}g   ·   "
                         f"F {data['fats']}g")
            tk.Label(hdr, text=macro_txt, bg=bg, fg=TEXT2,
                     font=F_BODY).pack(side="right", pady=4)

            tk.Frame(mc, bg=BORDER, height=1).pack(fill="x", padx=20)

            for item in data["items"]:
                row = tk.Frame(mc, bg=bg)
                row.pack(fill="x", padx=20, pady=5)

                tk.Label(row, text=item["name"], bg=bg, fg=TEXT,
                         font=F_BODY, anchor="w", width=34).pack(side="left")
                tk.Label(row, text=f"{item['grams']}g", bg=bg, fg=TEXT3,
                         font=F_MONO, width=7).pack(side="left")
                tk.Label(row, text=f"{item['calories']} kcal", bg=bg, fg=acc,
                         font=F_MONO, width=11).pack(side="left")
                tk.Label(row, text=f"P {item['protein']}g  "
                                   f"C {item['carbs']}g  "
                                   f"F {item['fats']}g",
                         bg=bg, fg=TEXT2, font=F_BODY_S).pack(side="left", padx=12)

            tk.Frame(mc, bg=bg, height=10).pack()

        # ── Bottom buttons ────────────────────────────────────────────────────
        btn_row = tk.Frame(pad, bg=BG)
        btn_row.pack(pady=28)
        self._green_btn(btn_row, "  ◈  Regenerate Plan  ",
                        self._show_form).pack(side="left", padx=10)
        self._outline_btn(btn_row, "  View Visualisation  ",
                          self._open_viz).pack(side="left", padx=10)

    def _open_viz(self):
        if not self.result:
            return
        try:
            from visualization import show_visualization
            show_visualization(self.result)
        except Exception as e:
            messagebox.showerror("Visualisation Error", str(e))

    # ── Helpers ───────────────────────────────────────────────────────────────
    def _card(self, parent):
        return tk.Frame(parent, bg=CARD,
                        highlightthickness=1, highlightbackground=BORDER)

    def _section(self, parent, text):
        row = tk.Frame(parent, bg=BG)
        row.pack(fill="x", pady=(20, 8))
        tk.Label(row, text=text, bg=BG, fg=TEXT,
                 font=F_SECTION).pack(side="left")
        tk.Frame(row, bg=BORDER, height=1).pack(side="left", fill="x",
                                                 expand=True, padx=(12, 0), pady=6)

    def _green_btn(self, parent, text, cmd, big=False):
        font = ("Trebuchet MS", 13, "bold") if big else ("Trebuchet MS", 11, "bold")
        return tk.Button(parent, text=text, command=cmd,
                         bg=ACCENT, fg=BG, font=font,
                         relief="flat", bd=0, padx=26, pady=12,
                         activebackground=ACC2, activeforeground=BG,
                         cursor="hand2")

    def _outline_btn(self, parent, text, cmd):
        return tk.Button(parent, text=text, command=cmd,
                         bg=BG, fg=ACCENT, font=("Trebuchet MS", 11, "bold"),
                         relief="flat", bd=0, padx=26, pady=12,
                         highlightthickness=1, highlightbackground=ACCENT,
                         activebackground=CARD, activeforeground=ACC2,
                         cursor="hand2")

    def _set_nav(self, active):
        for i, b in enumerate([self.btn_home, self.btn_form, self.btn_result]):
            if b["state"] == "disabled":
                continue
            b.config(fg=ACCENT if i == active else TEXT2)