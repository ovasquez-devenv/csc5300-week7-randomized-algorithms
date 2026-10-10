"""Plot helpers. Titles avoid dash characters.

Omar Vasquez, CSC 5300 Week 7.
"""

from __future__ import annotations

from pathlib import Path
from typing import Sequence

import matplotlib

matplotlib.use("Agg")
import matplotlib.pyplot as plt


def save_line_plot(
    path: Path,
    series: dict,
    xlabel: str,
    ylabel: str,
    title: str,
) -> None:
    """series maps a label to (xs, ys)."""
    path.parent.mkdir(parents=True, exist_ok=True)
    fig, ax = plt.subplots(figsize=(8, 5))
    for label, (xs, ys) in series.items():
        ax.plot(xs, ys, marker="o", label=label)
    ax.set_xlabel(xlabel)
    ax.set_ylabel(ylabel)
    ax.set_title(title)
    ax.legend()
    fig.tight_layout()
    fig.savefig(path)
    plt.close(fig)
