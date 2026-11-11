
import random
import time

MAX_ATTEMPTS = 4
BASE_DELAY_SECONDS = 0.5
MAX_DELAY_SECONDS = 4.0

# Deterministic demonstration:
# the first two attempts fail, and the third succeeds.
SIMULATED_OUTCOMES = [
    "temporary_failure",
    "temporary_failure",
    "success",
]


class TemporaryServiceError(Exception):
    pass


def simulated_service(attempt: int) -> str:
    print(f"Service request, attempt {attempt}")

    outcome = SIMULATED_OUTCOMES[
        min(attempt - 1, len(SIMULATED_OUTCOMES) - 1)
    ]

    if outcome == "temporary_failure":
        raise TemporaryServiceError(
            "Simulated temporary service failure."
        )

    return "Service response received successfully."


def request_with_retry() -> str:
    for attempt in range(1, MAX_ATTEMPTS + 1):
        try:
            return simulated_service(attempt)

        except TemporaryServiceError as exc:
            print("Error:", exc)

            if attempt == MAX_ATTEMPTS:
                print("Retry budget exhausted.")
                raise

            # Exponential backoff with jitter.
            delay = min(
                BASE_DELAY_SECONDS * (2 ** (attempt - 1)),
                MAX_DELAY_SECONDS,
            )
            delay += random.uniform(0, 0.2)

            print(f"Retrying after {delay:.2f} seconds...")
            time.sleep(delay)

    raise RuntimeError("Unexpected termination.")


def main():
    try:
        result = request_with_retry()
        print("\nResult:", result)
    except TemporaryServiceError:
        print("\nRequest failed after all permitted attempts.")


if __name__ == "__main__":
    main()

