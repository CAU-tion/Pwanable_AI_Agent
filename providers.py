from __future__ import annotations

import json
import os
from dataclasses import dataclass, field


@dataclass
class ToolCall:
    id: str
    name: str
    arguments: dict


@dataclass
class LLMMessage:
    role: str
    content: str | None
    tool_calls: list[ToolCall] | None = None

    def to_dict(self) -> dict:
        d: dict = {"role": self.role}

        if self.content is not None:
            d["content"] = self.content

        if self.tool_calls:
            d["tool_calls"] = [
                {
                    "id": tc.id,
                    "name": tc.name,
                    "arguments": tc.arguments
                }
                for tc in self.tool_calls
            ]

        return d


class LLMProvider:
    name: str = "base"

    def complete(self, messages: list[dict], tools: list[dict]) -> LLMMessage:
        raise NotImplementedError

    def __str__(self) -> str:
        return self.name


class OpenAICompatProvider(LLMProvider):

    def __init__(
        self,
        api_key: str,
        model: str,
        base_url: str | None = None,
        label: str = "gemini",
    ):
        from openai import OpenAI

        kwargs: dict = {"api_key": api_key}

        if base_url:
            kwargs["base_url"] = base_url

        self.client = OpenAI(**kwargs)
        self.model = model
        self.name = f"{label}/{model}"

    def complete(self, messages: list[dict], tools: list[dict]) -> LLMMessage:
        kwargs: dict = {
            "model": self.model,
            "messages": _to_openai_messages(messages),
        }

        if tools:
            kwargs["tools"] = tools
            kwargs["tool_choice"] = "auto"

        response = self.client.chat.completions.create(**kwargs)
        msg = response.choices[0].message

        tool_calls = None

        if msg.tool_calls:
            tool_calls = [
                ToolCall(
                    id=tc.id,
                    name=tc.function.name,
                    arguments=json.loads(tc.function.arguments),
                )
                for tc in msg.tool_calls
            ]

        return LLMMessage(
            role="assistant",
            content=msg.content,
            tool_calls=tool_calls,
        )


def _to_openai_messages(canonical: list[dict]) -> list[dict]:
    result = []

    for msg in canonical:
        if msg["role"] == "tool":
            result.append({
                "role": "tool",
                "tool_call_id": msg["tool_call_id"],
                "content": msg["content"],
            })

        elif msg["role"] == "assistant" and msg.get("tool_calls"):
            result.append({
                "role": "assistant",
                "content": msg.get("content"),
                "tool_calls": [
                    {
                        "id": tc["id"],
                        "type": "function",
                        "function": {
                            "name": tc["name"],
                            "arguments": json.dumps(tc["arguments"]),
                        },
                    }
                    for tc in msg["tool_calls"]
                ],
            })

        else:
            result.append({
                "role": msg["role"],
                "content": msg.get("content", ""),
            })

    return result


_DEFAULTS: dict[str, str] = {
    "gemini": "gemini-2.0-flash",
}


def create_provider(provider: str, model: str | None = None) -> LLMProvider:
    model = model or _DEFAULTS.get(provider, "")

    if provider == "gemini":
        return OpenAICompatProvider(
            api_key=_require_env("GEMINI_API_KEY"),
            model=model,
            base_url="https://generativelanguage.googleapis.com/v1beta/openai/",
            label="gemini",
        )

    raise ValueError(
        f"Unknown provider '{provider}'. Choose from: gemini"
    )


def _require_env(key: str) -> str:
    val = os.environ.get(key)

    if not val:
        raise EnvironmentError(
            f"Environment variable {key} is not set. "
            f"Add it to your .env file or export it in your shell."
        )

    return val