input_file = "2content_after_capi_deascii.txt"
output_file = "2content_after_capi_deascii_splitter.txt"

with open(input_file, "r", encoding="utf-8") as f_in, \
        open(output_file, "w", encoding="utf-8") as f_out:
    for line in f_in:
        line = line.strip()
        if not line:
            continue

        # Skip entry IDs and "Content:" lines
        if line.startswith("Entry ID:") or line == "Content:":
            continue

        # Split on periods, question marks, exclamation marks
        sentences = []
        current = ""

        i = 0
        while i < len(line):
            char = line[i]
            current += char

            if char in '.!?':
                # Check if next char is space or end of line (real sentence end)
                if i + 1 >= len(line) or line[i + 1] == ' ':
                    sentences.append(current.strip())
                    current = ""

            i += 1

        # Add remaining text if any
        if current.strip():
            sentences.append(current.strip())

        # Write each sentence on its own line
        for sentence in sentences:
            if sentence:
                f_out.write(sentence + "\n")

print("Done!")