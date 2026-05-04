"""Claude API wrapper for wiki CLI."""

from __future__ import annotations

import json
import sys

import anthropic

from .config import Config


def call_claude(
    config: Config,
    system: str,
    user: str,
    *,
    max_tokens: int = 4096,
) -> str:
    """Call Claude API and return the response text. Prints token usage to stderr."""
    client = anthropic.Anthropic(
        api_key=config.api_key,
        base_url=config.base_url,
    )

    message = client.messages.create(
        model=config.model,
        max_tokens=max_tokens,
        system=system,
        messages=[{"role": "user", "content": user}],
    )

    usage = message.usage
    print(
        f"[LLM] {usage.input_tokens} input + {usage.output_tokens} output tokens "
        f"(model: {config.model})",
        file=sys.stderr,
    )

    return message.content[0].text


def call_claude_json(
    config: Config,
    system: str,
    user: str,
    *,
    max_tokens: int = 4096,
) -> dict | list:
    """Call Claude and parse the response as JSON."""
    raw = call_claude(config, system, user, max_tokens=max_tokens)
    # Strip markdown code fences if present
    text = raw.strip()
    if text.startswith("```"):
        lines = text.split("\n")
        # Remove first line (```json) and last line (```)
        lines = lines[1:]
        if lines and lines[-1].strip() == "```":
            lines = lines[:-1]
        text = "\n".join(lines)
    return json.loads(text)
