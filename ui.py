import customtkinter as ctk
import tkinter as tk
from tkinter import messagebox
import threading

from theme import *
from calorie_calculator import ACTIVITY_LEVELS, GOALS
from meal_planner import generate_meal_plan, get_meal_breakdown
from data_loader import load_foods

ctk.set_appearance_mode("dark")
ctk.set_default_color_theme("green")


class NutriGenApp(ctk.CTk):
    def __init__(self):
        super().__init__()
        self.title("NutriGen — AI Diet Planner")
        self.geometry("1180x800")
        self.minsize(1060, 720)
        self.configure(fg_color=BG_DARK)

        self.result = None
        self.ga_running = False
        self._build_sidebar()
        self._build_main()
        self._show_welcome()

        self.protocol("WM_DELETE_WINDOW", self._on_close)

    def _on_close(self):
        """Clean shutdown — prevent dangling after-callbacks."""
        import os, signal
        try:
            self.quit()
            self.destroy()
        except Exception:
            pass
        os.kill(os.getpid(), signal.SIGTERM)


    def _card_3d(self, card):
        """Add 3D hover glow effect to a card frame."""
        def on_enter(e):
            try:
                card.configure(border_color=EMERALD_D, fg_color=BG_CARD2)
            except Exception:
                pass
        def on_leave(e):
            try:
                card.configure(border_color=BORDER, fg_color=BG_CARD)
            except Exception:
                pass
        card.bind("<Enter>", on_enter)
        card.bind("<Leave>", on_leave)

    # ── Sidebar ─────────────────────────────────
    def _build_sidebar(self):
        self.sidebar = ctk.CTkFrame(self, width=240, fg_color=BG_MID,
                                     corner_radius=0, border_width=0)
        self.sidebar.pack(side="left", fill="y")
        self.sidebar.pack_propagate(False)

        # logo
        logo_frame = ctk.CTkFrame(self.sidebar, fg_color="transparent")
        logo_frame.pack(fill="x", padx=20, pady=(28, 8))
        ctk.CTkLabel(logo_frame, text="🥗", font=("Segoe UI", 34)).pack(side="left")
        ctk.CTkLabel(logo_frame, text=" NutriGen", font=F_LOGO,
                     text_color=EMERALD).pack(side="left", padx=(4,0))

        ctk.CTkLabel(self.sidebar, text="AI Halal Diet Planner",
                     font=F_TINY, text_color=TEXT_MUTED).pack(padx=20, anchor="w")

        # divider
        ctk.CTkFrame(self.sidebar, height=1, fg_color=BORDER).pack(fill="x", padx=20, pady=(20,20))

        # nav buttons
        self.nav_btns = []
        nav_items = [
            ("🏠", "Home",    self._show_welcome),
            ("📋", "Plan",    self._show_form),
            ("📊", "Results", self._show_results),
        ]
        for icon, label, cmd in nav_items:
            btn = ctk.CTkButton(
                self.sidebar, text=f"  {icon}  {label}", font=F_NAV,
                fg_color="transparent", text_color=TEXT_SECONDARY,
                hover_color=BG_CARD2, anchor="w", height=48,
                corner_radius=12, command=cmd
            )
            btn.pack(fill="x", padx=12, pady=3)
            self.nav_btns.append(btn)

        # results disabled initially
        self.nav_btns[2].configure(state="disabled", text_color=TEXT_MUTED)

        # bottom info
        spacer = ctk.CTkFrame(self.sidebar, fg_color="transparent")
        spacer.pack(fill="both", expand=True)

        ctk.CTkFrame(self.sidebar, height=1, fg_color=BORDER).pack(fill="x", padx=20, pady=(0,12))

        try:
            _fc = len(load_foods())
        except Exception:
            _fc = 182
        ctk.CTkLabel(self.sidebar, text=f"📦 {_fc} Halal Foods",
                     font=F_TINY, text_color=TEXT_MUTED).pack(padx=20, anchor="w")
        ctk.CTkLabel(self.sidebar, text="⚡ Genetic Algorithm",
                     font=F_TINY, text_color=TEXT_MUTED).pack(padx=20, anchor="w", pady=(2,20))

    def _set_nav(self, idx):
        for i, btn in enumerate(self.nav_btns):
            if i == 2 and not self.result and i != idx:
                btn.configure(state="disabled", fg_color="transparent",
                              text_color=TEXT_MUTED)
            elif i == idx:
                btn.configure(fg_color=EMERALD_D, text_color=TEXT_PRIMARY,
                              state="normal")
            else:
                btn.configure(fg_color="transparent", text_color=TEXT_SECONDARY,
                              state="normal")

    # ── Main Area ───────────────────────────────
    def _build_main(self):
        self.main = ctk.CTkFrame(self, fg_color=BG_DARK, corner_radius=0)
        self.main.pack(side="right", fill="both", expand=True)

    def _clear_main(self):
        for w in self.main.winfo_children():
            w.destroy()

    # ── WELCOME PAGE ────────────────────────────
    def _show_welcome(self):
        self._clear_main()
        self._set_nav(0)

        center = ctk.CTkFrame(self.main, fg_color="transparent")
        center.place(relx=0.5, rely=0.45, anchor="center")

        ctk.CTkLabel(center, text="🥗", font=("Segoe UI", 72)).pack()
        ctk.CTkLabel(center, text="NutriGen", font=F_HERO,
                     text_color=EMERALD).pack(pady=(10,0))
        ctk.CTkLabel(center, text="Your AI-powered halal meal planner",
                     font=F_HERO_SUB, text_color=TEXT_SECONDARY).pack(pady=(6,0))

        # divider
        ctk.CTkFrame(center, width=120, height=3, fg_color=EMERALD,
                     corner_radius=2).pack(pady=24)

        # feature pills
        pill_frame = ctk.CTkFrame(center, fg_color="transparent")
        pill_frame.pack(pady=(0, 32))
        pills = [
            ("🧬  Genetic Algorithm", EMERALD_D),
            ("🍽️  Macro Optimised", "#92400e"),
            ("📊  Visual Analytics", "#1e3a5f"),
        ]
        for text, color in pills:
            ctk.CTkButton(pill_frame, text=text, font=F_BODY_B,
                          fg_color=color, hover_color=color,
                          text_color=TEXT_PRIMARY, corner_radius=22,
                          height=44, width=200, state="disabled"
                          ).pack(side="left", padx=10)

        # CTA
        ctk.CTkButton(center, text="✨  Generate My Diet Plan", font=F_H2,
                      fg_color=EMERALD, hover_color=EMERALD_D,
                      text_color=TEXT_ON_ACCENT, height=56,
                      corner_radius=16, width=360,
                      command=self._show_form).pack(pady=(8,0))

        ctk.CTkLabel(center, text="Powered by evolutionary optimisation",
                     font=F_TINY, text_color=TEXT_MUTED).pack(pady=(20,0))

    # ── FORM PAGE ───────────────────────────────
    def _show_form(self):
        self._clear_main()
        self._set_nav(1)

        scroll = ctk.CTkScrollableFrame(self.main, fg_color=BG_DARK,
                                         scrollbar_button_color=BORDER,
                                         scrollbar_button_hover_color=BORDER_LIGHT)
        scroll.pack(fill="both", expand=True, padx=0, pady=0)

        pad = ctk.CTkFrame(scroll, fg_color="transparent")
        pad.pack(fill="x", expand=True, padx=50, pady=30)

        # ── Section: Personal Details ───────────
        self._section(pad, "👤", "Personal Details")

        row1 = ctk.CTkFrame(pad, fg_color="transparent")
        row1.pack(fill="x", pady=(0,16))
        row1.columnconfigure((0,1,2), weight=1)

        self.age_var = tk.IntVar(value=25)
        self.weight_var = tk.IntVar(value=70)
        self.height_var = tk.IntVar(value=170)

        self._slider_card(row1, "AGE", "years", self.age_var, 10, 80, 0)
        self._slider_card(row1, "WEIGHT", "kg", self.weight_var, 30, 180, 1)
        self._slider_card(row1, "HEIGHT", "cm", self.height_var, 120, 220, 2)

        # ── Section: Goals & Activity ───────────
        self._section(pad, "🎯", "Goals & Activity")

        row2 = ctk.CTkFrame(pad, fg_color="transparent")
        row2.pack(fill="x", pady=(0,16))
        row2.columnconfigure((0,1,2), weight=1)

        # Gender
        gc = ctk.CTkFrame(row2, fg_color=BG_CARD, corner_radius=12, border_width=1, border_color=BORDER)
        gc.grid(row=0, column=0, sticky="nsew", padx=(0,8))
        ctk.CTkLabel(gc, text="GENDER", font=F_SMALL_B, text_color=TEXT_MUTED).pack(anchor="w", padx=18, pady=(16,8))
        self.gender_var = tk.StringVar(value="Male")
        gf = ctk.CTkFrame(gc, fg_color="transparent")
        gf.pack(anchor="w", padx=18, pady=(0,18))
        for g in ("Male", "Female"):
            ctk.CTkRadioButton(gf, text=g, variable=self.gender_var, value=g,
                               font=F_BODY, text_color=TEXT_PRIMARY,
                               fg_color=EMERALD, hover_color=EMERALD_D,
                               border_color=BORDER_LIGHT).pack(side="left", padx=(0,16))

        # Goal
        goalc = ctk.CTkFrame(row2, fg_color=BG_CARD, corner_radius=12, border_width=1, border_color=BORDER)
        goalc.grid(row=0, column=1, sticky="nsew", padx=4)
        ctk.CTkLabel(goalc, text="FITNESS GOAL", font=F_SMALL_B, text_color=TEXT_MUTED).pack(anchor="w", padx=18, pady=(16,8))
        self.goal_var = tk.StringVar(value="Weight Loss")
        ctk.CTkOptionMenu(goalc, variable=self.goal_var, values=list(GOALS.keys()),
                          font=F_BODY, fg_color=BG_INPUT, button_color=EMERALD_D,
                          button_hover_color=EMERALD, dropdown_fg_color=BG_CARD,
                          dropdown_hover_color=BG_CARD2, text_color=TEXT_PRIMARY
                          ).pack(fill="x", padx=18, pady=(0,18))

        # Activity
        actc = ctk.CTkFrame(row2, fg_color=BG_CARD, corner_radius=12, border_width=1, border_color=BORDER)
        actc.grid(row=0, column=2, sticky="nsew", padx=(8,0))
        ctk.CTkLabel(actc, text="ACTIVITY LEVEL", font=F_SMALL_B, text_color=TEXT_MUTED).pack(anchor="w", padx=18, pady=(16,8))
        self.activity_var = tk.StringVar(value="Moderately Active (exercise 3-5 days/week)")
        ctk.CTkOptionMenu(actc, variable=self.activity_var, values=list(ACTIVITY_LEVELS.keys()),
                          font=F_SMALL, fg_color=BG_INPUT, button_color=EMERALD_D,
                          button_hover_color=EMERALD, dropdown_fg_color=BG_CARD,
                          dropdown_hover_color=BG_CARD2, text_color=TEXT_PRIMARY
                          ).pack(fill="x", padx=18, pady=(0,18))

        # ── Section: Food Exclusions ────────────
        self._section(pad, "🚫", "Food Exclusions (optional)")

        exc_card = ctk.CTkFrame(pad, fg_color=BG_CARD, corner_radius=12, border_width=1, border_color=BORDER)
        exc_card.pack(fill="x", pady=(0,16))
        ctk.CTkLabel(exc_card, text="Comma-separated food names to skip  —  e.g.  Garlic, Bitter Gourd",
                     font=F_SMALL, text_color=TEXT_MUTED).pack(anchor="w", padx=18, pady=(14,6))
        self.excl_var = tk.StringVar()
        ctk.CTkEntry(exc_card, textvariable=self.excl_var, font=F_BODY,
                     fg_color=BG_INPUT, border_color=BORDER, text_color=TEXT_PRIMARY,
                     placeholder_text="e.g. Garlic, Bitter Gourd / Karela",
                     placeholder_text_color=TEXT_MUTED, height=46, corner_radius=12
                     ).pack(fill="x", padx=18, pady=(0,18))

        # ── Section: Algorithm Settings ─────────
        self._section(pad, "⚙️", "Algorithm Settings")

        row3 = ctk.CTkFrame(pad, fg_color="transparent")
        row3.pack(fill="x", pady=(0,24))
        row3.columnconfigure((0,1), weight=1)

        self.gen_var = tk.IntVar(value=60)
        self.pop_var = tk.IntVar(value=30)

        self._slider_card(row3, "GENERATIONS", "", self.gen_var, 40, 200, 0)
        self._slider_card(row3, "POPULATION SIZE", "", self.pop_var, 20, 150, 1)

        # Generate button
        self.gen_btn = ctk.CTkButton(pad, text="🚀  Generate My Plan", font=F_H2,
                                     fg_color=EMERALD, hover_color=EMERALD_D,
                                     text_color=TEXT_ON_ACCENT, height=56,
                                     corner_radius=16, command=self._run_ga)
        self.gen_btn.pack(pady=(8,4))

        self.status_var = tk.StringVar(value="")
        self.status_label = ctk.CTkLabel(pad, textvariable=self.status_var,
                                         font=F_SMALL, text_color=TEXT_SECONDARY)
        self.status_label.pack(pady=(4,0))

        self.progress = ctk.CTkProgressBar(pad, width=400, height=8,
                                           fg_color=BG_CARD, progress_color=EMERALD,
                                           corner_radius=4)

    def _slider_card(self, parent, label, unit, var, lo, hi, col):
        c = ctk.CTkFrame(parent, fg_color=BG_CARD, corner_radius=14,
                         border_width=1, border_color=BORDER)
        px = (0 if col == 0 else 6, 0 if col == parent.grid_size()[0]-1 else 6)
        c.grid(row=0, column=col, sticky="nsew", padx=px)
        self._card_3d(c)

        ctk.CTkLabel(c, text=label, font=F_BODY_B,
                     text_color=TEXT_MUTED).pack(anchor="w", padx=20, pady=(18,4))

        val_frame = ctk.CTkFrame(c, fg_color="transparent")
        val_frame.pack(anchor="w", padx=20)
        val_label = ctk.CTkLabel(val_frame, textvariable=var, font=F_NUM_BIG,
                                 text_color=EMERALD)
        val_label.pack(side="left")
        if unit:
            ctk.CTkLabel(val_frame, text=f"  {unit}", font=F_BODY,
                         text_color=TEXT_MUTED).pack(side="left", pady=(10,0))

        slider = ctk.CTkSlider(c, from_=lo, to=hi, variable=var,
                               fg_color=BG_INPUT, progress_color=EMERALD_D,
                               button_color=EMERALD, button_hover_color=EMERALD_L,
                               height=20, corner_radius=10,
                               command=lambda v: var.set(int(float(v))))
        slider.pack(fill="x", padx=20, pady=(8,20))

    # ── GA Execution ────────────────────────────
    def _run_ga(self):
        if self.ga_running:
            return
        try:
            age = int(self.age_var.get())
            weight = int(self.weight_var.get())
            height = int(self.height_var.get())
        except Exception:
            messagebox.showerror("Input Error", "Please check your inputs.")
            return

        excl_raw = self.excl_var.get().strip()
        excluded = [x.strip() for x in excl_raw.split(",") if x.strip()] if excl_raw else []

        self.ga_running = True
        self.gen_btn.configure(state="disabled", text="⏳  Running...")
        self.status_var.set("Initialising population...")
        self.progress.pack(pady=(6,14))
        self.progress.configure(mode="indeterminate")
        self.progress.start()

        def worker():
            total_gens = self.gen_var.get()
            def cb(gen, fit, _):
                pct = int((gen / total_gens) * 100)
                self.status_var.set(
                    f"Generation {gen} / {total_gens}   ·   "
                    f"fitness  {fit:.4f}   ({pct}%)")

            self.result = generate_meal_plan(
                weight_kg=weight, height_cm=height, age=age,
                gender=self.gender_var.get(),
                activity_level=self.activity_var.get(),
                goal=self.goal_var.get(),
                excluded_foods=excluded,
                population_size=int(self.pop_var.get()),
                generations=int(self.gen_var.get()),
                callback=cb,
            )
            self.after(0, self._on_ga_done)

        threading.Thread(target=worker, daemon=True).start()

    def _on_ga_done(self):
        self.progress.stop()
        self.progress.pack_forget()
        self.ga_running = False
        self.gen_btn.configure(state="normal", text="🚀  Generate My Plan")
        self.status_var.set("✅ Plan ready!")
        self.nav_btns[2].configure(state="normal", text_color=TEXT_SECONDARY)
        self._show_results()

    # ── RESULTS PAGE ────────────────────────────
    def _show_results(self):
        if not self.result:
            messagebox.showinfo("No Plan Yet", "Generate a plan first.")
            self._show_form()
            return
        self._clear_main()
        self._set_nav(2)

        scroll = ctk.CTkScrollableFrame(self.main, fg_color=BG_DARK,
                                         scrollbar_button_color=BORDER,
                                         scrollbar_button_hover_color=BORDER_LIGHT)
        scroll.pack(fill="both", expand=True)

        pad = ctk.CTkFrame(scroll, fg_color="transparent")
        pad.pack(fill="x", expand=True, padx=50, pady=28)

        profile = self.result["profile"]
        totals = self.result["totals"]
        score = self.result["fitness_score"]
        breakdown = get_meal_breakdown(self.result)

        # ── Score Banner ────────────────────────
        banner = ctk.CTkFrame(pad, fg_color=BG_CARD, corner_radius=14,
                              border_width=1, border_color=BORDER)
        banner.pack(fill="x", pady=(0,20))
        bf = ctk.CTkFrame(banner, fg_color="transparent")
        bf.pack(fill="x", padx=24, pady=16)
        ctk.CTkLabel(bf, text=f"🎯 Optimization Score: {round(score*100,1)}%",
                     font=F_H2, text_color=EMERALD).pack(side="left")
        ctk.CTkLabel(bf, text=f"Goal: {profile['goal']}  ·  BMI: {profile['bmi']} ({profile['bmi_category']})",
                     font=F_SMALL, text_color=TEXT_SECONDARY).pack(side="right")

        # ── Stat Cards ──────────────────────────
        self._section(pad, "📊", "Daily Targets")

        stat_row = ctk.CTkFrame(pad, fg_color="transparent")
        stat_row.pack(fill="x", pady=(0,18))

        cal_diff = round(abs(totals["calories"] - profile["target_calories"]), 1)
        cal_sign = "+" if totals["calories"] > profile["target_calories"] else "-"

        stats = [
            ("🔥", "CALORIES", f"{profile['target_calories']}", "kcal", AMBER),
            ("💪", "PROTEIN",  f"{profile['protein_g']}",       "g",    EMERALD),
            ("🌾", "CARBS",    f"{profile['carbs_g']}",         "g",    SKY),
            ("🧈", "FATS",     f"{profile['fats_g']}",          "g",    ROSE),
            ("📏", "BMI",      f"{profile['bmi']}",    profile["bmi_category"], VIOLET),
            ("±",  "CAL ±",    f"{cal_sign}{cal_diff}", "kcal off",
             EMERALD if cal_diff <= 50 else AMBER),
        ]
        for i, (icon, label, val, unit, color) in enumerate(stats):
            sc = ctk.CTkFrame(stat_row, fg_color=BG_CARD, corner_radius=14,
                              border_width=1, border_color=BORDER)
            sc.pack(side="left", fill="both", expand=True, padx=4)
            self._card_3d(sc)

            ctk.CTkLabel(sc, text=f"{icon} {label}", font=F_BODY_B,
                         text_color=TEXT_MUTED).pack(pady=(16,4))
            ctk.CTkLabel(sc, text=val, font=F_NUM, text_color=color).pack()
            ctk.CTkLabel(sc, text=unit, font=F_SMALL,
                         text_color=TEXT_MUTED).pack(pady=(4,16))

        # ── Achieved vs Target ──────────────────
        self._section(pad, "📈", "Achieved vs Target")

        ach_card = ctk.CTkFrame(pad, fg_color=BG_CARD, corner_radius=12,
                                border_width=1, border_color=BORDER)
        ach_card.pack(fill="x", pady=(0,18))

        macros = [
            ("Calories", totals["calories"], profile["target_calories"], "kcal", AMBER),
            ("Protein",  totals["protein"],  profile["protein_g"],       "g",    EMERALD),
            ("Carbs",    totals["carbs"],    profile["carbs_g"],         "g",    SKY),
            ("Fats",     totals["fats"],     profile["fats_g"],          "g",    ROSE),
        ]
        for name, achieved, target, unit, color in macros:
            row = ctk.CTkFrame(ach_card, fg_color="transparent")
            row.pack(fill="x", padx=20, pady=10)

            info = ctk.CTkFrame(row, fg_color="transparent")
            info.pack(fill="x")
            ctk.CTkLabel(info, text=name, font=F_BODY_B, text_color=TEXT_PRIMARY,
                         width=90, anchor="w").pack(side="left")
            ctk.CTkLabel(info, text=f"{achieved}  /  {target} {unit}",
                         font=F_BODY, text_color=TEXT_SECONDARY).pack(side="left")
            pct = achieved / target if target else 0
            pct_color = EMERALD if pct <= 1.05 else ROSE
            ctk.CTkLabel(info, text=f"{round(pct*100)}%", font=F_BODY_B,
                         text_color=pct_color).pack(side="right")

            bar = ctk.CTkProgressBar(row, height=8, fg_color=BG_INPUT,
                                     progress_color=color, corner_radius=4)
            bar.pack(fill="x", pady=(6,0))
            bar.set(min(pct, 1.0))

        # ── Meal Plan ───────────────────────────
        self._section(pad, "🍽️", "Your Meal Plan")

        for meal, data in breakdown.items():
            acc = MEAL_ACCENT.get(meal, EMERALD)
            icon = MEAL_ICON.get(meal, "🍴")

            mc = ctk.CTkFrame(pad, fg_color=BG_CARD, corner_radius=14,
                              border_width=1, border_color=BORDER)
            mc.pack(fill="x", pady=8)
            self._card_3d(mc)

            # header
            hdr = ctk.CTkFrame(mc, fg_color="transparent")
            hdr.pack(fill="x", padx=20, pady=(16,10))

            ctk.CTkLabel(hdr, text=f"{icon}  {meal.upper()}", font=F_H3,
                         text_color=acc).pack(side="left")

            macro_txt = (f"{data['calories']} kcal   ·   "
                         f"P {data['protein']}g   ·   "
                         f"C {data['carbs']}g   ·   "
                         f"F {data['fats']}g")
            ctk.CTkLabel(hdr, text=macro_txt, font=F_SMALL,
                         text_color=TEXT_MUTED).pack(side="right")

            ctk.CTkFrame(mc, height=1, fg_color=BORDER).pack(fill="x", padx=20)

            # items
            for item in data["items"]:
                irow = ctk.CTkFrame(mc, fg_color="transparent")
                irow.pack(fill="x", padx=20, pady=4)

                ctk.CTkLabel(irow, text=item["name"], font=F_BODY,
                             text_color=TEXT_PRIMARY, anchor="w",
                             width=260).pack(side="left")
                ctk.CTkLabel(irow, text=f"{item['grams']}g", font=F_MONO,
                             text_color=TEXT_MUTED, width=60).pack(side="left")
                ctk.CTkLabel(irow, text=f"{item['calories']} kcal", font=F_MONO,
                             text_color=acc, width=90).pack(side="left")
                ctk.CTkLabel(irow, text=f"P {item['protein']}g  C {item['carbs']}g  F {item['fats']}g",
                             font=F_SMALL, text_color=TEXT_MUTED).pack(side="left", padx=12)

            ctk.CTkFrame(mc, height=8, fg_color="transparent").pack()

        # Action buttons
        btn_row = ctk.CTkFrame(pad, fg_color="transparent")
        btn_row.pack(pady=28)

        ctk.CTkButton(btn_row, text="🔄  Regenerate Plan", font=F_BODY_B,
                      fg_color=EMERALD, hover_color=EMERALD_D,
                      text_color=TEXT_ON_ACCENT, height=42,
                      corner_radius=10, command=self._show_form).pack(side="left", padx=8)

        ctk.CTkButton(btn_row, text="📊  View Visualisation", font=F_BODY_B,
                      fg_color=BG_CARD, hover_color=BG_CARD2,
                      text_color=EMERALD, border_width=2, border_color=EMERALD,
                      height=42, corner_radius=10,
                      command=self._open_viz).pack(side="left", padx=8)

    # ── Viz ─────────────────────────────────────
    def _open_viz(self):
        if not self.result:
            return
        try:
            from visualization import show_visualization
            show_visualization(self.result)
        except Exception as e:
            messagebox.showerror("Visualisation Error", str(e))

    # ── Helpers ─────────────────────────────────
    def _section(self, parent, icon, text):
        row = ctk.CTkFrame(parent, fg_color="transparent")
        row.pack(fill="x", pady=(24,12))
        ctk.CTkLabel(row, text=f"{icon}  {text}", font=F_H2,
                     text_color=TEXT_PRIMARY).pack(side="left")
        ctk.CTkFrame(row, height=1, fg_color=BORDER).pack(side="left", fill="x",
                                                            expand=True, padx=(16,0), pady=2)