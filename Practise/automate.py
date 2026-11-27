import os
from pathlib import Path
from dotenv import load_dotenv
from openai import OpenAI

load_dotenv()
client = OpenAI()

INPUT_DIR = Path("input_notes")
OUTPUT_DIR = Path("output_summaries")
OUTPUT_DIR.mkdir(exist_ok=True)  # Creates the output folder if it doesn't exist

def summarize_text(text: str) -> str:
    response = client.chat.completions.create(
        model="gpt-4o-mini",
        messages=[
            {"role": "system", "content": "Extract action items as concise bullet points."},
            {"role": "user", "content": text}
        ]
    )
    return response.choices[0].message.content

# Loop through every .txt file in input_notes
for file_path in INPUT_DIR.glob("*.txt"):
    print(f"Processing {file_path.name}...")
    raw_text = file_path.read_text(encoding="utf-8")

    summary = summarize_text(raw_text)

    # Save the result to output_summaries
    output_file = OUTPUT_DIR / f"summary_{file_path.name}"
    output_file.write_text(summary, encoding="utf-8")
    print(f"Saved -> {output_file}")

print("All files processed!")