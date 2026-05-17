---
title: "MultiSpinner ContextVar Delegation Pattern for Parallel Terminal Output"
doc_type: lesson
brief: "使用 ContextVar 在线程池中协调多个 spinner 槽位，避免并行 stderr 写入冲突"
confidence: verified
created: 2026-05-17
updated: 2026-05-17
revision: 1
---

# MultiSpinner ContextVar Delegation Pattern

> Source(s): commit de76129, `src/wiki_cli/llm.py`, `src/wiki_cli/executor.py`

## Problem

When running multiple LLM API calls in parallel via `ThreadPoolExecutor`, each call
typically starts its own terminal spinner animation on stderr. Multiple concurrent
spinners writing to stderr independently produce garbled, flickering output and can
corrupt the terminal display. This happens because each spinner thread writes `\r`
(carriage return) to overwrite the same line without coordination.

## Pattern

Use Python `ContextVar` (thread-aware) to create a shared **MultiSpinner** that all
worker threads can register with. When a MultiSpinner context manager is active,
individual `_Spinner` instances detect it via ContextVar and **delegate** their
display to a single rendering thread, rather than starting their own animation
threads. The MultiSpinner renders a single consolidated line showing all active
worker slots.

## Key Components

### 1. ContextVars for thread-aware state

```python
_active_multi_spinner: ContextVar["MultiSpinner | None"] = ContextVar(
    "_active_multi_spinner", default=None
)
_spinner_label: ContextVar[str] = ContextVar("_spinner_label", default="")
```

- `_active_multi_spinner`: References the shared `MultiSpinner` instance. Set in
  `MultiSpinner.__enter__`, reset in `__exit__`. Each worker thread sees it because
  `ContextVar` values propagate across threads created by `ThreadPoolExecutor`.
- `_spinner_label`: Each worker thread sets its own label (e.g., chapter ID) before
  making API calls. The MultiSpinner reading thread uses this to identify which slot
  belongs to which worker.

### 2. MultiSpinner: single-line slot renderer

The MultiSpinner maintains a `_slots` dict `{slot_id: (label, message)}` protected by
a threading lock. A daemon renderer thread loops, reads all current slots, and writes
a single line to stderr:

```
  ⠋ [ch-01] Thinking... | ⠙ [ch-02] Thinking... | ⠹ [ch-03] Thinking...
```

The `\r` carriage return repositions the cursor at the start of the line for the
next frame. No ANSI cursor-movement codes are used, which avoids terminal cursor
conflicts when stdout `print()` output is interleaved.

### 3. _Spinner delegation (the core innovation)

When `_Spinner.__enter__` runs, it checks `_active_multi_spinner.get()`:

- **MultiSpinner active**: reads `_spinner_label.get()` for the label, calls
  `ms.add(label, message)` to register a slot, stores the `slot_id`. On `__exit__`,
  calls `ms.remove(slot_id)`. No animation thread is started.
- **MultiSpinner not active**: starts its own animation thread (legacy standalone
  behavior).

### 4. stderr / stdout output routing

While MultiSpinner owns stderr for the animation line, other log output (token usage
stats, tool-call logs) must not write to stderr. The helper `_stderr_safe()` returns
`False` when MultiSpinner is active, redirecting log output to stdout:

```python
def _stderr_safe() -> bool:
    return _active_multi_spinner.get() is None
```

### 5. Result printing outside MultiSpinner

Results (success/failure per chapter) are collected silently inside the MultiSpinner
context, then printed after the context exits. This avoids terminal cursor conflicts
where `print()` output would displace the spinner animation line.

## Why ContextVar instead of threading.local

`ThreadPoolExecutor` reuses threads across futures. A `threading.local` value set in
worker A's thread might persist when the same OS thread is later assigned to worker
B. `ContextVar` correctly isolates values per logical context (each `future.submit`
creates a new context copy), so a label set by worker A does not leak to worker B
even if they share the same OS thread.

## Usage in executor.py

```python
with MultiSpinner():
    with ThreadPoolExecutor(max_workers=min(max_workers, len(level))) as executor:
        for ch in chapters_in_level:
            executor.submit(_process_chapter, config, ch, ch_text, get_page_lock)
        # Collect results silently (no print)
        for future in as_completed(futures):
            result = future.result()
            level_results.append(result)

# Print results AFTER MultiSpinner exits (clean stderr)
for result in level_results:
    print(f"    {'✓' if result.status == 'success' else '✗'} {result.chapter_id}: ...")
```

And inside `_process_chapter`:

```python
_spinner_label.set(chapter.id)  # set before any LLM call
# ... call_claude / call_claude_with_tools (their _Spinner auto-delegates) ...
```

## Benefits

- Single consolidated animation line instead of overlapping stochastic output
- No terminal corruption from concurrent `\r` writes
- Worker threads need no knowledge of the coordination mechanism -- they just set a label
- Output routing is transparent to callers (`_stderr_safe()` check is inside `call_claude`)
- Clean fallback: when no MultiSpinner is active, _Spinner works as standalone
