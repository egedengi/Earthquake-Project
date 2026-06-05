input_file = "found_with_apostrophe.txt"
output_file = "found_with_apostrophe_cleannnnnnnnnnnn.txt"

valid_suffixes = {
    'a', 'e', 'ı', 'i', 'u', 'ü',
    'da', 'de', 'ta', 'te',
    'dan', 'den', 'tan', 'ten',
    'ın', 'in', 'un', 'ün',
    'nın', 'nin', 'nun', 'nün',
    'na', 'ne',
    'nda', 'nde',
    'ndan', 'nden',
    'ya', 'ye',
    'yla', 'yle', 'la', 'le',
    'yı', 'yi', 'yu', 'yü',
    'ı', 'i', 'u', 'ü',
    'sı', 'si', 'su', 'sü',
    'ım', 'im', 'um', 'üm',
    'ımız', 'imiz', 'umuz', 'ümüz',
    'mız', 'miz', 'muz', 'müz',
    'ımı', 'imi', 'umu', 'ümü',
    'tir', 'tır', 'dir', 'dır',
    'miş', 'mış', 'muş', 'müş',
    'teki', 'taki', 'deki', 'daki',
    'ler', 'lar',
}

removed = 0
kept = 0

with open(input_file, 'r', encoding='utf-8') as f_in, \
        open(output_file, 'w', encoding='utf-8') as f_out:
    for line in f_in:
        line = line.strip()
        if not line:
            continue

        parts = line.split()
        if len(parts) < 2:
            continue

        original = parts[0]
        corrected = parts[1]
        count = parts[2] if len(parts) > 2 else ""

        if "'" not in corrected:
            f_out.write(line + "\n")
            kept += 1
            continue

        after_apostrophe = corrected.split("'")[1].lower()

        if after_apostrophe in valid_suffixes:
            f_out.write(f"{original} {corrected} {count}\n")
            kept += 1
        else:
            removed += 1
            print(f"Removed: {corrected} (suffix: '{after_apostrophe}')")

print(f"\nDone!")
print(f"Removed: {removed}")
print(f"Kept: {kept}")