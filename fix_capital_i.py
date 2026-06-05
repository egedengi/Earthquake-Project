from MorphologicalAnalysis.FsmMorphologicalAnalyzer import FsmMorphologicalAnalyzer

print("Loading analyzer...")
fsm = FsmMorphologicalAnalyzer()
print("Processing...\n")

input_file = "still_not_found_copy.txt"
output_fixed = "words_i_fixed.txt"
output_still_unanalyzed = "words_still_unanalyzed_after_i.txt"

fixed_count = 0
still_unanalyzed_count = 0

with open(input_file, 'r', encoding='utf-8') as f_in, \
        open(output_fixed, 'w', encoding='utf-8') as f_fixed, \
        open(output_still_unanalyzed, 'w', encoding='utf-8') as f_unanalyzed:
    for line in f_in:
        line = line.strip()
        if not line:
            continue

        parts = line.split()
        word = parts[0]
        count = parts[1] if len(parts) > 1 else ""

        if word[0] == 'i':
            fixed_word = 'İ' + word[1:]
            parse_list = fsm.morphologicalAnalysis(fixed_word)

            if parse_list.size() > 0:
                f_fixed.write(f"{word} {fixed_word} {count}\n")
                fixed_count += 1
            else:
                f_unanalyzed.write(f"{word} {count}\n")
                still_unanalyzed_count += 1
        else:
            f_unanalyzed.write(f"{word} {count}\n")
            still_unanalyzed_count += 1

total = fixed_count + still_unanalyzed_count
print(f"Done!")
print(f"Total: {total}")
print(f"Fixed (i → İ): {fixed_count}")
print(f"Still unanalyzed: {still_unanalyzed_count}")