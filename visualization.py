import tkinter as tk
from tkinter import ttk
import matplotlib
matplotlib.use("TkAgg")
import matplotlib.pyplot as plt
import matplotlib.patches as mpatches
from matplotlib.backends.backend_tkagg import FigureCanvasTkAgg
from matplotlib.gridspec import GridSpec
import numpy as np

from meal_planner import get_meal_breakdown

BG     = "#0f1a0f"
CARD   = "#162416"
CARD2  = "#1c2e1c"
BORDER = "#2a3d2a"
ACCENT = "#7ec44f"
ACC2   = "#a8d876"
MUTED  = "#4a6b3a"
TEXT   = "#e8f0e0"
TEXT2  = "#b0c4a0"
RED    = "#e05c5c"
GOLD   = "#d4a843"

MEAL_COLORS = {
    "Breakfast": "#5dade2",
    "Lunch":     "#7ec44f",
    "Dinner":    "#a8d876",
    "Snack 1":   "#d4a843",
    "Snack 2":   "#e07c5c",
}


def set_theme():
    plt.rcParams.update({
        "figure.facecolor":  BG,
        "axes.facecolor":    CARD,
        "axes.edgecolor":    BORDER,
        "axes.labelcolor":   TEXT2,
        "axes.titlecolor":   TEXT,
        "xtick.color":       TEXT2,
        "ytick.color":       TEXT2,
        "text.color":        TEXT,
        "grid.color":        BORDER,
        "grid.alpha":        0.5,
        "legend.facecolor":  CARD,
        "legend.edgecolor":  BORDER,
        "legend.labelcolor": TEXT,
        "axes.spines.top":   False,
        "axes.spines.right": False,
    })


def embed(fig, frame):
    c = FigureCanvasTkAgg(fig, master=frame)
    c.draw()
    c.get_tk_widget().pack(fill="both", expand=True, padx=6, pady=6)


def fitness_chart(ax, result):
    best = result["fitness_history"]
    avg  = result["avg_history"]
    x    = range(1, len(best) + 1)

    ax.plot(x, best, color=ACCENT, linewidth=2, label="Best")
    ax.plot(x, avg,  color=GOLD, linewidth=1.5, linestyle="--", alpha=0.8, label="Average")
    ax.fill_between(x, avg, best, color=ACCENT, alpha=0.07)

    ax.set_title("Fitness over Generations", fontsize=11, pad=10)
    ax.set_xlabel("Generation", fontsize=9)
    ax.set_ylabel("Fitness", fontsize=9)
    ax.set_xlim(1, len(best))
    ax.set_ylim(0, 1.05)
    ax.legend(fontsize=8, loc="lower right")
    ax.grid(True, axis="y")

    ax.annotate(
        f"{best[-1]:.4f}",
        xy=(len(best), best[-1]),
        xytext=(-40, 10),
        textcoords="offset points",
        fontsize=8, color=ACC2,
        arrowprops=dict(arrowstyle="->", color=ACCENT, lw=1)
    )


def macros_bar(ax, result):
    p = result["profile"]
    t = result["totals"]

    labels   = ["Calories\n(kcal)", "Protein\n(g)", "Carbs\n(g)", "Fats\n(g)"]
    targets  = [p["target_calories"], p["protein_g"], p["carbs_g"], p["fats_g"]]
    achieved = [t["calories"],        t["protein"],   t["carbs"],   t["fats"]]

    y = np.arange(len(labels))
    h = 0.35

    ax.barh(y + h/2, targets,  height=h, color=MUTED, alpha=0.7, label="Target")
    bars = ax.barh(y - h/2, achieved, height=h,
                   color=[ACCENT if a <= tgt * 1.05 else RED
                          for a, tgt in zip(achieved, targets)],
                   alpha=0.9, label="Achieved")

    ax.set_yticks(y)
    ax.set_yticklabels(labels, fontsize=9)
    ax.set_title("Achieved vs Target", fontsize=11, pad=10)
    ax.set_xlabel("Amount", fontsize=9)
    ax.legend(fontsize=8)
    ax.grid(True, axis="x")

    for bar in bars:
        w = bar.get_width()
        ax.text(w + max(targets) * 0.01, bar.get_y() + bar.get_height() / 2,
                f"{w:.0f}", va="center", fontsize=7.5, color=TEXT2)


