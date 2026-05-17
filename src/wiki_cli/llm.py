"""Claude API wrapper for wiki CLI."""

from __future__ import annotations

import json
import sys
import threading
import time
from collections.abc import Callable
from contextvars import ContextVar
from typing import Any

import anthropic

from .config import Config
from .tracker import effective_input_tokens, get_tracker

# ContextVar for MultiSpinner delegation. When set, _Spinner registers
# with the shared MultiSpinner instead of starting its own thread.
_active_multi_spinner: ContextVar[MultiSpinner | None] = ContextVar(
    "_active_multi_spinner", default=None
)

# ContextVar for the current spinner label (e.g. chapter ID).
_spinner_label: ContextVar[str] = ContextVar("_spinner_label", default="")


class MultiSpinner:
    """Coordinates multiple spinner slots for parallel LLM calls.

    Renders a single line on stderr that shows all active workers::

          ⠋ [ch1] Thinking... | ⠙ [ch2] Thinking...

    Uses ``\\r`` (carriage return) to update in place — no multi-line ANSI
    cursor codes, so it coexists peacefully with stdout ``print()`` output.
    Install with ``with MultiSpinner():`` — _Spinner instances will
    automatically register as slots instead of starting their own threads.
    """

    FRAMES = ["⠋", "⠙", "⠹", "⠸", "⠼", "⠴", "⠦", "⠧", "⠇", "⠸"]

    def __init__(self):
        self._slots: dict[int, tuple[str, str]] = {}  # slot_id -> (label, message)
        self._lock = threading.Lock()
        self._running = False
        self._thread: threading.Thread | None = None
        self._next_slot_id = 0
        self._token: ContextVar.Token | None = None

    # -- public API for _Spinner delegation ---

    def add(self, label: str, message: str) -> int:
        """Register a new spinner slot. Returns slot_id."""
        with self._lock:
            sid = self._next_slot_id
            self._next_slot_id += 1
            self._slots[sid] = (label, message)
            return sid  # type: ignore[no-any-return]

    def remove(self, slot_id: int) -> None:
        """Remove a spinner slot."""
        with self._lock:
            self._slots.pop(slot_id, None)

    # -- internal rendering ---

    def _render(self) -> None:
        frame_idx = 0
        while self._running:
            with self._lock:
                slots = list(self._slots.items())

            if not slots:
                # No active slots: clear the line and wait
                sys.stderr.write("\r\033[K")
                sys.stderr.flush()
                time.sleep(0.1)
                continue

            frame = self.FRAMES[frame_idx % len(self.FRAMES)]
            frame_idx += 1

            parts: list[str] = []
            for _sid, (label, message) in slots:
                label_part = f"[{label}] " if label else ""
                parts.append(f"{frame} {label_part}{message}")

            sys.stderr.write(f"\r  {' | '.join(parts)}\033[K")
            sys.stderr.flush()
            time.sleep(0.1)

    def _cleanup(self) -> None:
        sys.stderr.write("\r\033[K")
        sys.stderr.flush()

    def __enter__(self) -> MultiSpinner:
        self._running = True
        self._token = _active_multi_spinner.set(self)
        self._thread = threading.Thread(target=self._render, daemon=True)
        self._thread.start()
        return self

    def __exit__(self, *args: Any) -> None:
        self._running = False
        if self._thread:
            self._thread.join(timeout=0.5)
        self._cleanup()
        if self._token is not None:
            _active_multi_spinner.reset(self._token)
            self._token = None


class _Spinner:
    """Terminal spinner for indicating LLM wait time.

    When a MultiSpinner is active (via ContextVar), this delegates to it
    instead of starting its own animation thread — enabling stacked
    multi-line display during parallel execution.
    """

    FRAMES = ["⠋", "⠙", "⠹", "⠸", "⠼", "⠴", "⠦", "⠧", "⠇", "⠸"]

    def __init__(self, message: str, *, quiet: bool = False):
        self._message = message
        self._quiet = quiet
        self._running = False
        self._thread: threading.Thread | None = None
        self._slot_id: int | None = None  # used in delegated mode

    def _animate(self):
        i = 0
        while self._running:
            sys.stderr.write(f"\r  {self.FRAMES[i]} {self._message}")
            sys.stderr.flush()
            i = (i + 1) % len(self.FRAMES)
            time.sleep(0.1)
        # Clear spinner line
        sys.stderr.write("\r" + " " * (len(self._message) + 10) + "\r")
        sys.stderr.flush()

    def __enter__(self):
        if self._quiet:
            return self
        ms = _active_multi_spinner.get()
        if ms is not None:
            label = _spinner_label.get()
            self._slot_id = ms.add(label, self._message)
            return self
        self._running = True
        self._thread = threading.Thread(target=self._animate, daemon=True)
        self._thread.start()
        return self

    def __exit__(self, *args):
        if self._quiet:
            return
        if self._slot_id is not None:
            ms = _active_multi_spinner.get()
            if ms is not None:
                ms.remove(self._slot_id)
            self._slot_id = None
            return
        self._running = False
        if self._thread:
            self._thread.join(timeout=0.5)


