import re
import time
from pathlib import Path

from ollama import chat

MODEL = "qwen2.5:7b"
RUNS = 3
PROMPT_FILE = Path(__file__).with_name("Prompt.txt")


def load_prompts(path: Path) -> dict[str, str]:
    text = path.read_text(encoding="utf-8")
    parts = re.split(r"^(Prompt \d+):?\s*$", text, flags=re.MULTILINE)

    return {
        parts[i]: parts[i + 1].strip()
        for i in range(1, len(parts), 2)
    }


def run(prompt: str) -> tuple[str, float]:
    start = time.perf_counter()

    response = chat(
        model=MODEL,
        messages=[{"role": "user", "content": prompt}],
    )

    return response.message.content.strip(), time.perf_counter() - start


def main():
    prompts = load_prompts(PROMPT_FILE)

    structured = prompts["Prompt 02"]
    claim = "Claim:\n" + structured.split("Claim:", 1)[1].strip()
    vague = f"{prompts['Prompt 01']}\n\n{claim}"

    for name, prompt in [
        ("VAGUE PROMPT", vague),
        ("STRUCTURED PROMPT", structured),
    ]:
        print("\n" + "=" * 70)
        print(name)
        print("=" * 70)
        print(prompt)

        for run_number in range(1, RUNS + 1):
            output, latency = run(prompt)
            words = len(output.split())

            print(f"\n--- Run {run_number} | {latency:.2f}s | {words} words ---")
            print(output)


if __name__ == "__main__":
    main()
