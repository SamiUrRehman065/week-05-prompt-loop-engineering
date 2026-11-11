import time
from dataclasses import dataclass

import httpx
from ollama import Client, ResponseError

from config import MODEL, OLLAMA_HOST, REQUEST_TIMEOUT_SECONDS, TEMPERATURE
from errors import LLMServiceError, ModelUnavailableError


@dataclass
class LLMReply:
    content: str
    latency_seconds: float
    prompt_tokens: int
    output_tokens: int


class OllamaClient:
    def __init__(
        self,
        model: str = MODEL,
        host: str = OLLAMA_HOST,
        timeout: float = REQUEST_TIMEOUT_SECONDS,
    ):
        self.model = model
        self.host = host
        self._client = Client(host=host, timeout=timeout)

    def chat_json(self, messages: list[dict]) -> LLMReply:
        start = time.perf_counter()

        try:
            response = self._client.chat(
                model=self.model,
                messages=messages,
                format="json",
                options={"temperature": TEMPERATURE},
            )
        except ResponseError as exc:
            if exc.status_code == 404:
                raise ModelUnavailableError(
                    f"Model '{self.model}' was not found. "
                    f"Run: ollama pull {self.model}"
                ) from exc
            raise LLMServiceError(f"Ollama returned an error: {exc.error}") from exc
        except (ConnectionError, httpx.TransportError) as exc:
            raise LLMServiceError(
                f"Could not reach Ollama at {self.host}. Is it running?"
            ) from exc

        return LLMReply(
            content=response.message.content.strip(),
            latency_seconds=time.perf_counter() - start,
            prompt_tokens=response.prompt_eval_count or 0,
            output_tokens=response.eval_count or 0,
        )
