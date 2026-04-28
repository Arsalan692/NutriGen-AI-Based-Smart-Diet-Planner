import sys
import os

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

def check_csv():
    path = os.path.join(os.path.dirname(os.path.abspath(__file__)), "halal_foods.csv")
    if not os.path.isfile(path):
        print(f"halal_foods.csv not found at {path}")
        sys.exit(1)


if __name__ == "__main__":
    check_csv()

    from ui import NutriGenApp
    NutriGenApp().mainloop()
