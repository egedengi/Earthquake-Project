from MorphologicalAnalysis.FsmMorphologicalAnalyzer import FsmMorphologicalAnalyzer

print("Loading analyzer...")
fsm = FsmMorphologicalAnalyzer()
print("Ready!\n")

input_file = "content_cap_apo.txt"
analyzed_file = "analyzed_cap_apo.txt"
unanalyzed_file = "unanalyzed_cap_apo.txt"

analyzed_count = 0
unanalyzed_count = 0

with open(input_file, 'r', encoding='utf-8') as f_in, \
        open(analyzed_file, 'w', encoding='utf-8') as f_analyzed, \
        open(unanalyzed_file, 'w', encoding='utf-8') as f_unanalyzed:
    for line in f_in:
        line = line.strip()
        if not line:
            continue

        parts = line.split()
        word = parts[0]
        count = parts[1] if len(parts) > 1 else ""

        parse_list = fsm.morphologicalAnalysis(word)

        if parse_list.size() > 0:

            f_analyzed.write(f"{word} {count}\n")
            analyzed_count += 1
        else:
            f_unanalyzed.write(f"{word} {count}\n")
            unanalyzed_count += 1

total = analyzed_count + unanalyzed_count
print(f"\nDone!")
print(f"Total words: {total}")
print(f"Analyzed: {analyzed_count} ({analyzed_count / total * 100:.1f}%)")
print(f"Unanalyzed: {unanalyzed_count} ({unanalyzed_count / total * 100:.1f}%)")
print(f"\nFiles created:")
print(f"  - {analyzed_file}")
print(f"  - {unanalyzed_file}")