def calorie_donut(ax, result):
    bd     = get_meal_breakdown(result)
    meals  = list(bd.keys())
    cals   = [bd[m]["calories"] for m in meals]
    colors = [MEAL_COLORS[m] for m in meals]

    wedges, texts, pcts = ax.pie(
        cals, labels=meals, colors=colors,
        autopct="%1.1f%%", startangle=90, pctdistance=0.78,
        wedgeprops=dict(width=0.55, edgecolor=BG, linewidth=2)
    )
    for t in texts:
        t.set_color(TEXT2)
        t.set_fontsize(8)
    for p in pcts:
        p.set_color(BG)
        p.set_fontsize(7.5)
        p.set_fontweight("bold")

    ax.text(0, 0, f"{sum(cals):.0f}\nkcal",
            ha="center", va="center", fontsize=10,
            color=ACCENT, fontweight="bold")
    ax.set_title("Calories by Meal", fontsize=11, pad=10)


def macro_pie(ax, result):
    t      = result["totals"]
    sizes  = [t["protein"] * 4, t["carbs"] * 4, t["fats"] * 9]
    labels = ["Protein", "Carbs", "Fats"]
    colors = [ACCENT, GOLD, "#e07c5c"]

    wedges, texts, pcts = ax.pie(
        sizes, labels=labels, colors=colors,
        autopct="%1.1f%%", startangle=120, pctdistance=0.75,
        wedgeprops=dict(width=0.55, edgecolor=BG, linewidth=2)
    )
    for t in texts:
        t.set_color(TEXT2)
        t.set_fontsize(9)
    for p in pcts:
        p.set_color(BG)
        p.set_fontsize(8)
        p.set_fontweight("bold")

    ax.set_title("Macro Energy Split", fontsize=11, pad=10)


def meal_macros_bar(ax, result):
    bd       = get_meal_breakdown(result)
    meals    = list(bd.keys())
    proteins = [bd[m]["protein"] for m in meals]
    carbs    = [bd[m]["carbs"]   for m in meals]
    fats     = [bd[m]["fats"]    for m in meals]
    x        = np.arange(len(meals))

    ax.bar(x, proteins, width=0.55, label="Protein", color=ACCENT)
    ax.bar(x, carbs,    width=0.55, bottom=proteins, label="Carbs", color=GOLD)
    ax.bar(x, fats,     width=0.55,
           bottom=[p + c for p, c in zip(proteins, carbs)],
           label="Fats", color="#e07c5c")

    ax.set_xticks(x)
    ax.set_xticklabels(meals, fontsize=8)
    ax.set_ylabel("Grams", fontsize=9)
    ax.set_title("Macros per Meal", fontsize=11, pad=10)
    ax.legend(fontsize=8)
    ax.grid(True, axis="y")


def bmi_gauge(ax, result):
    bmi   = result["profile"]["bmi"]
    label = result["profile"]["bmi_category"]

    segments = [
        (8.5,  "#5dade2", "Underweight"),
        (6.5,  ACCENT,    "Normal"),
        (5.0,  GOLD,      "Overweight"),
        (10.0, RED,       "Obese"),
    ]

    ax.set_xlim(-1.3, 1.3)
    ax.set_ylim(-0.2, 1.3)
    ax.axis("off")

    current = 10.0
    for width, color, _ in segments:
        t0 = np.pi - (current - 10) / 30 * np.pi
        t1 = np.pi - (current + width - 10) / 30 * np.pi
        t  = np.linspace(t0, t1, 60)
        ax.plot(np.cos(t), np.sin(t), color=color, linewidth=14, solid_capstyle="butt")
        current += width

    angle = np.pi - (max(10, min(40, bmi)) - 10) / 30 * np.pi
    ax.annotate("", xy=(0.7 * np.cos(angle), 0.7 * np.sin(angle)),
                xytext=(0, 0),
                arrowprops=dict(arrowstyle="-|>", color=TEXT, lw=2, mutation_scale=12))
    ax.plot(0, 0, "o", color=TEXT, markersize=6, zorder=5)

    ax.text(0, 0.42, f"{bmi}", ha="center", va="center",
            fontsize=22, fontweight="bold", color=ACCENT)
    ax.text(0, 0.22, label, ha="center", va="center", fontsize=9, color=TEXT2)
    ax.set_title("BMI", fontsize=11, pad=4)

    patches = [mpatches.Patch(color=c, label=l) for _, c, l in segments]
    ax.legend(handles=patches, loc="lower center", ncol=4,
              fontsize=7, framealpha=0.3, bbox_to_anchor=(0.5, -0.05))


