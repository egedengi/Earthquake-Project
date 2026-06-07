print("Loading mahalle list...")

# Load mahalle names
mahalle_set = set()
with open("mahalle_listesi.txt", "r", encoding="utf-8") as f:
    for line in f:
        mahalle = line.strip().lower()
        if mahalle:
            mahalle_set.add(mahalle)

print(f"Loaded {len(mahalle_set)} mahalle names")

print("\nChecking words...")

input_file = "words_still_unanalyzed_after_deasciified_part2.txt"
output_mahalles = "analyzed_after_mah.txt"
output_not_mahalles = "un_af_deasc_mah_notspace.txt"

mahalle_count = 0
not_mahalle_count = 0

with open(input_file, "r", encoding="utf-8") as f_in, \
        open(output_mahalles, "w", encoding="utf-8") as f_mahalles, \
        open(output_not_mahalles, "w", encoding="utf-8") as f_not:
    for line in f_in:
        line = line.strip()
        if not line:
            continue

        parts = line.split()
        word = parts[0]
        count = parts[1] if len(parts) > 1 else ""

        if word.lower() in mahalle_set:
            f_mahalles.write(f"{word} {count}\n")
            mahalle_count += 1
        else:
            f_not.write(f"{word} {count}\n")
            not_mahalle_count += 1

total = mahalle_count + not_mahalle_count

print(f"\nDone!")
print(f"Total words: {total}")
print(f"Words that are mahalles: {mahalle_count}")
print(f"Words that are NOT mahalles: {not_mahalle_count}")
print(f"\nFiles created:")
print(f"  - {output_mahalles}")
print(f"  - {output_not_mahalles}")