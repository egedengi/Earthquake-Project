import pdfplumber
import re

print("Reading PDF...")

mahalle_names = set()

with pdfplumber.open("mahalle-listesi.pdf") as pdf:
    print(f"Total pages: {len(pdf.pages)}")

    for page_num, page in enumerate(pdf.pages, 1):
        if page_num % 50 == 0:
            print(f"Processing page {page_num}...")

        text = page.extract_text()

        if not text:
            continue

        lines = text.split('\n')

        for line in lines:

            match = re.match(r'^\d+\s+([A-ZÇĞİÖŞÜ\s]+?)\s+[A-ZÇĞİÖŞÜ]+\s+->', line)
            if match:
                mahalle = match.group(1).strip()
                mahalle_lower = mahalle.replace('I', 'ı').replace('İ', 'i').lower()
                mahalle_names.add(mahalle_lower)

print(f"\nExtracted {len(mahalle_names)} unique mahalle names")

# Write to file
with open("mahalle_listesi.txt", "w", encoding="utf-8") as f:
    for mahalle in sorted(mahalle_names):
        f.write(mahalle + "\n")

print("Saved to: mahalle_listesi.txt")


print(f"\nDone! Total unique mahalles: {len(mahalle_names)}")