def show_visualization(result):
    set_theme()

    win = tk.Toplevel()
    win.title("NutriGen — Visualisation")
    win.geometry("1100x750")
    win.configure(bg=BG)
    win.resizable(True, True)

    header = tk.Frame(win, bg=CARD, height=48)
    header.pack(fill="x")
    header.pack_propagate(False)
    tk.Label(header, text="✦ NutriGen — Visualisation", bg=CARD, fg=ACCENT,
             font=("Georgia", 13, "bold")).pack(side="left", padx=20, pady=12)
    tk.Label(header, text=f"Match: {round(result['fitness_score'] * 100, 1)}%",
             bg=CARD, fg=TEXT2, font=("Trebuchet MS", 9)).pack(side="right", padx=20)
    tk.Frame(win, bg=BORDER, height=1).pack(fill="x")

    tab_bar = tk.Frame(win, bg=CARD2, height=36)
    tab_bar.pack(fill="x")
    tab_bar.pack_propagate(False)

    body = tk.Frame(win, bg=BG)
    body.pack(fill="both", expand=True)

    frames  = {}
    btn_map = {}

    tabs = [
        ("Overview",     "overview"),
        ("GA Evolution", "ga"),
        ("Macros",       "macros"),
        ("Meals",        "meals"),
        ("BMI",          "bmi"),
    ]

    for _, key in tabs:
        frames[key] = tk.Frame(body, bg=BG)

    def switch(key):
        for f in frames.values():
            f.pack_forget()
        frames[key].pack(fill="both", expand=True)
        for k, b in btn_map.items():
            b.config(fg=ACCENT if k == key else TEXT2,
                     bg=CARD  if k == key else CARD2)

    for label, key in tabs:
        b = tk.Button(tab_bar, text=label, bg=CARD2, fg=TEXT2,
                      font=("Trebuchet MS", 9, "bold"),
                      relief="flat", bd=0, padx=16, pady=8,
                      activebackground=CARD, activeforeground=ACCENT,
                      cursor="hand2",
                      command=lambda k=key: switch(k))
        b.pack(side="left")
        btn_map[key] = b

    fig1 = plt.figure(figsize=(10, 6.5), facecolor=BG)
    gs   = GridSpec(2, 2, figure=fig1, hspace=0.42, wspace=0.34,
                    left=0.07, right=0.97, top=0.93, bottom=0.08)
    fitness_chart(fig1.add_subplot(gs[0, :]), result)
    calorie_donut(fig1.add_subplot(gs[1, 0]), result)
    macro_pie(    fig1.add_subplot(gs[1, 1]), result)
    embed(fig1, frames["overview"])

    fig2, ax2 = plt.subplots(figsize=(10, 5.5), facecolor=BG)
    ax2.set_facecolor(CARD)
    fitness_chart(ax2, result)
    fig2.tight_layout(pad=1.8)
    embed(fig2, frames["ga"])

    fig3, (ax3a, ax3b) = plt.subplots(1, 2, figsize=(10, 5.2), facecolor=BG)
    ax3a.set_facecolor(CARD)
    ax3b.set_facecolor(CARD)
    macros_bar(ax3a, result)
    macro_pie( ax3b, result)
    fig3.tight_layout(pad=1.8)
    embed(fig3, frames["macros"])

    fig4, (ax4a, ax4b) = plt.subplots(1, 2, figsize=(10, 5.2), facecolor=BG)
    ax4a.set_facecolor(CARD)
    ax4b.set_facecolor(CARD)
    calorie_donut(  ax4a, result)
    meal_macros_bar(ax4b, result)
    fig4.tight_layout(pad=1.8)
    embed(fig4, frames["meals"])

    fig5, ax5 = plt.subplots(figsize=(6, 4), facecolor=BG)
    ax5.set_facecolor(BG)
    bmi_gauge(ax5, result)
    fig5.tight_layout(pad=1.5)
    embed(fig5, frames["bmi"])

    switch("overview")
    win.mainloop()


if __name__ == "__main__":
    from meal_planner import generate_meal_plan
    root = tk.Tk()
    root.withdraw()
    res = generate_meal_plan(
        weight_kg=75, height_cm=175, age=21,
        gender="Male",
        activity_level="Moderately Active (exercise 3-5 days/week)",
        goal="Weight Loss",
        generations=80,
    )
    show_visualization(res)
