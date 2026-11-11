import re
from pathlib import Path

from ollama import chat

MODEL = "qwen2.5:7b"
RUNS = 3
LABELS = ["positive", "negative", "neutral"]
TEXT_FILE = Path(__file__).with_name("Text.txt")


def build_prompt(text: str) -> str:
    return f"""
Classify the following text as positive, negative, or neutral.

Text:
"{text}"

Answer in this format:
Label: <positive, negative, or neutral>
Reason: <one sentence>
"""


def classify(text: str) -> tuple[str, str]:
    response = chat(
        model=MODEL,
        messages=[{"role": "user", "content": build_prompt(text)}],
    )
    output = response.message.content.strip()

    label_match = re.search(r"label\W*\s*([a-z-]+)", output, re.IGNORECASE)
    reason_match = re.search(r"reason\W*\s*(.+)", output, re.IGNORECASE)

    label = label_match.group(1).lower() if label_match else "unparsed"
    reason = reason_match.group(1).strip() if reason_match else output

    return label, reason


def main():
    lines = TEXT_FILE.read_text(encoding="utf-8").splitlines()
    texts = [line.strip() for line in lines if line.strip()]

    for text in texts:
        print("\n" + "=" * 70)
        print("Text:", text)
        print("=" * 70)

        labels = []

        for run_number in range(1, RUNS + 1):
            label, reason = classify(text)
            labels.append(label)

            note = "" if label in LABELS else "   <-- not an allowed label"
            print(f"Run {run_number}: {label}{note}")
            print(f"       {reason}")

        same = "yes" if len(set(labels)) == 1 else "no"
        print("Same label in every run:", same)


if __name__ == "__main__":
    main()
