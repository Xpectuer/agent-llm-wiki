"""Token usage tracker with pivot table reporting."""

from __future__ import annotations

import threading
import time
from collections import defaultdict
from contextlib import contextmanager
from dataclasses import dataclass, field
from pathlib import Path
from typing import Any


@dataclass
class TokenUsage:
    phase: str
    model: str
    input_tokens: int
    output_tokens: int
    cache_creation_input_tokens: int
    cache_read_input_tokens: int
    timestamp: float = field(default_factory=time.time)


# Approximate pricing per 1M tokens (input, output)
MODEL_PRICING: dict[str, tuple[float, float]] = {
    "claude-sonnet-4-6": (3.0, 15.0),
    "claude-sonnet-4-5": (3.0, 15.0),
    "claude-opus-4-7": (15.0, 75.0),
    "claude-opus-4-6": (15.0, 75.0),
    "claude-haiku-4-5": (1.0, 5.0),
}
DEFAULT_PRICING = (3.0, 15.0)


def effective_input_tokens(usage: Any) -> int:
    """Return effective input tokens, handling non-standard APIs that may
    report input_tokens=0 while stashing counts in cache_read_input_tokens."""
    raw_input = getattr(usage, "input_tokens", 0) or 0
    if raw_input > 0:
        return raw_input
    cache_create = getattr(usage, "cache_creation_input_tokens", 0) or 0
    cache_read = getattr(usage, "cache_read_input_tokens", 0) or 0
    return cache_create + cache_read


