from MorphologicalAnalysis.FsmMorphologicalAnalyzer import FsmMorphologicalAnalyzer

print("Loading analyzer...")
fsm = FsmMorphologicalAnalyzer()
print("Processing...\n")

input_file = "unanalyzed_words.txt"
analyzed_capitalized_file = "analyzed_capitalized.txt"
still_unanalyzed_file = "still_unanalyzed.txt"

analyzed_count = 0
still_unanalyzed_count = 0

with open(input_file, 'r', encoding='utf-8') as f_in, \
        open(analyzed_capitalized_file, 'w', encoding='utf-8') as f_analyzed, \
        open(still_unanalyzed_file, 'w', encoding='utf-8') as f_still_unanalyzed:
    for line in f_in:
        line = line.strip()
        if not line:
            continue

        parts = line.split()
        word = parts[0]
        count = parts[1] if len(parts) > 1 else ""

        capitalized_word = word[0].upper() + word[1:] if len(word) > 0 else word
        parse_list = fsm.morphologicalAnalysis(capitalized_word)

        if parse_list.size() > 0:
            f_analyzed.write(f"{word} {capitalized_word} {count}\n")
            analyzed_count += 1
        else:
            f_still_unanalyzed.write(f"{word} {count}\n")
            still_unanalyzed_count += 1

total = analyzed_count + still_unanalyzed_count
print(f"Done!")
print(f"Total: {total}")
print(f"Analyzed (capitalized): {analyzed_count}")
print(f"Still unanalyzed: {still_unanalyzed_count}")