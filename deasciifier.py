from MorphologicalAnalysis.FsmMorphologicalAnalyzer import FsmMorphologicalAnalyzer
import itertools

print("Loading analyzer...")
fsm = FsmMorphologicalAnalyzer()
print("Processing...\n")

input_file = "un_af_deasc_mah_notspace.txt"
output_deasciified = "deasc_part2_analyzed.txt"
output_still_unanalyzed = "deasc_part2_unanalyzed.txt"

MAX_WORD_LENGTH = 12

deasciified_count = 0
still_unanalyzed_count = 0
skipped_too_long = 0

turkish_char_map = {
    'c': ['c', 'ç'],
    'C': ['C', 'Ç'],
    'g': ['g', 'ğ'],
    'G': ['G', 'Ğ'],
    'i': ['i', 'ı', 'İ'],
    'I': ['I', 'ı', 'İ'],
    'o': ['o', 'ö'],
    'O': ['O', 'Ö'],
    's': ['s', 'ş'],
    'S': ['S', 'Ş'],
    'u': ['u', 'ü'],
    'U': ['U', 'Ü'],
}


def generate_turkish_variants(word):
    positions = []
    chars = []

    for i, char in enumerate(word):
        if char in turkish_char_map:
            positions.append(i)
            chars.append(turkish_char_map[char])
        else:
            positions.append(i)
            chars.append([char])

    all_combinations = itertools.product(*chars)

    variants = []
    for combination in all_combinations:
        variant = ''.join(combination)
        if variant != word:
            variants.append(variant)

    return variants


with open(input_file, 'r', encoding='utf-8') as f_in, \
        open(output_deasciified, 'w', encoding='utf-8') as f_deasciified, \
        open(output_still_unanalyzed, 'w', encoding='utf-8') as f_unanalyzed:
    for line_num, line in enumerate(f_in, 1):
        line = line.strip()
        if not line:
            continue

        parts = line.split()
        word = parts[0]
        count = parts[1] if len(parts) > 1 else ""

        if len(word) > MAX_WORD_LENGTH:
            f_unanalyzed.write(f"{word} {count}\n")
            still_unanalyzed_count += 1
            skipped_too_long += 1
            continue

        variants = generate_turkish_variants(word)

        if len(variants) == 0:
            f_unanalyzed.write(f"{word} {count}\n")
            still_unanalyzed_count += 1
            continue

        valid_variants = []

        for variant in variants:
            parse_list = fsm.morphologicalAnalysis(variant)
            if parse_list.size() > 0:
                valid_variants.append(variant)

        if len(valid_variants) == 1:
            f_deasciified.write(f"{word} {valid_variants[0]} {count}\n")
            deasciified_count += 1
        else:
            f_unanalyzed.write(f"{word} {count}\n")
            still_unanalyzed_count += 1

        if line_num % 100 == 0:
            print(f"Processed {line_num} words...")

total = deasciified_count + still_unanalyzed_count
print(f"\nDone!")
print(f"Total: {total}")
print(f"Deasciified: {deasciified_count}")
print(f"Still unanalyzed: {still_unanalyzed_count}")
print(f"Skipped (too long, >{MAX_WORD_LENGTH} chars): {skipped_too_long}")