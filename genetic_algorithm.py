import random
import copy

MEAL_SLOTS = {
    "Breakfast": {"count": 3, "grams_range": (80, 200)},
    "Lunch":     {"count": 4, "grams_range": (100, 250)},
    "Dinner":    {"count": 4, "grams_range": (100, 250)},
    "Snack 1":   {"count": 2, "grams_range": (30, 100)},
    "Snack 2":   {"count": 2, "grams_range": (30, 100)},
}

MEAL_CATEGORIES = {
    "Breakfast": ["Grains", "Dairy", "Fruits", "Protein", "Nuts & Seeds", "Beverages"],
    "Lunch":     ["Grains", "Protein", "Vegetables", "Legumes", "Dairy"],
    "Dinner":    ["Grains", "Protein", "Vegetables", "Legumes", "Dairy"],
    "Snack 1":   ["Fruits", "Nuts & Seeds", "Dairy", "Other", "Beverages"],
    "Snack 2":   ["Fruits", "Nuts & Seeds", "Dairy", "Other", "Beverages"],
}


class GeneticAlgorithm:
    def __init__(self, foods, target_calories, target_protein, target_carbs, target_fats,
                 population_size=50, generations=100, mutation_rate=0.15,
                 crossover_rate=0.8, elitism_count=5, callback=None):

        self.foods           = foods
        self.target_calories = target_calories
        self.target_protein  = target_protein
        self.target_carbs    = target_carbs
        self.target_fats     = target_fats
        self.pop_size        = population_size
        self.generations     = generations
        self.mutation_rate   = mutation_rate
        self.crossover_rate  = crossover_rate
        self.elitism_count   = elitism_count
        self.callback        = callback

        # group foods by category for faster lookup
        self.cat_map = {}
        for f in foods:
            self.cat_map.setdefault(f["category"], []).append(f)

        self.fitness_history     = []
        self.avg_fitness_history = []

    def _pick_food(self, allowed_cats):
        pool = []
        for cat in allowed_cats:
            pool.extend(self.cat_map.get(cat, []))
        return random.choice(pool) if pool else random.choice(self.foods)

    def _pick_grams(self, grams_range):
        low, high = grams_range
        return random.randrange(low, high + 1, 5)

    def _make_plan(self):
        plan = {}
        for meal, cfg in MEAL_SLOTS.items():
            items = []
            for _ in range(cfg["count"]):
                food  = self._pick_food(MEAL_CATEGORIES[meal])
                grams = self._pick_grams(cfg["grams_range"])
                items.append((food, grams))
            plan[meal] = items
        return plan

    def _init_population(self):
        return [self._make_plan() for _ in range(self.pop_size)]

    def get_totals(self, plan):
        totals = {"calories": 0, "protein": 0, "carbs": 0, "fats": 0, "fiber": 0}
        for items in plan.values():
            for food, grams in items:
                s = grams / 100.0
                totals["calories"] += food["calories"] * s
                totals["protein"]  += food["protein"]  * s
                totals["carbs"]    += food["carbs"]    * s
                totals["fats"]     += food["fats"]     * s
                totals["fiber"]    += food["fiber"]    * s
        return {k: round(v, 1) for k, v in totals.items()}

    def fitness(self, plan):
        t = self.get_totals(plan)

        cal_dev  = abs(t["calories"] - self.target_calories) / self.target_calories
        prot_dev = abs(t["protein"]  - self.target_protein)  / max(self.target_protein, 1)
        carb_dev = abs(t["carbs"]    - self.target_carbs)    / max(self.target_carbs, 1)
        fat_dev  = abs(t["fats"]     - self.target_fats)     / max(self.target_fats, 1)

        penalty = 0.40 * cal_dev + 0.30 * prot_dev + 0.20 * carb_dev + 0.10 * fat_dev
        return round(1 / (1 + penalty), 6)

    def _tournament(self, population, fitnesses, k=3):
        picks = random.sample(range(len(population)), k)
        winner = max(picks, key=lambda i: fitnesses[i])
        return copy.deepcopy(population[winner])

    def _crossover(self, p1, p2):
        if random.random() > self.crossover_rate:
            return copy.deepcopy(p1), copy.deepcopy(p2)
        c1, c2 = {}, {}
        for meal in MEAL_SLOTS:
            if random.random() < 0.5:
                c1[meal] = copy.deepcopy(p1[meal])
                c2[meal] = copy.deepcopy(p2[meal])
            else:
                c1[meal] = copy.deepcopy(p2[meal])
                c2[meal] = copy.deepcopy(p1[meal])
        return c1, c2

    def _mutate(self, plan):
        for meal, items in plan.items():
            for i, (food, grams) in enumerate(items):
                if random.random() < self.mutation_rate:
                    choice = random.choice(["swap", "grams"])

                    if choice == "swap":
                        new_food = self._pick_food(MEAL_CATEGORIES[meal])
                        plan[meal][i] = (new_food, grams)

                    elif choice == "grams":
                        low, high = MEAL_SLOTS[meal]["grams_range"]
                        delta = random.randint(-30, 30)
                        new_grams = max(low, min(high, grams + delta))
                        plan[meal][i] = (food, new_grams)
        return plan

    def run(self):
        population   = self._init_population()
        best_plan    = None
        best_fitness = 0

        for gen in range(self.generations):
            fitnesses = [self.fitness(p) for p in population]

            top_fitness = max(fitnesses)
            avg_fitness = round(sum(fitnesses) / len(fitnesses), 6)
            self.fitness_history.append(top_fitness)
            self.avg_fitness_history.append(avg_fitness)

            best_idx = fitnesses.index(top_fitness)
            if top_fitness > best_fitness:
                best_fitness = top_fitness
                best_plan    = copy.deepcopy(population[best_idx])

            if self.callback:
                self.callback(gen + 1, top_fitness, best_plan)

            # keep the top performers as-is (elitism)
            sorted_pop = [x for _, x in sorted(zip(fitnesses, population),
                          key=lambda p: p[0], reverse=True)]
            next_gen = [copy.deepcopy(ind) for ind in sorted_pop[:self.elitism_count]]

            while len(next_gen) < self.pop_size:
                p1 = self._tournament(population, fitnesses)
                p2 = self._tournament(population, fitnesses)
                c1, c2 = self._crossover(p1, p2)
                next_gen.append(self._mutate(c1))
                if len(next_gen) < self.pop_size:
                    next_gen.append(self._mutate(c2))

            population = next_gen

        return best_plan, best_fitness
