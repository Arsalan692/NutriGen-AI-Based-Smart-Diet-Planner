import csv
import random
import shutil

input_file = "halal_foods.csv"
temp_file = "halal_foods_temp.csv"

def get_price(name, category):
    name = name.lower()
    if category == 'Protein':
        if 'beef' in name or 'mutton' in name or 'lamb' in name or 'goat' in name:
            return random.randint(250, 400)
        elif 'chicken' in name:
            return random.randint(100, 180)
        elif 'fish' in name or 'salmon' in name or 'tuna' in name or 'prawn' in name or 'shrimp' in name or 'crab' in name:
            return random.randint(200, 450)
        elif 'egg' in name:
            return random.randint(30, 60)
        else:
            return random.randint(150, 250)
    elif category == 'Dairy':
        if 'milk' in name or 'yogurt' in name or 'lassi' in name or 'laban' in name:
            return random.randint(20, 40)
        elif 'cheese' in name or 'paneer' in name or 'butter' in name:
            return random.randint(150, 250)
        else:
            return random.randint(50, 100)
    elif category == 'Grains':
        if 'rice' in name:
            return random.randint(30, 60)
        elif 'bread' in name or 'roti' in name or 'naan' in name or 'paratha' in name:
            return random.randint(20, 50)
        else:
            return random.randint(30, 80)
    elif category == 'Legumes':
        return random.randint(40, 80)
    elif category == 'Vegetables':
        return random.randint(15, 40)
    elif category == 'Fruits':
        if 'dates' in name or 'almonds' in name or 'walnut' in name:
            return random.randint(100, 250)
        return random.randint(30, 80)
    elif category == 'Nuts & Seeds':
        return random.randint(200, 500)
    elif category == 'Fats & Oils':
        if 'olive' in name:
            return random.randint(200, 400)
        return random.randint(80, 150)
    elif category == 'Other':
        return random.randint(100, 200)
    elif category == 'Beverages':
        return random.randint(20, 60)
    return random.randint(50, 100)

with open(input_file, 'r', newline='', encoding='utf-8') as f:
    reader = csv.reader(f)
    header = next(reader)
    if 'price_per_100g' not in header:
        header.append('price_per_100g')
    
    rows = []
    for row in reader:
        if len(row) == 7:
            price = get_price(row[0], row[1])
            row.append(str(price))
        rows.append(row)

with open(temp_file, 'w', newline='', encoding='utf-8') as f:
    writer = csv.writer(f)
    writer.writerow(header)
    writer.writerows(rows)

shutil.move(temp_file, input_file)
print("Prices added successfully.")
