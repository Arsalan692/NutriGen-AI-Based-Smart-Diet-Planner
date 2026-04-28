ACTIVITY_LEVELS = {
    "Sedentary (little or no exercise)":          1.2,
    "Lightly Active (exercise 1-3 days/week)":    1.375,
    "Moderately Active (exercise 3-5 days/week)": 1.55,
    "Very Active (exercise 6-7 days/week)":       1.725,
    "Extra Active (physical job or 2x training)": 1.9,
}

GOALS = {
    "Weight Loss":  -500,
    "Maintenance":     0,
    "Muscle Gain":  +300,
}

MACRO_SPLITS = {
    "Weight Loss":  {"protein": 0.40, "carbs": 0.35, "fats": 0.25},
    "Maintenance":  {"protein": 0.30, "carbs": 0.40, "fats": 0.30},
    "Muscle Gain":  {"protein": 0.35, "carbs": 0.45, "fats": 0.20},
}


def calculate_bmr(weight_kg, height_cm, age, gender):
    if gender == "Male":
        return round((10 * weight_kg) + (6.25 * height_cm) - (5 * age) + 5, 1)
    else:
        return round((10 * weight_kg) + (6.25 * height_cm) - (5 * age) - 161, 1)


def calculate_tdee(bmr, activity_level):
    multiplier = ACTIVITY_LEVELS.get(activity_level, 1.2)
    return round(bmr * multiplier, 1)


def calculate_target_calories(tdee, goal):
    adjustment = GOALS.get(goal, 0)
    return round(max(tdee + adjustment, 1200), 1)


def calculate_macros(target_calories, goal):
    split = MACRO_SPLITS.get(goal, MACRO_SPLITS["Maintenance"])
    return {
        "protein_g": round((target_calories * split["protein"]) / 4, 1),
        "carbs_g":   round((target_calories * split["carbs"])   / 4, 1),
        "fats_g":    round((target_calories * split["fats"])    / 9, 1),
    }


def calculate_bmi(weight_kg, height_cm):
    bmi = round(weight_kg / (height_cm / 100) ** 2, 1)
    if bmi < 18.5:
        label = "Underweight"
    elif bmi < 25:
        label = "Normal weight"
    elif bmi < 30:
        label = "Overweight"
    else:
        label = "Obese"
    return bmi, label


def get_full_profile(weight_kg, height_cm, age, gender, activity_level, goal):
    bmr        = calculate_bmr(weight_kg, height_cm, age, gender)
    tdee       = calculate_tdee(bmr, activity_level)
    target_cal = calculate_target_calories(tdee, goal)
    macros     = calculate_macros(target_cal, goal)
    bmi, bmi_label = calculate_bmi(weight_kg, height_cm)

    return {
        "weight_kg":       weight_kg,
        "height_cm":       height_cm,
        "age":             age,
        "gender":          gender,
        "activity_level":  activity_level,
        "goal":            goal,
        "bmr":             bmr,
        "tdee":            tdee,
        "target_calories": target_cal,
        "protein_g":       macros["protein_g"],
        "carbs_g":         macros["carbs_g"],
        "fats_g":          macros["fats_g"],
        "bmi":             bmi,
        "bmi_category":    bmi_label,
    }
