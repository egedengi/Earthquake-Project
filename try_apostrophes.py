from MorphologicalAnalysis.FsmMorphologicalAnalyzer import FsmMorphologicalAnalyzer

print("Loading analyzer...")
fsm = FsmMorphologicalAnalyzer()
print("Processing...\n")

input_file = "unanalyzed_words.txt"
output_found = "apostrophe_found.txt"
output_not_found = "apostrophe_not_found.txt"

found_count = 0
not_found_count = 0

with open(input_file, 'r', encoding='utf-8') as f_in, \
        open(output_found, 'w', encoding='utf-8') as f_found, \
        open(output_not_found, 'w', encoding='utf-8') as f_not_found:
    for line in f_in:
        line = line.strip()
        if not line:
            continue

        parts = line.split()
        word = parts[0]
        count = parts[1] if len(parts) > 1 else ""

        word_len = len(word)

        if word_len < 6:
            f_not_found.write(f"{word} {count}\n")
            not_found_count += 1
            continue

        valid_results = []

        for i in range(1, 5):
            if i >= word_len:
                continue

            left_part = word[:-i]
            right_part = word[-i:]

            if len(left_part) < 2:
                continue

            left_cap = left_part[0].upper() + left_part[1:]

            left_parse = fsm.morphologicalAnalysis(left_cap)

            if left_parse.size() == 0:
                continue

            has_prop = False
            for j in range(left_parse.size()):
                analysis = left_parse.getFsmParse(j).transitionList()
                if '+PROP' in analysis:
                    has_prop = True
                    break

            if not has_prop:
                continue

            word_with_apos = left_cap + "'" + right_part
            full_parse = fsm.morphologicalAnalysis(word_with_apos)

            if full_parse.size() > 0:
                valid_results.append((len(right_part), word_with_apos))

        if valid_results:
            valid_results.sort(key=lambda x: x[0], reverse=True)
            best_result = valid_results[0][1]

            f_found.write(f"{word} {best_result} {count}\n")
            found_count += 1
        else:
            f_not_found.write(f"{word} {count}\n")
            not_found_count += 1

total = found_count + not_found_count
print(f"Done!")
print(f"Total: {total}")
print(f"Found with apostrophe: {found_count}")
print(f"Not found: {not_found_count}")