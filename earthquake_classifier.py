import google.generativeai as genai
import json
import re
import sys
import time
import os

BATCH_SIZE = 10
MODEL = "gemini-1.5-flash"

SYSTEM_PROMPT = """You are part of an automated earthquake disaster response system.
You will classify Turkish social media entries (from Eksi Sozluk) posted during earthquake disasters.

Classification Classes:
- Class 1: Structural damage/debris + Aid needed + Location or contact info AVAILABLE
- Class 2: No structural damage + Aid needed + Location or contact info AVAILABLE
- Class 3: Structural damage/debris + Aid needed + No location info
- Class 4: No structural damage + Aid needed + No location info
- Class 5: Structural damage present + No aid needed (already rescued, informational)
- Class 6: No damage / Coordination message / General info only

Aid Type Codes:
K=Rescue, G=Food/Water, S=Health, B=Shelter, I=Heating,
Y=Clothing, H=Hygiene, U=Transport, M=Financial Aid, F=Fuel, P=Missing Person

Rules:
- Entries OFFERING help count as no aid needed (Class 5 or 6)
- Coordination messages, Twitter links, short acknowledgement posts -> Class 6
- A phone number OR an address counts as location/contact info AVAILABLE
- Write only the phone number in the contact field, not the address

Respond ONLY with valid JSON, nothing else."""

USER_PROMPT_TEMPLATE = """Classify the following {count} entries.

{entries}

Respond with this exact JSON format:
{{
  "results": [
    {{
      "entry_id": <int>,
      "class": <1-6>,
      "aid_types": "<comma-separated codes, empty string if none>",
      "contact": "<phone number only, empty string if none>"
    }}
  ]
}}"""


def parse_entries_from_file(filepath):
    entries = []
    with open(filepath, "r", encoding="utf-8") as f:
        content = f.read()

    blocks = re.split(r'\n[-_*=<]{3,}.*\n', content)

    for block in blocks:
        block = block.strip()
        if not block:
            continue

        id_match = re.match(r'\[ENTRY (\d+)\]', block)
        if id_match:
            entry_id = int(id_match.group(1))
            text = block[id_match.end():].strip()
        else:
            entry_id = len(entries) + 1
            text = block

        if "► Class:" in text or "► Aid Types:" in text:
            continue

        if text:
            entries.append({"id": entry_id, "text": text})

    return entries


def parse_entries_from_raw_file(filepath):
    entries = []
    entry_id = 1
    current_content = []
    in_content = False

    with open(filepath, "r", encoding="utf-8") as f:
        for line in f:
            line = line.rstrip()
            if line.startswith("Content:"):
                in_content = True
                current_content = []
            elif line.startswith("-" * 10) or line.startswith("=" * 10):
                if in_content and current_content:
                    text = "\n".join(current_content).strip()
                    if text:
                        entries.append({"id": entry_id, "text": text})
                        entry_id += 1
                in_content = False
                current_content = []
            elif in_content:
                current_content.append(line)

    if in_content and current_content:
        text = "\n".join(current_content).strip()
        if text:
            entries.append({"id": entry_id, "text": text})

    return entries


def classify_batch(model, batch):
    formatted = "\n\n".join(
        f"[ENTRY {e['id']}]\n{e['text'][:500]}"
        for e in batch
    )

    prompt = SYSTEM_PROMPT + "\n\n" + USER_PROMPT_TEMPLATE.format(
        count=len(batch),
        entries=formatted
    )

    for attempt in range(3):
        try:
            response = model.generate_content(prompt)
            raw = response.text.strip()
            raw = re.sub(r'^```json\s*|\s*```$', '', raw, flags=re.MULTILINE).strip()
            data = json.loads(raw)
            return data["results"]
        except Exception as e:
            print(f"  Attempt {attempt + 1} failed: {e}")
            if attempt < 2:
                time.sleep(5)

    return []


def format_entry_output(entry, result):
    lines = [
        f"[ENTRY {result['entry_id']}]",
        entry["text"],
        "",
        f"► Class: {result['class']}",
    ]
    if result.get("aid_types"):
        lines.append(f"► Aid Types: {result['aid_types']}")
    if result.get("contact"):
        lines.append(f"► Contact: {result['contact']}")
    return "\n".join(lines)


