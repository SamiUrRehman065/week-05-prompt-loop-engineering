
from ollama import chat

from demo_2 import build_prompt

test_claims = [
    "A pipe burst in my house, but I have no repair estimate.",
    "My car was hit in a parking lot, and the other driver left.",
    "My laptop was stolen from my office, but I have no police report.",
]

for index, claim in enumerate(test_claims, start=1):
    prompt = build_prompt(claim)

    response = chat(
        model="qwen2.5:7b",
        messages=[
            {
                "role": "user",
                "content": prompt,
            }
        ],
    )

    print(f"\nTEST CLAIM {index}: {claim}")
    print(response.message.content)

