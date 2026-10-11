"""Plot helpers. Titles avoid dash characters.

Omar Vasquez, CSC 5300 Week 7.
"""

from __future__ import annotations

from pathlib import Path
from typing import Sequence

import matplotlib

matplotlib.use("Agg")
import matplotlib.pyplot as plt
from matplotlib.ticker import NullLocator


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


def _short_number(value) -> str:
    """100000 becomes 100k so tick labels near each other do not overlap."""
    if value >= 1000 and value % 1000 == 0:
        return f"{int(value) // 1000}k"
    return str(value)


def _draw_errorbars(ax, series: dict, logx: bool, logy: bool) -> None:
    """series maps a label to (xs, means, stds). stds can be None for a plain line."""
    all_xs = set()
    for label, (xs, ys, errs) in series.items():
        if not xs:
            continue
        ax.errorbar(xs, ys, yerr=errs, marker="o", capsize=4, label=label)
        all_xs.update(xs)
    if logx:
        ax.set_xscale("log")
    # Label the tested x values themselves instead of powers of ten.
    ticks = sorted(all_xs)
    ax.set_xticks(ticks)
    ax.set_xticklabels([_short_number(tick) for tick in ticks])
    ax.xaxis.set_minor_locator(NullLocator())
    if logy:
        ax.set_yscale("log")
    ax.legend()


def save_errorbar_plot(
    path: Path,
    series: dict,
    xlabel: str,
    ylabel: str,
    title: str,
    logx: bool = False,
    logy: bool = False,
) -> None:
    """One chart of means with one standard deviation error bars."""
    path.parent.mkdir(parents=True, exist_ok=True)
    fig, ax = plt.subplots(figsize=(8, 5))
    _draw_errorbars(ax, series, logx, logy)
    ax.set_xlabel(xlabel)
    ax.set_ylabel(ylabel)
    ax.set_title(title)
    fig.tight_layout()
    fig.savefig(path)
    plt.close(fig)


def save_panel_plot(
    path: Path,
    panels: dict,
    xlabel: str,
    ylabel: str,
    title: str,
    logx: bool = False,
    logy: bool = False,
) -> None:
    """Side by side charts. panels maps a panel title to a series dict."""
    path.parent.mkdir(parents=True, exist_ok=True)
    count = len(panels)
    cols = 2 if count > 1 else 1
    rows = (count + cols - 1) // cols
    fig, axes = plt.subplots(rows, cols, figsize=(6 * cols, 4.5 * rows), squeeze=False)
    flat = [ax for row in axes for ax in row]
    for ax, (panel_title, series) in zip(flat, panels.items()):
        _draw_errorbars(ax, series, logx, logy)
        ax.set_title(panel_title)
        ax.set_xlabel(xlabel)
        ax.set_ylabel(ylabel)
    for ax in flat[count:]:
        ax.set_visible(False)
    fig.suptitle(title)
    fig.tight_layout()
    fig.savefig(path)
    plt.close(fig)
