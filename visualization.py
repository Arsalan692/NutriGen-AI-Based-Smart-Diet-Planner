import customtkinter as ctk
import tkinter as tk
import matplotlib
matplotlib.use("TkAgg")
import matplotlib.pyplot as plt
import matplotlib.patches as mpatches
from matplotlib.backends.backend_tkagg import FigureCanvasTkAgg
from matplotlib.gridspec import GridSpec
import numpy as np

from meal_planner import get_meal_breakdown
from theme import *

# ── Matplotlib dark theme ───────────────────
def set_theme():
    plt.rcParams.update({
        "figure.facecolor":  BG_DARK,
        "axes.facecolor":    BG_CARD,
        "axes.edgecolor":    BORDER,
        "axes.labelcolor":   TEXT_SECONDARY,
        "axes.titlecolor":   TEXT_PRIMARY,
        "xtick.color":       TEXT_MUTED,
        "ytick.color":       TEXT_MUTED,
        "text.color":        TEXT_PRIMARY,
        "grid.color":        BORDER,
        "grid.alpha":        0.5,
        "legend.facecolor":  BG_CARD,
        "legend.edgecolor":  BORDER,
        "legend.labelcolor": TEXT_SECONDARY,
        "axes.spines.top":   False,
        "axes.spines.right": False,
        "axes.linewidth":    1.2,
        "font.family":       "Segoe UI",
    })


def embed(fig, frame):
    c = FigureCanvasTkAgg(fig, master=frame)
    c.draw()
    c.get_tk_widget().pack(fill="both", expand=True, padx=6, pady=6)


def fitness_chart(ax, result):
    best = result["fitness_history"]
    avg  = result["avg_history"]
    x    = range(1, len(best) + 1)

    ax.plot(x, best, color=EMERALD, linewidth=2.2, label="Best", zorder=3)
    ax.plot(x, avg,  color=AMBER, linewidth=1.5, linestyle="--", alpha=0.7, label="Average")
    ax.fill_between(x, avg, best, color=EMERALD, alpha=0.08)

    ax.set_title("Fitness over Generations", fontsize=12, pad=12, fontweight="bold")
    ax.set_xlabel("Generation", fontsize=9)
    ax.set_ylabel("Fitness", fontsize=9)
    ax.set_xlim(1, len(best))
    ax.set_ylim(0, 1.05)
    ax.legend(fontsize=8, loc="lower right")
    ax.grid(True, axis="y", alpha=0.3)

    ax.annotate(
        f"{best[-1]:.4f}",
        xy=(len(best), best[-1]),
        xytext=(-44, 12), textcoords="offset points",
        fontsize=8, color=EMERALD_L, fontweight="bold",
        arrowprops=dict(arrowstyle="->", color=EMERALD, lw=1.2)
    )


def macros_bar(ax, result):
    p = result["profile"]
    t = result["totals"]

    labels   = ["Calories\n(kcal)", "Protein\n(g)", "Carbs\n(g)", "Fats\n(g)"]
    targets  = [p["target_calories"], p["protein_g"], p["carbs_g"], p["fats_g"]]
    achieved = [t["calories"],        t["protein"],   t["carbs"],   t["fats"]]
    colors   = [AMBER, EMERALD, SKY, ROSE]

    y = np.arange(len(labels))
    h = 0.35

    ax.barh(y + h/2, targets,  height=h, color=BORDER_LIGHT, alpha=0.6, label="Target")
    bars = ax.barh(y - h/2, achieved, height=h,
                   color=[c if a <= tgt*1.05 else ROSE for a, tgt, c in zip(achieved, targets, colors)],
                   alpha=0.9, label="Achieved")

    ax.set_yticks(y)
    ax.set_yticklabels(labels, fontsize=9)
    ax.set_title("Achieved vs Target", fontsize=12, pad=12, fontweight="bold")
    ax.set_xlabel("Amount", fontsize=9)
    ax.legend(fontsize=8)
    ax.grid(True, axis="x", alpha=0.3)

    for bar in bars:
        w = bar.get_width()
        ax.text(w + max(targets)*0.01, bar.get_y() + bar.get_height()/2,
                f"{w:.0f}", va="center", fontsize=7.5, color=TEXT_SECONDARY)