class TokenTracker:
    def __init__(self) -> None:
        self._lock = threading.Lock()
        self._usages: list[TokenUsage] = []
        self._current_phase = "unknown"

    def record(self, usage: Any, model: str) -> None:
        raw_output = getattr(usage, "output_tokens", 0) or 0
        effective_input = effective_input_tokens(usage)

        raw_cache_create = getattr(usage, "cache_creation_input_tokens", 0) or 0
        raw_cache_read = getattr(usage, "cache_read_input_tokens", 0) or 0

        # Cache tokens should never exceed total input. Non-standard APIs
        # (e.g. Kimi) may inflate cache counts, so cap them for integrity.
        cache_create = min(raw_cache_create, effective_input)
        cache_read = min(raw_cache_read, effective_input - cache_create)

        u = TokenUsage(
            phase=self._current_phase,
            model=model,
            input_tokens=effective_input,
            output_tokens=raw_output,
            cache_creation_input_tokens=cache_create,
            cache_read_input_tokens=cache_read,
        )
        with self._lock:
            self._usages.append(u)

    @contextmanager
    def phase(self, name: str):
        old = self._current_phase
        self._current_phase = name
        try:
            yield
        finally:
            self._current_phase = old

    def reset(self) -> None:
        with self._lock:
            self._usages.clear()

    @property
    def usages(self) -> list[TokenUsage]:
        with self._lock:
            return list(self._usages)

    def report(self) -> str:
        usages = self.usages
        if not usages:
            return "No token usage recorded."

        phase_agg, totals = self._aggregate()

        # Build table
        lines = ["", "=== Token Usage Report ===", ""]
        lines.append("Phase-wise Breakdown:")
        lines.append("")

        headers = ["Phase", "Calls", "Input", "Output", "Cache Create", "Cache Read", "Est. Cost"]
        widths = [24, 7, 12, 12, 14, 12, 12]

        def hr(left: str, mid: str, right: str) -> str:
            return left + mid.join("─" * w for w in widths) + right

        def row(vals: list[str]) -> str:
            return (
                "│ "
                + " │ ".join(
                    v.ljust(w) if i == 0 else v.rjust(w)
                    for i, (v, w) in enumerate(zip(vals, widths, strict=False))
                )
                + " │"
            )

        lines.append(hr("┌─", "─┬─", "─┐"))
        lines.append(row(headers))
        lines.append(hr("├─", "─┼─", "─┤"))

        for phase in sorted(phase_agg):
            p = phase_agg[phase]
            lines.append(
                row(
                    [
                        phase,
                        str(p["calls"]),
                        f"{p['input']:,}",
                        f"{p['output']:,}",
                        f"{p['cache_create']:,}",
                        f"{p['cache_read']:,}",
                        f"${p['cost']:.4f}",
                    ]
                )
            )

        lines.append(hr("├─", "─┼─", "─┤"))
        lines.append(
            row(
                [
                    "TOTAL",
                    str(totals["calls"]),
                    f"{totals['input']:,}",
                    f"{totals['output']:,}",
                    f"{totals['cache_create']:,}",
                    f"{totals['cache_read']:,}",
                    f"${totals['cost']:.4f}",
                ]
            )
        )
        lines.append(hr("└─", "─┴─", "─┘"))
        lines.append("")

        # Summary stats
        total_tokens = totals["input"] + totals["output"]
        if total_tokens:
            input_pct = totals["input"] / total_tokens * 100
            output_pct = totals["output"] / total_tokens * 100
        else:
            input_pct = output_pct = 0

        cache_pct = totals["cache_read"] / totals["input"] * 100 if totals["input"] else 0

        lines.append(f"Input/Output Ratio: {input_pct:.1f}% input / {output_pct:.1f}% output")
        lines.append(
            f"Cache Hit Rate: {cache_pct:.1f}% "
            f"({totals['cache_read']:,} / {totals['input']:,} input tokens from cache)"
        )
        lines.append(f"Total API Calls: {totals['calls']}")
        lines.append(f"Estimated Cost: ${totals['cost']:.4f}")

        return "\n".join(lines)

    def _aggregate(self) -> tuple[dict[str, dict], dict]:
        """Build phase-wise aggregation and totals. Returns (phase_agg, totals)."""
        usages = self.usages
        phase_agg: dict[str, dict] = defaultdict(
            lambda: {"calls": 0, "input": 0, "output": 0, "cache_create": 0, "cache_read": 0}
        )
        for u in usages:
            p = phase_agg[u.phase]
            p["calls"] += 1
            p["input"] += u.input_tokens
            p["output"] += u.output_tokens
            p["cache_create"] += u.cache_creation_input_tokens
            p["cache_read"] += u.cache_read_input_tokens

        for phase, p in phase_agg.items():
            model = next((u.model for u in usages if u.phase == phase), "")
            input_price, output_price = MODEL_PRICING.get(model, DEFAULT_PRICING)
            p["cost"] = (p["input"] * input_price + p["output"] * output_price) / 1_000_000

        totals = {
            "calls": 0,
            "input": 0,
            "output": 0,
            "cache_create": 0,
            "cache_read": 0,
            "cost": 0.0,
        }
        for p in phase_agg.values():
            for k in ("calls", "input", "output", "cache_create", "cache_read"):
                totals[k] += p[k]
            totals["cost"] += p["cost"]

        return phase_agg, totals

    def html_report(self) -> str:
        usages = self.usages
        if not usages:
            return "<html><body><p>No token usage recorded.</p></body></html>"

        phase_agg, totals = self._aggregate()

        total_tokens = totals["input"] + totals["output"]
        input_pct = totals["input"] / total_tokens * 100 if total_tokens else 0
        output_pct = totals["output"] / total_tokens * 100 if total_tokens else 0
        cache_pct = totals["cache_read"] / totals["input"] * 100 if totals["input"] else 0

        rows_html = ""
        for phase in sorted(phase_agg):
            p = phase_agg[phase]
            rows_html += f"""<tr>
                <td>{phase}</td>
                <td class="num">{p["calls"]}</td>
                <td class="num">{p["input"]:,}</td>
                <td class="num">{p["output"]:,}</td>
                <td class="num">{p["cache_create"]:,}</td>
                <td class="num">{p["cache_read"]:,}</td>
                <td class="num">${p["cost"]:.4f}</td>
            </tr>"""

        return f"""<!DOCTYPE html>
<html lang="en">
<head>
<meta charset="utf-8">
<title>Token Usage Report</title>
<style>
body {{ font-family: -apple-system, BlinkMacSystemFont, 'Segoe UI', Roboto, sans-serif; max-width: 960px; margin: 40px auto; padding: 0 20px; color: #1a1a1a; background: #fafafa; }}
h1 {{ font-size: 24px; margin-bottom: 24px; }}
table {{ width: 100%; border-collapse: collapse; margin-bottom: 32px; background: #fff; border-radius: 8px; overflow: hidden; box-shadow: 0 1px 3px rgba(0,0,0,0.08); }}
th {{ background: #f5f5f5; text-align: left; padding: 10px 14px; font-weight: 600; font-size: 13px; text-transform: uppercase; letter-spacing: 0.5px; color: #555; border-bottom: 2px solid #e0e0e0; }}
td {{ padding: 10px 14px; font-size: 14px; border-bottom: 1px solid #eee; }}
.num {{ text-align: right; font-variant-numeric: tabular-nums; }}
tr.total {{ font-weight: 700; background: #f9f9f9; border-top: 2px solid #e0e0e0; }}
.stats {{ display: grid; grid-template-columns: repeat(auto-fit, minmax(200px, 1fr)); gap: 16px; margin-bottom: 32px; }}
.stat-card {{ background: #fff; border-radius: 8px; padding: 18px; box-shadow: 0 1px 3px rgba(0,0,0,0.08); }}
.stat-card .label {{ font-size: 12px; text-transform: uppercase; letter-spacing: 0.5px; color: #777; margin-bottom: 6px; }}
.stat-card .value {{ font-size: 22px; font-weight: 700; }}
.meter {{ height: 8px; border-radius: 4px; background: #e0e0e0; margin-top: 8px; overflow: hidden; }}
.meter-fill {{ height: 100%; border-radius: 4px; }}
.meter-fill.input {{ background: #3b82f6; }}
.meter-fill.cache {{ background: #10b981; }}
</style>
</head>
<body>
<h1>Token Usage Report</h1>

<div class="stats">
    <div class="stat-card">
        <div class="label">Total Tokens</div>
        <div class="value">{total_tokens:,}</div>
        <div class="meter"><div class="meter-fill input" style="width:{input_pct:.0f}%"></div></div>
        <div style="font-size:12px;color:#777;margin-top:6px">{input_pct:.1f}% input / {output_pct:.1f}% output</div>
    </div>
    <div class="stat-card">
        <div class="label">Cache Hit Rate</div>
        <div class="value">{cache_pct:.1f}%</div>
        <div class="meter"><div class="meter-fill cache" style="width:{cache_pct:.0f}%"></div></div>
        <div style="font-size:12px;color:#777;margin-top:6px">{totals["cache_read"]:,} / {totals["input"]:,} tokens cached</div>
    </div>
    <div class="stat-card">
        <div class="label">Total API Calls</div>
        <div class="value">{totals["calls"]}</div>
    </div>
    <div class="stat-card">
        <div class="label">Estimated Cost</div>
        <div class="value">${totals["cost"]:.4f}</div>
    </div>
</div>

<table>
<thead>
<tr>
    <th>Phase</th>
    <th class="num">Calls</th>
    <th class="num">Input Tokens</th>
    <th class="num">Output Tokens</th>
    <th class="num">Cache Created</th>
    <th class="num">Cache Read</th>
    <th class="num">Est. Cost</th>
</tr>
</thead>
<tbody>
{rows_html}
<tr class="total">
    <td>TOTAL</td>
    <td class="num">{totals["calls"]}</td>
    <td class="num">{totals["input"]:,}</td>
    <td class="num">{totals["output"]:,}</td>
    <td class="num">{totals["cache_create"]:,}</td>
    <td class="num">{totals["cache_read"]:,}</td>
    <td class="num">${totals["cost"]:.4f}</td>
</tr>
</tbody>
</table>
</body>
</html>"""

    def save_report(self, path: str) -> Path:
        """Write the token usage report to a file. Format determined by extension (.html or .md)."""
        p = Path(path)
        p.parent.mkdir(parents=True, exist_ok=True)
        content = self.html_report() if p.suffix == ".html" else self.report()
        p.write_text(content, encoding="utf-8")
        return p


_tracker: TokenTracker | None = None


def get_tracker() -> TokenTracker:
    global _tracker
    if _tracker is None:
        _tracker = TokenTracker()
    return _tracker