def _stderr_safe() -> bool:
    """Return True when it's safe to write info lines to stderr
    (i.e. no MultiSpinner is actively rendering there)."""
    return _active_multi_spinner.get() is None


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

    with _Spinner(f"Thinking (model: {config.model})...", quiet=config.quiet):
        message = client.messages.create(
            model=config.model,
            max_tokens=max_tokens,
            system=system,
            messages=[{"role": "user", "content": user}],
        )

    usage = message.usage
    get_tracker().record(usage, config.model)
    # During parallel execution, emit to stdout so we don't disrupt the
    # MultiSpinner which owns stderr for animated lines.
    out = sys.stderr if _stderr_safe() else sys.stdout
    print(
        f"[LLM] {effective_input_tokens(usage)} input + {usage.output_tokens} output tokens "
        f"(model: {config.model})",
        file=out,
    )

    for block in message.content:
        if block.type == "text":
            return block.text  # type: ignore[no-any-return]
    return ""


def call_claude_json(
    config: Config,
    system: str,
    user: str,
    *,
    max_tokens: int = 4096,
) -> Any:
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

    messages: list[dict[str, Any]] = [{"role": "user", "content": user}]

    text_parts: list[str] = []

    for turn in range(max_turns):
        with _Spinner(f"Thinking (model: {config.model})...", quiet=config.quiet):
            message = client.messages.create(
                model=config.model,
                max_tokens=max_tokens,
                system=system,
                messages=messages,
                tools=tools,
            )

        usage = message.usage
        get_tracker().record(usage, config.model)
        out = sys.stderr if _stderr_safe() else sys.stdout
        print(
            f"[LLM turn {turn + 1}] {effective_input_tokens(usage)} input + "
            f"{usage.output_tokens} output tokens (model: {config.model})",
            file=out,
        )

        # Separate text and tool_use blocks
        text_parts.clear()
        tool_use_blocks: list[Any] = []

        for block in message.content:
            if block.type == "text":
                text_parts.append(block.text)
            elif block.type == "tool_use":
                tool_use_blocks.append(block)

        # Build assistant content from all blocks (including thinking blocks
        # which must be passed back to the API when present)
        assistant_content: list[dict[str, Any]] = []
        for block in message.content:
            if block.type == "text":
                assistant_content.append({"type": "text", "text": block.text})
            elif block.type == "tool_use":
                assistant_content.append(
                    {
                        "type": "tool_use",
                        "id": block.id,
                        "name": block.name,
                        "input": block.input,
                    }
                )
            elif block.type == "thinking":
                assistant_content.append(
                    {
                        "type": "thinking",
                        "thinking": block.thinking,
                    }
                )

        messages.append({"role": "assistant", "content": assistant_content})

        # Done if no tool calls
        if not tool_use_blocks:
            return "\n".join(text_parts)

        # Execute each tool and collect results
        tool_results: list[dict[str, Any]] = []
        tool_out = sys.stderr if _stderr_safe() else sys.stdout
        for tb in tool_use_blocks:
            print(
                f"  [Tool] {tb.name}({json.dumps(tb.input, ensure_ascii=False)})",
                file=tool_out,
            )
            try:
                result = execute_tool(tb.name, tb.input)
                tool_results.append(
                    {
                        "type": "tool_result",
                        "tool_use_id": tb.id,
                        "content": result,
                    }
                )
            except Exception as e:
                tool_results.append(
                    {
                        "type": "tool_result",
                        "tool_use_id": tb.id,
                        "content": f"Error: {e}",
                        "is_error": True,
                    }
                )

        messages.append({"role": "user", "content": tool_results})

    return "\n".join(text_parts) + "\n\n[工具调用超过最大轮次，回答可能不完整。]"