def write_outputs(all_entries, all_results, output_dir):
    os.makedirs(output_dir, exist_ok=True)

    result_map = {r["entry_id"]: r for r in all_results}
    entry_map = {e["id"]: e for e in all_entries}

    sep = "-" * 80 + "\n"
    priority_count = 0
    other_count = 0

    header = (
        "Class Definitions:\n"
        "  1: Damage + Aid needed + Location AVAILABLE\n"
        "  2: Aid needed + Location AVAILABLE\n"
        "  3: Damage + Aid needed, No location\n"
        "  4: Aid needed, No location\n"
        "  5: Damage, No aid needed\n"
        "  6: Info / Coordination only\n"
        + "=" * 80 + "\n\n"
    )

    with open(os.path.join(output_dir, "class_1_2.txt"), "w", encoding="utf-8") as f1, \
         open(os.path.join(output_dir, "class_3_6.txt"), "w", encoding="utf-8") as f2:

        f1.write(header)
        f2.write(header)

        for entry_id, result in sorted(result_map.items()):
            entry = entry_map.get(entry_id)
            if not entry:
                continue
            formatted = format_entry_output(entry, result) + "\n"
            if result["class"] in (1, 2):
                f1.write(formatted + sep)
                priority_count += 1
            else:
                f2.write(formatted + sep)
                other_count += 1

    summary = {
        "total_classified": len(all_results),
        "priority_entries": priority_count,
        "other_entries": other_count,
        "class_distribution": {},
        "priority_list": []
    }

    for result in all_results:
        c = str(result["class"])
        summary["class_distribution"][c] = summary["class_distribution"].get(c, 0) + 1
        if result["class"] in (1, 2):
            entry = entry_map.get(result["entry_id"], {})
            summary["priority_list"].append({
                "entry_id": result["entry_id"],
                "class": result["class"],
                "aid_types": result.get("aid_types", ""),
                "contact": result.get("contact", ""),
                "preview": entry.get("text", "")[:150]
            })

    with open(os.path.join(output_dir, "summary.json"), "w", encoding="utf-8") as f:
        json.dump(summary, f, ensure_ascii=False, indent=2)

    return priority_count, other_count


def main():
    if len(sys.argv) < 2:
        print("Usage: python earthquake_classifier.py <input_file> [output_dir]")
        sys.exit(1)

    input_file = sys.argv[1]
    output_dir = sys.argv[2] if len(sys.argv) > 2 else "classified_output"

    api_key = os.environ.get("GEMINI_API_KEY")
    if not api_key:
        print("Error: GEMINI_API_KEY environment variable not set.")
        sys.exit(1)

    genai.configure(api_key=api_key)
    model = genai.GenerativeModel(MODEL)

    print(f"Reading entries from: {input_file}")

    entries = parse_entries_from_file(input_file)
    if not entries:
        entries = parse_entries_from_raw_file(input_file)

    print(f"Found {len(entries)} entries")

    if not entries:
        print("No entries to classify.")
        sys.exit(0)

    all_results = []
    total_batches = (len(entries) + BATCH_SIZE - 1) // BATCH_SIZE

    for i in range(0, len(entries), BATCH_SIZE):
        batch = entries[i:i + BATCH_SIZE]
        batch_num = i // BATCH_SIZE + 1
        print(f"Classifying batch {batch_num}/{total_batches}...")

        results = classify_batch(model, batch)
        all_results.extend(results)

        if batch_num < total_batches:
            time.sleep(1)

    print(f"Done. {len(all_results)}/{len(entries)} entries classified.")
    priority, other = write_outputs(entries, all_results, output_dir)

    print(f"Output written to: {output_dir}/")
    print(f"  Priority (Class 1-2): {priority} entries -> class_1_2.txt")
    print(f"  Other    (Class 3-6): {other} entries -> class_3_6.txt")
    print(f"  Summary:               summary.json")


if __name__ == "__main__":
    main()