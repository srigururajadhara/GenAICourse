
import json
import glob
import hashlib
from collections import Counter, defaultdict

files = glob.glob("data/raw/html/*.json")

records = []

for path in files:
    with open(path, encoding="utf-8") as f:
        record = json.load(f)

    record["_path"] = path
    records.append(record)


def normalized_hash(text):
    normalized = " ".join(text.lower().split())
    return hashlib.sha256(
        normalized.encode("utf-8")
    ).hexdigest()


complete_details = []
empty_details = []
scheme_lists = []
department_profiles = []
beneficiary_pages = []
other_pages = []

for r in records:

    url = r.get("url", "")
    text = r.get("text", "")
    lower_url = url.lower()

    if "scheme_details.php" in lower_url:

        if (
            "Training to Farmers" in text
            or (
                len(text) > 450
                and "Scheme Title/Name:" in text
                and "Beneficiaries:" in text
            )
        ):
            complete_details.append(r)
        else:
            empty_details.append(r)

    elif "scheme_list.php" in lower_url or "scheme_wise.php" in lower_url:
        scheme_lists.append(r)

    elif "dept_profile.php" in lower_url:
        department_profiles.append(r)

    elif "scheme_beneficiary_list.php" in lower_url:
        beneficiary_pages.append(r)

    else:
        other_pages.append(r)


# Find duplicate content.
hash_groups = defaultdict(list)

for r in records:
    hash_groups[normalized_hash(r.get("text", ""))].append(r)

duplicate_groups = {
    key: value
    for key, value in hash_groups.items()
    if len(value) > 1
}

print("\n========== DATASET AUDIT ==========")

print("Total records:", len(records))
print("Complete scheme detail candidates:", len(complete_details))
print("Empty scheme detail records:", len(empty_details))
print("Scheme listing pages:", len(scheme_lists))
print("Department profiles:", len(department_profiles))
print("Beneficiary listing pages:", len(beneficiary_pages))
print("Other pages:", len(other_pages))

print("\nDuplicate content groups:", len(duplicate_groups))

print("\n========== EMPTY SCHEME DETAILS ==========")

for r in empty_details[:15]:
    print(r.get("url"), "|", len(r.get("text", "")), "chars")

print("\n========== DUPLICATE CONTENT ==========")

for group in list(duplicate_groups.values())[:10]:
    print("\nCopies:", len(group))
    for r in group[:5]:
        print("-", r.get("url"))

print("\n========== COMPLETE SCHEME CANDIDATES ==========")

for r in complete_details[:15]:
    print(
        r.get("title"),
        "|",
        len(r.get("text", "")),
        "chars"
    )

print("\n========== AUDIT COMPLETED ==========")
