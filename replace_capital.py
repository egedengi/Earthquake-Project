print("Reading words that need capitalization...\n")

analyzed_capitalized_file = "words_deasciified_part2.txt"
input_text_file = "content_after_capi_new.txt"
output_text_file = "2content_after_capi_deascii.txt"

words_to_capitalize = {}

with open(analyzed_capitalized_file, 'r', encoding='utf-8') as f:
    for line in f:
        line = line.strip()
        if not line:
            continue

        parts = line.split()
        if len(parts) >= 2:
            lowercase_word = parts[0]
            capitalized_word = parts[1]
            words_to_capitalize[lowercase_word] = capitalized_word
            print(f"Will replace: '{lowercase_word}' → '{capitalized_word}'")

print(f"\nTotal words to capitalize: {len(words_to_capitalize)}")
print("\nProcessing your text file...\n")

replaced_count = 0
replacement_details = {}

with open(input_text_file, 'r', encoding='utf-8') as f_in, \
        open(output_text_file, 'w', encoding='utf-8') as f_out:
    for line_num, line in enumerate(f_in, 1):
        original_line = line
        words_in_line = line.split()
        new_words = []

        for word in words_in_line:
            if word in words_to_capitalize:
                replacement = words_to_capitalize[word]
                new_words.append(replacement)
                replaced_count += 1

                if word not in replacement_details:
                    replacement_details[word] = 0
                replacement_details[word] += 1

                print(f"Line {line_num}: '{word}' → '{replacement}'")
            else:
                new_words.append(word)

        f_out.write(' '.join(new_words) + '\n')

print(f"\n{'=' * 50}")
print(f"Done!")
print(f"Total replacements made: {replaced_count}")
print(f"\nBreakdown by word:")
for word, count in replacement_details.items():
    print(f"  {word} → {words_to_capitalize[word]}: {count} times")
print(f"\nOutput saved to: {output_text_file}")
print(f"{'=' * 50}")