import requests
import json
import re
import sys
import time
import os

BATCH_SIZE = 50
MODEL = "gemini-2.5-flash-lite"
API_URL = "https://generativelanguage.googleapis.com/v1beta/models/{model}:generateContent?key={key}"

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

    parts = re.split(r'\nEntry ID:', content)

    entry_id = 1
    for part in parts[1:]:
        lines = part.strip().split('\n')
        content_lines = []
        in_content = False

        for line in lines:
            if line.startswith("Author:") or line.startswith("Date:"):
                continue
            elif line.startswith("Content:"):
                in_content = True
            elif line.startswith("-" * 10):
                break
            elif in_content:
                content_lines.append(line)

        text = "\n".join(content_lines).strip()
        if text:
            entries.append({"id": entry_id, "text": text})
            entry_id += 1

    return entries


def classify_batch(api_key, batch):
    formatted = "\n\n".join(
        f"[ENTRY {e['id']}]\n{e['text'][:500]}"
        for e in batch
    )

    prompt = SYSTEM_PROMPT + "\n\n" + USER_PROMPT_TEMPLATE.format(
        count=len(batch),
        entries=formatted
    )

    url = API_URL.format(model=MODEL, key=api_key)
    payload = {
        "contents": [{"parts": [{"text": prompt}]}]
    }

    for attempt in range(3):
        try:
            response = requests.post(url, json=payload, timeout=60)
            response.raise_for_status()
            data = response.json()
            raw = data["candidates"][0]["content"]["parts"][0]["text"].strip()
            raw = re.sub(r'^```json\s*|\s*```$', '', raw, flags=re.MULTILINE).strip()
            result = json.loads(raw)
            return result["results"]
        except Exception as e:
            print(f"  Attempt {attempt + 1} failed: {e}")
            if attempt < 2:
                time.sleep(30)

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
        print("Error: GEMINI_API_KEY not set.")
        sys.exit(1)

    print(f"Reading entries from: {input_file}")
    entries = parse_entries_from_file(input_file)
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

        results = classify_batch(api_key, batch)
        all_results.extend(results)

        if batch_num < total_batches:
            time.sleep(20)

    print(f"Done. {len(all_results)}/{len(entries)} entries classified.")
    priority, other = write_outputs(entries, all_results, output_dir)

    print(f"Output: {output_dir}/")
    print(f"  Priority (Class 1-2): {priority} -> class_1_2.txt")
    print(f"  Other    (Class 3-6): {other} -> class_3_6.txt")
    print(f"  Summary:               summary.json")


if __name__ == "__main__":
    main()