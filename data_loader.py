import csv
import os


def _find_csv():
    candidates = [
        os.path.join(os.path.dirname(os.path.abspath(__file__)), "halal_foods.csv"),
        os.path.join(os.getcwd(), "halal_foods.csv"),
    ]
    for path in candidates:
        if os.path.isfile(path):
            return path
    return candidates[0]

CSV_PATH = _find_csv()


def load_foods():
    foods = []
    with open(CSV_PATH, newline="", encoding="utf-8") as f:
        reader = csv.DictReader(f)
        for row in reader:
            foods.append({
                "name":     row["food_name"].strip(),
                "category": row["category"].strip(),
                "calories": float(row["calories"]),
                "protein":  float(row["protein"]),
                "carbs":    float(row["carbs"]),
                "fats":     float(row["fats"]),
                "fiber":    float(row["fiber"]),
            })
    return foods


def get_categories(foods):
    return sorted(set(f["category"] for f in foods))


def filter_by_category(foods, category):
    return [f for f in foods if f["category"] == category]


def exclude_foods(foods, excluded_names):
    blocked = [n.lower() for n in excluded_names]
    return [f for f in foods if f["name"].lower() not in blocked]


def search_foods(foods, query):
    q = query.lower()
    return [f for f in foods if q in f["name"].lower()]


def get_food_by_name(foods, name):
    for f in foods:
        if f["name"].lower() == name.lower():
            return f
    return None


def scale_nutrition(food, grams):
    s = grams / 100.0
    return {
        "name":     food["name"],
        "grams":    grams,
        "calories": round(food["calories"] * s, 1),
        "protein":  round(food["protein"]  * s, 1),
        "carbs":    round(food["carbs"]    * s, 1),
        "fats":     round(food["fats"]     * s, 1),
        "fiber":    round(food["fiber"]    * s, 1),
    }