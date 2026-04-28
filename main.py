import sys
import os

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))


def check_deps():
    missing = [p for p in ("matplotlib", "numpy") if not __import__("importlib").util.find_spec(p)]
    if missing:
        print(f"Missing: {', '.join(missing)}")
        print(f"Run: pip install {' '.join(missing)}")
        sys.exit(1)


def check_csv():
    path = os.path.join(os.path.dirname(os.path.abspath(__file__)), "halal_foods.csv")
    if not os.path.isfile(path):
        print(f"halal_foods.csv not found at {path}")
        sys.exit(1)


if __name__ == "__main__":
    check_deps()
    check_csv()

    from ui import NutriGenApp
    NutriGenApp().mainloop()
