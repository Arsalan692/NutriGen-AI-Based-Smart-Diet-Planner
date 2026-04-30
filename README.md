# 🥗 NutriGen: AI-Based Smart Diet Planner

![NutriGen Banner](https://img.shields.io/badge/NutriGen-AI%20Diet%20Planner-10b981?style=for-the-badge)
![Python](https://img.shields.io/badge/Python-3.8+-blue.svg?style=for-the-badge&logo=python)
![License](https://img.shields.io/badge/License-MIT-green.svg?style=for-the-badge)

NutriGen is an intelligent, AI-powered desktop application designed to generate personalized, macro-optimized halal meal plans. By leveraging an evolutionary **Genetic Algorithm**, NutriGen mathematically optimizes daily food intake to perfectly match your specific caloric and macronutrient goals based on your physical profile.

---

## ✨ Features

*   🧬 **Genetic Algorithm Optimization:** Uses evolutionary computing to find the optimal combination of foods that meet your specific calorie, protein, carb, and fat targets.
*   📊 **Visual Analytics:** Interactive, dark-themed matplotlib charts providing deep insights into meal breakdowns, macro splits, and fitness evolution across algorithm generations.
*   🍽️ **Extensive Halal Database:** Built-in database of 180+ carefully categorized halal food items with precise nutritional values.
*   🎯 **Highly Personalized:** Calculates Basal Metabolic Rate (BMR) and Total Daily Energy Expenditure (TDEE) based on age, weight, height, gender, activity level, and fitness goals (Weight Loss, Maintenance, Muscle Gain).
*   🚫 **Custom Dietary Restrictions:** Easily exclude specific ingredients or foods you dislike or are allergic to.
*   💻 **Premium Modern UI:** A stunning, ultra-smooth dark mode interface built with CustomTkinter, featuring 3D card hover effects, smooth transitions, and intuitive navigation.

---

## 🛠️ Technology Stack

*   **Core Logic:** Pure Python
*   **AI / Algorithm:** Custom Genetic Algorithm (Selection, Crossover, Mutation, Elitism)
*   **GUI Framework:** `customtkinter` (Modern, dark-themed wrapper for Tkinter)
*   **Data Visualization:** `matplotlib`, `numpy`
*   **Data Handling:** Native `csv` module

---

## 🧠 How the AI Works (Genetic Algorithm)

NutriGen doesn't just guess your meals. It "evolves" them:
1.  **Initialization:** Generates a random initial population of 30-150 daily meal plans.
2.  **Fitness Evaluation:** Each plan is scored based on how closely it hits your target macros, penalizing for calorie deviations, missing macros, or unbalanced meal distributions.
3.  **Selection (Tournament):** The best plans are selected to be "parents".
4.  **Crossover:** Parent plans swap meals to create new, potentially better "child" plans.
5.  **Mutation:** Individual food items or portion sizes (grams) are randomly altered to maintain genetic diversity and find better combinations.
6.  **Elitism:** The absolute best plans are automatically carried over to the next generation to ensure quality never degrades.
*After 40-200 generations, the algorithm converges on a highly optimized daily diet plan.*

---

## 🚀 Installation & Setup

1. **Clone the repository:**
   ```bash
   git clone https://github.com/Arsalan692/NutriGen-AI-Based-Smart-Diet-Planner.git
   cd NutriGen-AI-Based-Smart-Diet-Planner
   ```

2. **Create a virtual environment (Optional but recommended):**
   ```bash
   python -m venv venv
   # On Windows:
   venv\Scripts\activate
   # On Mac/Linux:
   source venv/bin/activate
   ```

3. **Install required dependencies:**
   ```bash
   pip install -r requirements.txt
   ```

4. **Run the application:**
   ```bash
   python main.py
   ```

---

## 💻 Usage

1.  **Enter Profile:** Input your age, weight, height, gender, goal, and activity level on the "Plan" tab.
2.  **Set Restrictions:** Add any foods you want the AI to avoid (e.g., "Garlic, Bitter Gourd").
3.  **Tweak AI:** Adjust Generation and Population size (higher numbers take longer but yield more accurate results).
4.  **Generate:** Click "Generate My Plan" and watch the AI optimize your diet in real-time.
5.  **Review & Visualize:** Go to the "Results" tab to see your meal-by-meal breakdown, then click "View Visualisation" to explore the data charts.

---

## 📸 Screenshots

*(Add screenshots of your amazing new CustomTkinter UI here!)*
*   *Welcome Screen*
*   *Diet Plan Form*
*   *Results Dashboard*
*   *Matplotlib Visualizations*

---

## 🤝 Contributing
Contributions, issues, and feature requests are welcome! Feel free to check the [issues page](https://github.com/Arsalan692/NutriGen-AI-Based-Smart-Diet-Planner/issues).

## 📝 License
This project is open-source and available under the [MIT License](LICENSE).
