print("Loading English word list...")

# Load English words
english_set = set()
with open("words_alpha.txt", "r", encoding="utf-8") as f:
    for line in f:
        word = line.strip().lower()
        if word:
            english_set.add(word)

print(f"Loaded {len(english_set)} English words")

print("\nChecking words...")

input_file = "un_af_deasc_mah_notspace.txt"
output_english = "english_words.txt"
output_not_english = "not_english.txt"

english_count = 0
not_english_count = 0

with open(input_file, "r", encoding="utf-8") as f_in, \
        open(output_english, "w", encoding="utf-8") as f_english, \
        open(output_not_english, "w", encoding="utf-8") as f_not:
    for line in f_in:
        line = line.strip()
        if not line:
            continue

        parts = line.split()
        word = parts[0]
        count = parts[1] if len(parts) > 1 else ""

        # Check if word is English (case-insensitive)
        if word.lower() in english_set:
            f_english.write(f"{word} {count}\n")
            english_count += 1
        else:
            f_not.write(f"{word} {count}\n")
            not_english_count += 1

total = english_count + not_english_count

print(f"\nDone!")
print(f"Total words: {total}")
print(f"Words that are English: {english_count}")
print(f"Words that are NOT English: {not_english_count}")
print(f"\nFiles created:")
print(f"  - {output_english}")
print(f"  - {output_not_english}")