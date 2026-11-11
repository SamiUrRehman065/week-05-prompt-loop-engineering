from ollama import chat

MODEL = "qwen2.5:7b"

prompt = """
Explain why software systems validate LLM output.
Use exactly three bullet points.
"""


for temperature in [0, 0.7, 1.0]:
    print(f"\n--- Temperature: {temperature} ---")

    for run in range(2):
        response = chat(
            model=MODEL,
            messages=[
                {"role": "user", "content": prompt}
            ],
            options={"temperature": temperature},
        )

        print(f"\nRun {run + 1}:")
        print(response.message.content)