def calorie_donut(ax, result):
    bd     = get_meal_breakdown(result)
    meals  = list(bd.keys())
    cals   = [bd[m]["calories"] for m in meals]
    colors = [MEAL_ACCENT.get(m, EMERALD) for m in meals]

    wedges, texts, pcts = ax.pie(
        cals, labels=meals, colors=colors,
        autopct="%1.1f%%", startangle=90, pctdistance=0.78,
        wedgeprops=dict(width=0.55, edgecolor=BG_DARK, linewidth=2.5)
    )
    for t in texts:
        t.set_color(TEXT_SECONDARY)
        t.set_fontsize(8)
    for p in pcts:
        p.set_color(TEXT_PRIMARY)
        p.set_fontsize(7.5)
        p.set_fontweight("bold")

    ax.text(0, 0, f"{sum(cals):.0f}\nkcal",
            ha="center", va="center", fontsize=11,
            color=EMERALD, fontweight="bold")
    ax.set_title("Calories by Meal", fontsize=12, pad=12, fontweight="bold")


def macro_pie(ax, result):
    t      = result["totals"]
    sizes  = [t["protein"]*4, t["carbs"]*4, t["fats"]*9]
    labels = ["Protein", "Carbs", "Fats"]
    colors = [EMERALD, AMBER, ROSE]

    wedges, texts, pcts = ax.pie(
        sizes, labels=labels, colors=colors,
        autopct="%1.1f%%", startangle=120, pctdistance=0.75,
        wedgeprops=dict(width=0.55, edgecolor=BG_DARK, linewidth=2.5)
    )
    for t in texts:
        t.set_color(TEXT_SECONDARY)
        t.set_fontsize(9)
    for p in pcts:
        p.set_color(TEXT_PRIMARY)
        p.set_fontsize(8)
        p.set_fontweight("bold")

    ax.set_title("Macro Energy Split", fontsize=12, pad=12, fontweight="bold")


def meal_macros_bar(ax, result):
    bd       = get_meal_breakdown(result)
    meals    = list(bd.keys())
    proteins = [bd[m]["protein"] for m in meals]
    carbs    = [bd[m]["carbs"]   for m in meals]
    fats     = [bd[m]["fats"]    for m in meals]
    x        = np.arange(len(meals))

    ax.bar(x, proteins, width=0.55, label="Protein", color=EMERALD)
    ax.bar(x, carbs,    width=0.55, bottom=proteins, label="Carbs", color=AMBER)
    ax.bar(x, fats,     width=0.55,
           bottom=[p+c for p,c in zip(proteins, carbs)],
           label="Fats", color=ROSE)

    ax.set_xticks(x)
    ax.set_xticklabels(meals, fontsize=8)
    ax.set_ylabel("Grams", fontsize=9)
    ax.set_title("Macros per Meal", fontsize=12, pad=12, fontweight="bold")
    ax.legend(fontsize=8)
    ax.grid(True, axis="y", alpha=0.3)


def bmi_gauge(ax, result):
    bmi   = result["profile"]["bmi"]
    label = result["profile"]["bmi_category"]

    segments = [
        (8.5,  SKY,     "Underweight"),
        (6.5,  EMERALD, "Normal"),
        (5.0,  AMBER,   "Overweight"),
        (10.0, ROSE,    "Obese"),
    ]

    ax.set_xlim(-1.3, 1.3)
    ax.set_ylim(-0.2, 1.3)
    ax.axis("off")

    current = 10.0
    for width, color, _ in segments:
        t0 = np.pi - (current - 10) / 30 * np.pi
        t1 = np.pi - (current + width - 10) / 30 * np.pi
        t  = np.linspace(t0, t1, 60)
        ax.plot(np.cos(t), np.sin(t), color=color, linewidth=16, solid_capstyle="butt")
        current += width

    angle = np.pi - (max(10, min(40, bmi)) - 10) / 30 * np.pi
    ax.annotate("", xy=(0.7*np.cos(angle), 0.7*np.sin(angle)),
                xytext=(0, 0),
                arrowprops=dict(arrowstyle="-|>", color=TEXT_PRIMARY, lw=2.2, mutation_scale=13))
    ax.plot(0, 0, "o", color=TEXT_PRIMARY, markersize=7, zorder=5)

    ax.text(0, 0.42, f"{bmi}", ha="center", va="center",
            fontsize=24, fontweight="bold", color=EMERALD)
    ax.text(0, 0.22, label, ha="center", va="center", fontsize=9, color=TEXT_SECONDARY)
    ax.set_title("BMI", fontsize=12, pad=6, fontweight="bold")

    patches = [mpatches.Patch(color=c, label=l) for _, c, l in segments]
    ax.legend(handles=patches, loc="lower center", ncol=4,
              fontsize=7, framealpha=0.3, bbox_to_anchor=(0.5, -0.05))


