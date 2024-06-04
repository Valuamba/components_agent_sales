from openai import OpenAI
from schemas.completion import CompletionResponse

import time


completion_pricing_per_1k_tokens_usd = {
    "gpt-4-1106-preview": {"input": 0.01, "output": 0.03},
    "gpt-4-1106-vision-preview": {"input": 0.01, "output": 0.03},
    "gpt-4": {"input": 0.03, "output": 0.06},
    "gpt-4o": {"input": 0.005, "output": 0.015},
    "gpt-4-32k": {"input": 0.06, "output": 0.12},
    "gpt-3.5-turbo-1106": {"input": 0.0010, "output": 0.002},
    "gpt-3.5-turbo-instruct": {"input": 0.0010, "output": 0.002},
}

assistants_api_price_usd = {
    "Code interpreter": {"input": 0.03},
    "Retrieval": {"input": 0.2},
}

embedding_price_per_1k_tokens_usd = {"text-embedding-ada-002": {"usage": 0.0001}}


class OpenAIClient:
    def __init__(self, client: OpenAI) -> None:
        self.client: OpenAI = client

    @classmethod
    def count_usage_price(
        cls, completion_tokens: int, prompt_tokens: int, model: str
    ) -> float:
        model_pricing_info = completion_pricing_per_1k_tokens_usd[model]

        return (
            completion_tokens * model_pricing_info["output"]
            + prompt_tokens * model_pricing_info["input"]
        ) / 1000

    def create_completion(self, model: str, messages, **kwargs) -> CompletionResponse:
        start_time = time.time()

        resp = self.client.chat.completions.create(
            model=model, messages=messages, **kwargs
        )

        end_time = time.time()

        choice = resp.choices[0]

        if choice.finish_reason != "stop":
            raise Exception(
                f"The chat completion was ended due to {choice.finish_reason}"
            )

        elapsed_time_ms = (end_time - start_time) * 1000

        completion_response = CompletionResponse(
            completion_tokens=resp.usage.completion_tokens,
            prompt_tokens=resp.usage.prompt_tokens,
            content=choice.message.content,
            model=model,
            usage_cost_usd=self.count_usage_price(
                resp.usage.completion_tokens, resp.usage.prompt_tokens, model
            ),
            completion_time_ms=elapsed_time_ms
        )

        return completion_response
