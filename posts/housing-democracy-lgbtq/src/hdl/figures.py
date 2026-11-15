"""Static, publication-quality figures (PNG + SVG).

Colours follow the dataviz reference palette: categorical slots in fixed
order (blue, orange, aqua; at most three per chart), a single-hue blue ramp
for ordered categories, recessive grid and axes, text in neutral inks.
"""
from __future__ import annotations

import textwrap

import matplotlib

matplotlib.use("Agg")
import matplotlib.pyplot as plt  # noqa: E402
import numpy as np  # noqa: E402
import pandas as pd  # noqa: E402

from .paths import FIG  # noqa: E402

SURFACE = "#fcfcfb"
INK = "#0b0b0b"
INK2 = "#52514e"
GRID = "#e4e3df"
S1, S2, S3 = "#2a78d6", "#eb6834", "#1baf7a"
BLUE_RAMP = ["#c6dbf5", "#86b2e8", "#2a78d6", "#174a8b"]  # light -> dark, ordered categories


def style() -> None:
    plt.rcParams.update({
        "figure.facecolor": SURFACE, "axes.facecolor": SURFACE, "savefig.facecolor": SURFACE,
        "axes.edgecolor": INK2, "axes.labelcolor": INK, "xtick.color": INK2, "ytick.color": INK2,
        "text.color": INK, "axes.grid": True, "grid.color": GRID, "grid.linewidth": 0.8,
        "axes.spines.top": False, "axes.spines.right": False, "font.size": 10,
        "axes.titlesize": 11, "axes.titleweight": "bold", "axes.titlelocation": "left",
        "legend.frameon": False, "figure.dpi": 110, "savefig.dpi": 200, "lines.linewidth": 2,
    })


_ZILLOW = "Zillow Home Value Index (ZHVI), Zillow Group"
_SDI = "UC Berkeley State Democracy Index 2.0 (Grumbach & Bitton)"
_MAP = "Movement Advancement Project policy tallies (via Internet Archive)"

# Source line printed under every figure. Zillow's terms require clear attribution.
SOURCES = {
    "f01_sdi_vs_home_values_2023": [_ZILLOW, _SDI],
    "f02_annual_correlations": [_ZILLOW, _SDI],
    "f03_within_state": [_ZILLOW, _SDI, "BEA PCE price index"],
    "f04_leave_one_out": [_ZILLOW, _SDI, "U.S. Census Bureau ACS and 2020 Census"],
    "f05_price_level_extension": [_ZILLOW, _SDI, "BEA Regional Price Parities and personal income",
                                  "U.S. Census Bureau"],
    "f06_hrc_categories": [_ZILLOW, "Human Rights Campaign State Equality Index 2023"],
    "f07_map_scatter": [_ZILLOW, _MAP, _SDI],
    "f08_price_to_income": [_ZILLOW, _SDI, "U.S. Census Bureau ACS 1-year"],
    "f09_map_annual": [_ZILLOW, _MAP, _SDI],
    "f10_zhvi_vs_acs": [_ZILLOW, "U.S. Census Bureau ACS 1-year"],
    "f11_entry_points": [_ZILLOW + " (state and county)", "U.S. Census Bureau 2020 Census", _SDI, _MAP],
    "f12_mover_cost_share": [_ZILLOW + " (state and county)", "U.S. Census Bureau ACS 1-year",
                             "Freddie Mac Primary Mortgage Market Survey", _SDI, _MAP],
}


def _add_source(fig, name: str) -> None:
    if name not in SOURCES:
        raise KeyError(f"no source line defined for figure {name}")
    text = "Source: " + "; ".join(SOURCES[name]) + ". Author's calculations."
    renderer = fig.canvas.get_renderer()
    bb = fig.get_tightbbox(renderer)
    h = fig.get_figheight()
    # wrap to the figure's drawn width (~17 characters per inch at 7.5 pt)
    text = textwrap.fill(text, width=max(60, int((bb.x1 - bb.x0) * 17)))
    fig.text(bb.x0 / fig.get_figwidth(), (bb.y0 - 0.08) / h, text, ha="left", va="top", fontsize=7.5,
             color=INK2, wrap=False)


def save(fig, name: str) -> str:
    _add_source(fig, name)
    fig.savefig(FIG / f"{name}.png", bbox_inches="tight")
    fig.savefig(FIG / f"{name}.svg", bbox_inches="tight")
    plt.close(fig)
    return f"output/figures/{name}.png"


def _label_points(ax, x, y, labels, highlight=None, size=7):
    highlight = set(highlight or [])
    for xi, yi, lab in zip(x, y, labels):
        ax.annotate(lab, (xi, yi), xytext=(3, 2), textcoords="offset points", fontsize=size,
                    color=INK if lab in highlight else INK2,
                    fontweight="bold" if lab in highlight else "normal")


def _fit_line(ax, x, y, color=INK2, logy=False):
    yy = np.log(y) if logy else y
    b, a = np.polyfit(x, yy, 1)
    xs = np.linspace(np.min(x), np.max(x), 50)
    fit = a + b * xs
    ax.plot(xs, np.exp(fit) if logy else fit, color=color, lw=2, alpha=0.9, zorder=1)


def log_dollar_axis(ax, ticks=(150e3, 200e3, 300e3, 400e3, 600e3, 800e3)):
    ax.set_yscale("log")
    ax.yaxis.set_major_locator(matplotlib.ticker.FixedLocator(ticks))
    ax.yaxis.set_minor_formatter(matplotlib.ticker.NullFormatter())
    dollars(ax)


def scatter_labeled(ax, x, y, labels, xlabel, ylabel, title, highlight=None, color=S1, fit=True, logy=False):
    ax.scatter(x, y, s=34, color=color, edgecolor=SURFACE, linewidth=1.2, zorder=3)
    if fit:
        _fit_line(ax, np.asarray(x, float), np.asarray(y, float), logy=logy)
    _label_points(ax, x, y, labels, highlight)
    ax.set_xlabel(xlabel)
    ax.set_ylabel(ylabel)
    ax.set_title(title)


def dollars(ax, axis="y"):
    fmt = matplotlib.ticker.FuncFormatter(lambda v, _: f"${v/1000:,.0f}k")
    (ax.yaxis if axis == "y" else ax.xaxis).set_major_formatter(fmt)


def coef_plot(ax, df: pd.DataFrame, label_col: str, title: str, xlabel: str, color=S1, zero=True):
    """Horizontal point-and-interval plot. df needs coef, ci_low, ci_high."""
    y = np.arange(len(df))[::-1]
    ax.hlines(y, df.ci_low, df.ci_high, color=color, lw=2)
    ax.scatter(df.coef, y, s=40, color=color, edgecolor=SURFACE, linewidth=1.2, zorder=3)
    ax.set_yticks(y)
    ax.set_yticklabels(df[label_col])
    if zero:
        ax.axvline(0, color=INK2, lw=1, ls="--")
    ax.set_title(title)
    ax.set_xlabel(xlabel)
    ax.grid(axis="y", visible=False)