def show_visualization(result):
    set_theme()

    win = ctk.CTkToplevel()
    win.title("NutriGen — Visualisation")
    win.geometry("1100x750")
    win.configure(fg_color=BG_DARK)
    win.resizable(True, True)

    # header
    header = ctk.CTkFrame(win, height=52, fg_color=BG_MID, corner_radius=0)
    header.pack(fill="x")
    header.pack_propagate(False)
    ctk.CTkLabel(header, text="📊  NutriGen — Visualisation", font=F_H2,
                 text_color=EMERALD).pack(side="left", padx=20, pady=14)
    ctk.CTkLabel(header, text=f"Match: {round(result['fitness_score']*100,1)}%",
                 font=F_SMALL_B, text_color=TEXT_SECONDARY).pack(side="right", padx=20)

    # tab bar
    tab_bar = ctk.CTkFrame(win, height=44, fg_color=BG_CARD, corner_radius=0)
    tab_bar.pack(fill="x")
    tab_bar.pack_propagate(False)

    body = ctk.CTkFrame(win, fg_color=BG_DARK, corner_radius=0)
    body.pack(fill="both", expand=True)

    frames  = {}
    btn_map = {}

    tabs = [
        ("📋 Overview",     "overview"),
        ("🧬 GA Evolution", "ga"),
        ("💪 Macros",       "macros"),
        ("🍱 Meals",        "meals"),
        ("📏 BMI",          "bmi"),
    ]

    for _, key in tabs:
        frames[key] = ctk.CTkFrame(body, fg_color=BG_DARK, corner_radius=0)

    def switch(key):
        for f in frames.values():
            f.pack_forget()
        frames[key].pack(fill="both", expand=True)
        for k, b in btn_map.items():
            if k == key:
                b.configure(fg_color=EMERALD_D, text_color=TEXT_PRIMARY)
            else:
                b.configure(fg_color="transparent", text_color=TEXT_SECONDARY)

    for label, key in tabs:
        b = ctk.CTkButton(tab_bar, text=label, font=F_SMALL_B,
                          fg_color="transparent", text_color=TEXT_SECONDARY,
                          hover_color=BG_CARD2, corner_radius=8,
                          height=34, command=lambda k=key: switch(k))
        b.pack(side="left", padx=3, pady=5)
        btn_map[key] = b

    # ── Overview ────────────────────────────────
    fig1 = plt.figure(figsize=(10, 6.5), facecolor=BG_DARK)
    gs = GridSpec(2, 2, figure=fig1, hspace=0.42, wspace=0.34,
                  left=0.07, right=0.97, top=0.93, bottom=0.08)
    fitness_chart(fig1.add_subplot(gs[0, :]), result)
    calorie_donut(fig1.add_subplot(gs[1, 0]), result)
    macro_pie(    fig1.add_subplot(gs[1, 1]), result)
    embed(fig1, frames["overview"])

    # ── GA Evolution ────────────────────────────
    fig2, ax2 = plt.subplots(figsize=(10, 5.5), facecolor=BG_DARK)
    ax2.set_facecolor(BG_CARD)
    fitness_chart(ax2, result)
    fig2.tight_layout(pad=1.8)
    embed(fig2, frames["ga"])

    # ── Macros ──────────────────────────────────
    fig3, (ax3a, ax3b) = plt.subplots(1, 2, figsize=(10, 5.2), facecolor=BG_DARK)
    ax3a.set_facecolor(BG_CARD)
    ax3b.set_facecolor(BG_CARD)
    macros_bar(ax3a, result)
    macro_pie( ax3b, result)
    fig3.tight_layout(pad=1.8)
    embed(fig3, frames["macros"])

    # ── Meals ───────────────────────────────────
    fig4, (ax4a, ax4b) = plt.subplots(1, 2, figsize=(10, 5.2), facecolor=BG_DARK)
    ax4a.set_facecolor(BG_CARD)
    ax4b.set_facecolor(BG_CARD)
    calorie_donut(  ax4a, result)
    meal_macros_bar(ax4b, result)
    fig4.tight_layout(pad=1.8)
    embed(fig4, frames["meals"])

    # ── BMI ─────────────────────────────────────
    fig5, ax5 = plt.subplots(figsize=(6, 4), facecolor=BG_DARK)
    ax5.set_facecolor(BG_DARK)
    bmi_gauge(ax5, result)
    fig5.tight_layout(pad=1.5)
    embed(fig5, frames["bmi"])

    switch("overview")
    win.mainloop()


if __name__ == "__main__":
    from meal_planner import generate_meal_plan
    root = ctk.CTk()
    root.withdraw()
    res = generate_meal_plan(
        weight_kg=75, height_cm=175, age=21,
        gender="Male",
        activity_level="Moderately Active (exercise 3-5 days/week)",
        goal="Weight Loss",
        generations=80,
    )
    show_visualization(res)
