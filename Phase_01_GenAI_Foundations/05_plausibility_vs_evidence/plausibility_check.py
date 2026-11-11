from pathlib import Path

from ollama import chat

MODEL = "qwen2.5:7b"
PROMPT_FILE = Path(__file__).with_name("Prompt_3.txt")
OUTPUT_FILE = Path(__file__).with_name("model_output.txt")

LABELS = [
    "Supported by the input",
    "Reasonable but not established",
    "Unsupported",
]


def main():
    prompt = PROMPT_FILE.read_text(encoding="utf-8").strip()

    response = chat(
        model=MODEL,
        messages=[{"role": "user", "content": prompt}],
        options={"temperature": 0},
    )
    output = response.message.content.strip()

    print("PROMPT")
    print("-" * 60)
    print(prompt)

    print("\nMODEL OUTPUT")
    print("-" * 60)
    print(output)

    OUTPUT_FILE.write_text(output, encoding="utf-8")

    print("\nClassify each generated statement as one of:")
    for label in LABELS:
        print(f"  - {label}")
    print(f"\nOutput saved to {OUTPUT_FILE.name}")


if __name__ == "__main__":
    main()
