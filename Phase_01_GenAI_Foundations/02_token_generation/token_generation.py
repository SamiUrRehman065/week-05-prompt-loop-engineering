import re
from pathlib import Path

from ollama import chat

MODEL = "qwen2.5:7b"
PROMPTS_FILE = Path(__file__).with_name("Prompts.txt")


def load_prompts(path: Path) -> list[tuple[str, str]]:
    text = path.read_text(encoding="utf-8")
    parts = re.split(r"^(Prompt \d+):?\s*$", text, flags=re.MULTILINE)

    return [
        (parts[i], parts[i + 1].strip())
        for i in range(1, len(parts), 2)
    ]


def stream_tokens(prompt: str) -> list[str]:
    pieces = []

    stream = chat(
        model=MODEL,
        messages=[{"role": "user", "content": prompt}],
        options={"temperature": 0, "num_predict": 20},
        stream=True,
    )

    for chunk in stream:
        piece = chunk.message.content
        if piece:
            pieces.append(piece)
            print(repr(piece), end=" ", flush=True)

    print()
    return pieces


def main():
    for name, prompt in load_prompts(PROMPTS_FILE):
        print("\n" + "=" * 60)
        print(name)
        print("=" * 60)
        print(prompt)

        print("\nGenerated pieces:")
        pieces = stream_tokens(prompt)

        print("\nFull response:", "".join(pieces).strip())
        print("Number of pieces:", len(pieces))


if __name__ == "__main__":
    main()
