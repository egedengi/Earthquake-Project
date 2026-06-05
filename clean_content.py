input_file = "content_copy.txt"
output_file = "content_copy_clean.txt"

print("Cleaning entries file...")

with open(input_file, 'r', encoding='utf-8') as f_in, \
        open(output_file, 'w', encoding='utf-8') as f_out:
    for line in f_in:
        if line.startswith("Author:") or line.startswith("Date:"):
            continue
        else:
            f_out.write(line)

print(f"Cleaned file saved to: {output_file}")