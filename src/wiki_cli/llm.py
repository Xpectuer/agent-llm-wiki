"""Claude API wrapper for wiki CLI."""

from __future__ import annotations

import json
import sys
from typing import Any, Callable

import anthropic

from .config import Config
from .tracker import get_tracker


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
    get_tracker().record(usage, config.model)
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


def call_claude_with_tools(
    config: Config,
    system: str,
    user: str,
    tools: list[dict[str, Any]],
    *,
    execute_tool: Callable[[str, dict[str, Any]], str],
    max_turns: int = 8,
    max_tokens: int = 4096,
) -> str:
    """Call Claude with tool definitions. Loops until a final text response
    (no more tool calls) or max_turns is exhausted."""
    client = anthropic.Anthropic(
        api_key=config.api_key,
        base_url=config.base_url,
    )

    messages: list[dict[str, Any]] = [
        {"role": "user", "content": user}
    ]

    text_parts: list[str] = []

    for turn in range(max_turns):
        message = client.messages.create(
            model=config.model,
            max_tokens=max_tokens,
            system=system,
            messages=messages,
            tools=tools,
        )

        usage = message.usage
        get_tracker().record(usage, config.model)
        print(
            f"[LLM turn {turn + 1}] {usage.input_tokens} input + "
            f"{usage.output_tokens} output tokens (model: {config.model})",
            file=sys.stderr,
        )

        # Separate text and tool_use blocks
        text_parts.clear()
        tool_use_blocks: list[Any] = []

        for block in message.content:
            if block.type == "text":
                text_parts.append(block.text)
            elif block.type == "tool_use":
                tool_use_blocks.append(block)

        # Build assistant content from all blocks
        assistant_content: list[dict[str, Any]] = []
        for block in message.content:
            if block.type == "text":
                assistant_content.append({"type": "text", "text": block.text})
            elif block.type == "tool_use":
                assistant_content.append({
                    "type": "tool_use",
                    "id": block.id,
                    "name": block.name,
                    "input": block.input,
                })

        messages.append({"role": "assistant", "content": assistant_content})

        # Done if no tool calls
        if not tool_use_blocks:
            return "\n".join(text_parts)

        # Execute each tool and collect results
        tool_results: list[dict[str, Any]] = []
        for tb in tool_use_blocks:
            print(
                f"  [Tool] {tb.name}({json.dumps(tb.input, ensure_ascii=False)})",
                file=sys.stderr,
            )
            try:
                result = execute_tool(tb.name, tb.input)
                tool_results.append({
                    "type": "tool_result",
                    "tool_use_id": tb.id,
                    "content": result,
                })
            except Exception as e:
                tool_results.append({
                    "type": "tool_result",
                    "tool_use_id": tb.id,
                    "content": f"Error: {e}",
                    "is_error": True,
                })

        messages.append({"role": "user", "content": tool_results})

    return (
        "\n".join(text_parts)
        + "\n\n[工具调用超过最大轮次，回答可能不完整。]"
    )
