"""Getting completions from a large language model."""

import typing as t

import litellm
from litellm.types.utils import ModelResponse
from pydantic import BaseModel

from auto_survey.data_models import LiteLLMConfig


def get_llm_completion(
    messages: list[dict[str, str]],
    temperature: float,
    max_tokens: int,
    response_format: t.Type[BaseModel] | None,
    litellm_config: LiteLLMConfig,
) -> str:
    """Get a completion from the LLM.

    Args:
        messages:
            The messages to use for the completion. Each message is a dict with keys
            "role" and "content". The "role" can be "system", "user", or "assistant".
            The "content" is the content of the message.
        temperature:
            The temperature to use for the completion.
        max_tokens:
            The maximum number of tokens to generate.
        response_format:
            The response format to use. Can be None if no specific format is needed.
        litellm_config:
            The LiteLLM configuration to use.

    Returns:
        The completion from the LLM.
    """
    response = litellm.completion(
        messages=messages,
        temperature=temperature,
        max_tokens=max_tokens,
        response_format=response_format,
        **litellm_config.model_dump(),
    )
    assert isinstance(response, ModelResponse)
    choice = response.choices[0]
    assert isinstance(choice, litellm.Choices)
    completion = choice.message.content or ""
    return completion
