from MorphologicalAnalysis.FsmMorphologicalAnalyzer import FsmMorphologicalAnalyzer

print("Loading analyzer...")
fsm = FsmMorphologicalAnalyzer()
print("Processing...\n")

input_file = "un_af_deasc_mah_notspace.txt"
output_single_space = "space.txt"
output_unspaced = "nospace.txt"

single_count = 0
unspaced_count = 0


def is_valid_root(parse_list):
    if parse_list.size() == 0:
        return False

    for i in range(parse_list.size()):
        analysis = parse_list.getFsmParse(i).transitionList()
        root = analysis.split('+')[0]
        if len(root) >= 3:
            return True

    return False


with open(input_file, 'r', encoding='utf-8') as f_in, \
        open(output_single_space, 'w', encoding='utf-8') as f_single, \
        open(output_unspaced, 'w', encoding='utf-8') as f_unspaced:
    for line in f_in:
        line = line.strip()
        if not line:
            continue

        parts = line.split()
        word = parts[0]
        count = parts[1] if len(parts) > 1 else ""

        word_len = len(word)

        if word_len < 6:
            f_unspaced.write(f"{word} {count}\n")
            unspaced_count += 1
            continue

        valid_positions = []

        start = 3
        end = word_len - 3

        for pos in range(start, end + 1):
            left_part = word[:pos]
            right_part = word[pos:]

            left_cap = left_part[0].upper() + left_part[1:] if len(left_part) > 0 else left_part
            right_cap = right_part[0].upper() + right_part[1:] if len(right_part) > 0 else right_part

            if len(left_part) < 4 or len(right_part) < 4:
                continue

            left_parse = fsm.morphologicalAnalysis(left_cap)
            right_parse = fsm.morphologicalAnalysis(right_cap)

            if not (is_valid_root(left_parse) and is_valid_root(right_parse)):
                continue

            # Additional filter: check if at least one part has PROP tag or both have simple analyses
            left_has_prop = False
            right_has_prop = False

            for i in range(left_parse.size()):
                if '+PROP' in left_parse.getFsmParse(i).transitionList():
                    left_has_prop = True
                    break

            for i in range(right_parse.size()):
                if '+PROP' in right_parse.getFsmParse(i).transitionList():
                    right_has_prop = True
                    break

            if not (left_has_prop or right_has_prop):
                continue

            if is_valid_root(left_parse) and is_valid_root(right_parse):
                valid_positions.append((pos, left_cap, right_cap))

        if len(valid_positions) == 1:
            pos, left_cap, right_cap = valid_positions[0]
            spaced_word = left_cap + " " + right_cap
            f_single.write(f"{word} {spaced_word} {count}\n")
            single_count += 1
        else:
            f_unspaced.write(f"{word} {count}\n")
            unspaced_count += 1

total = single_count + unspaced_count
print(f"Done!")
print(f"Total: {total}")
print(f"Single valid space: {single_count}")
print(f"Unspaced: {unspaced_count}")