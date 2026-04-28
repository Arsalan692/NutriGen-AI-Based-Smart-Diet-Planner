from data_loader import load_foods, exclude_foods
from calorie_calculator import get_full_profile, ACTIVITY_LEVELS, GOALS
from genetic_algorithm import GeneticAlgorithm


def generate_meal_plan(weight_kg, height_cm, age, gender, activity_level, goal,
                       excluded_foods=None, population_size=50, generations=100,
                       callback=None):

    all_foods = load_foods()

    if excluded_foods:
        all_foods = exclude_foods(all_foods, excluded_foods)

    profile = get_full_profile(weight_kg, height_cm, age, gender, activity_level, goal)

    ga = GeneticAlgorithm(
        foods            = all_foods,
        target_calories  = profile["target_calories"],
        target_protein   = profile["protein_g"],
        target_carbs     = profile["carbs_g"],
        target_fats      = profile["fats_g"],
        population_size  = population_size,
        generations      = generations,
        callback         = callback,
    )

    best_plan, best_fitness = ga.run()
    totals = ga.get_totals(best_plan)

    return {
        "profile":         profile,
        "meal_plan":       best_plan,
        "totals":          totals,
        "fitness_score":   best_fitness,
        "fitness_history": ga.fitness_history,
        "avg_history":     ga.avg_fitness_history,
    }


def format_meal_plan(result):
    profile = result["profile"]
    plan    = result["meal_plan"]
    totals  = result["totals"]
    score   = result["fitness_score"]

    lines = []
    lines.append("=" * 55)
    lines.append("         NUTRIGEN — PERSONALIZED DIET PLAN")
    lines.append("=" * 55)

    lines.append(f"\n  Goal            : {profile['goal']}")
    lines.append(f"  Target Calories : {profile['target_calories']} kcal")
    lines.append(f"  Protein Target  : {profile['protein_g']} g")
    lines.append(f"  Carbs Target    : {profile['carbs_g']} g")
    lines.append(f"  Fats Target     : {profile['fats_g']} g")
    lines.append(f"  BMI             : {profile['bmi']} ({profile['bmi_category']})")
    lines.append(f"  Optimization    : {round(score * 100, 1)}% match")

    for meal, items in plan.items():
        lines.append(f"\n  {'─' * 45}")
        lines.append(f"  {meal.upper()}")
        lines.append(f"  {'─' * 45}")
        meal_cals = 0
        for food, grams in items:
            item_cals = round(food["calories"] * grams / 100, 1)
            meal_cals += item_cals
            lines.append(f"    {food['name']:<35} {grams:>4}g   {item_cals:>6} kcal")
        lines.append(f"    {'Meal Total':<35} {'':>4}    {round(meal_cals):>6} kcal")

    lines.append(f"\n  {'=' * 45}")
    lines.append("  DAILY TOTALS")
    lines.append(f"  {'=' * 45}")
    lines.append(f"    Calories : {totals['calories']} kcal  (target: {profile['target_calories']})")
    lines.append(f"    Protein  : {totals['protein']} g      (target: {profile['protein_g']}g)")
    lines.append(f"    Carbs    : {totals['carbs']} g      (target: {profile['carbs_g']}g)")
    lines.append(f"    Fats     : {totals['fats']} g       (target: {profile['fats_g']}g)")
    lines.append(f"    Fiber    : {totals['fiber']} g")
    lines.append("=" * 55)

    return "\n".join(lines)


def get_meal_breakdown(result):
    plan = result["meal_plan"]
    breakdown = {}
    for meal, items in plan.items():
        meal_data = {
            "items": [],
            "calories": 0,
            "protein":  0,
            "carbs":    0,
            "fats":     0,
        }
        for food, grams in items:
            s = grams / 100.0
            item_cals = round(food["calories"] * s, 1)
            meal_data["items"].append({
                "name":     food["name"],
                "category": food["category"],
                "grams":    grams,
                "calories": item_cals,
                "protein":  round(food["protein"] * s, 1),
                "carbs":    round(food["carbs"]   * s, 1),
                "fats":     round(food["fats"]    * s, 1),
            })
            meal_data["calories"] += item_cals
            meal_data["protein"]  += round(food["protein"] * s, 1)
            meal_data["carbs"]    += round(food["carbs"]   * s, 1)
            meal_data["fats"]     += round(food["fats"]    * s, 1)

        meal_data["calories"] = round(meal_data["calories"], 1)
        meal_data["protein"]  = round(meal_data["protein"],  1)
        meal_data["carbs"]    = round(meal_data["carbs"],    1)
        meal_data["fats"]     = round(meal_data["fats"],     1)
        breakdown[meal] = meal_data

    return breakdown


if __name__ == "__main__":
    print("Generating diet plan... please wait.\n")

    result = generate_meal_plan(
        weight_kg      = 75,
        height_cm      = 175,
        age            = 21,
        gender         = "Male",
        activity_level = "Moderately Active (exercise 3-5 days/week)",
        goal           = "Weight Loss",
        excluded_foods = ["Garlic", "Bitter Gourd / Karela"],
        generations    = 100,
    )

    print(format_meal_plan(result))

    print("\nPer-meal breakdown:")
    breakdown = get_meal_breakdown(result)
    for meal, data in breakdown.items():
        print(f"\n  {meal} — {data['calories']} kcal | "
              f"P:{data['protein']}g  C:{data['carbs']}g  F:{data['fats']}g")
