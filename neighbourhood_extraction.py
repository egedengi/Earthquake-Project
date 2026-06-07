import json

print("Reading neighbourhoods.json...")

with open("neighbourhoods.json", "r", encoding="utf-8") as f:
    data = json.load(f)

mahalles = set()

for entry in data:
    # Format: [city_code, city_name, district, mahalle, postal_code]
    mahalle = entry[3]  # 4th element is the mahalle name

    # Remove " Mah" suffix if present
    if mahalle.endswith(" Mah"):
        mahalle = mahalle[:-4]

    # Add lowercase version to set
    mahalles.add(mahalle.lower())

# Write to file
with open("mahalle_listesi.txt", "w", encoding="utf-8") as f:
    for mahalle in sorted(mahalles):
        f.write(mahalle + "\n")

print(f"Done! Extracted {len(mahalles)} unique mahalles")
print(f"Saved to: mahalle_listesi.txt")