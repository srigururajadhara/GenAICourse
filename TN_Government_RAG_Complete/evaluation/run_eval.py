import json
from pathlib import Path

DATASET = Path(__file__).with_name("test_dataset.json")


def main():
    cases = json.loads(DATASET.read_text(encoding="utf-8"))
    print(f"Loaded {len(cases)} bilingual evaluation cases.")
    print("This is a test-set inventory, not an automated accuracy score.")
    for index, case in enumerate(cases, 1):
        print(f"{index}. [{case['language']}] {case['question']}")
        print(f"   Expected: {case['expected_behavior']}")


if __name__ == "__main__":
    main()
