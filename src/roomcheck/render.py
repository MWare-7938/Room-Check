"""Pretty terminal panel for a RoomStatus."""
from __future__ import annotations
from .core import RoomStatus
from .thresholds import Thresholds, DEFAULT_THRESHOLDS

BANNERS = {
    "GREEN":   "[  SAFE   ]",
    "YELLOW":  "[ CAUTION ]",
    "RED":     "[ UNSAFE  ]",
    "UNKNOWN": "[ UNKNOWN ]",
}


def render_panel(
    result: RoomStatus,
    alert: str = "",
    timestamp: str = "",
    source: str = "",
    thresholds: Thresholds = DEFAULT_THRESHOLDS,
) -> str:
    """Build a printable terminal panel. Returns the string; caller prints it."""
    lines = []
    lines.append("")
    lines.append("=" * 60)
    header = f" ROOM CHECK  {BANNERS[result.overall]}"
    if timestamp:
        header += f"   {timestamp}"
    lines.append(header)
    if source:
        lines.append(f" Source: {source}")
    lines.append("=" * 60)
    for k, v in result.readings.items():
        st = result.parameters.get(k, "?")
        spec = getattr(thresholds, k, None)
        unit = getattr(spec, "unit", "") if spec else ""
        value_str = f"{v:>7.1f}" if isinstance(v, (int, float)) else f"{'--':>7}"
        lines.append(f"  {k:<16} {value_str} {unit:<10} [{st}]")
    if alert:
        lines.append("-" * 60)
        # Wrap long alerts.
        words = alert.split()
        line = "  ALERT:"
        for w in words:
            if len(line) + len(w) + 1 > 60:
                lines.append(line)
                line = "         " + w
            else:
                line += " " + w
        lines.append(line)
    lines.append("=" * 60)
    return "\n".join(lines)
