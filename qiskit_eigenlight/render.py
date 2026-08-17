"""
Matplotlib rendering for qiskit-eigenlight.

Two plots:
  * plot_emission_spectrum   -- glowing vertical lines at true eigenvalue
                                 gaps, colored by frequency.
  * plot_ctqw_populations    -- site-occupation dynamics over time.

Both take a matplotlib Axes if you want to compose them into a larger
figure (e.g. inside qiskit-stateviz); otherwise they create their own
figure and return it.
"""

from __future__ import annotations

from typing import Optional, Sequence

import numpy as np
import matplotlib.pyplot as plt
from matplotlib.axes import Axes
from matplotlib.colors import LinearSegmentedColormap

from .core import SpectralLine

__all__ = ["plot_emission_spectrum", "plot_ctqw_populations", "EIGENLIGHT_CMAP"]

# Custom "quantum spectrum" colormap -- not a literal visible-light mapping,
# it's an internally consistent palette used across this package.
_STOPS = [
    (0.00, "#6D4AFF"),
    (0.25, "#3B82F6"),
    (0.50, "#22D3EE"),
    (0.70, "#34D399"),
    (0.85, "#FBBF24"),
    (1.00, "#F43F5E"),
]
EIGENLIGHT_CMAP = LinearSegmentedColormap.from_list(
    "eigenlight", [c for _, c in _STOPS], N=256
)

_BG = "#090C10"
_PANEL = "#11151D"
_INK_HI = "#ECE9E1"
_INK_MID = "#9CA3AF"
_INK_LOW = "#5B6472"
_HAIR = "#22262F"

_SITE_COLORS = ["#8B8FEA", "#63C7B2", "#E0A458", "#D9647C", "#6FB1E0"]


def _style_axes(ax: Axes) -> None:
    ax.set_facecolor(_PANEL)
    ax.figure.set_facecolor(_BG)
    for spine in ax.spines.values():
        spine.set_visible(False)
    ax.tick_params(colors=_INK_LOW, labelsize=9)
    ax.xaxis.label.set_color(_INK_MID)
    ax.yaxis.label.set_color(_INK_MID)
    ax.title.set_color(_INK_HI)
    ax.grid(False)


def plot_emission_spectrum(
    lines: Sequence[SpectralLine],
    ax: Optional[Axes] = None,
    title: str = "Emission spectrum",
) -> "plt.Figure":
    """Render spectral lines as glowing bars positioned at true eigenvalue gaps.

    Glow is faked with layered, widened, low-alpha strokes underneath a
    sharp core line -- matplotlib has no native bloom/blur filter.
    """
    owns_fig = ax is None
    if owns_fig:
        fig, ax = plt.subplots(figsize=(9, 3.2), dpi=140)
    else:
        fig = ax.figure

    _style_axes(ax)

    if not lines:
        ax.text(0.5, 0.5, "no transitions", color=_INK_LOW, ha="center", va="center")
        return fig

    max_freq = max(ln.freq for ln in lines) or 1e-6
    ax.axhline(0, color=_HAIR, linewidth=1, zorder=1)

    glow_widths = [7, 4.5, 2.5]
    glow_alphas = [0.10, 0.16, 0.22]

    for ln in lines:
        color = EIGENLIGHT_CMAP(ln.freq / max_freq)
        height = 0.08 + ln.normalized * 0.92
        for w, a in zip(glow_widths, glow_alphas):
            ax.plot([ln.freq, ln.freq], [0, height], color=color,
                     linewidth=w, alpha=a, solid_capstyle="round", zorder=2)
        ax.plot([ln.freq, ln.freq], [0, height], color=color,
                 linewidth=1.8, alpha=0.95, solid_capstyle="round", zorder=3)

    ax.set_xlim(-max_freq * 0.05, max_freq * 1.15)
    ax.set_ylim(0, 1.08)
    ax.set_yticks([])
    ax.set_xlabel("ω  (energy units, ħ = 1)")
    ax.set_title(title, fontsize=11, loc="left", color=_INK_HI, pad=10)

    if owns_fig:
        fig.tight_layout()
    return fig


def plot_ctqw_populations(
    times: np.ndarray,
    populations: np.ndarray,
    ax: Optional[Axes] = None,
    title: str = "Vertex occupation |ψᵢ(t)|²",
) -> "plt.Figure":
    """Render site-population dynamics as line traces over time."""
    owns_fig = ax is None
    if owns_fig:
        fig, ax = plt.subplots(figsize=(9, 3.0), dpi=140)
    else:
        fig = ax.figure

    _style_axes(ax)

    n_sites = populations.shape[1]
    for i in range(n_sites):
        color = _SITE_COLORS[i % len(_SITE_COLORS)]
        ax.plot(times, populations[:, i], color=color, linewidth=1.6,
                alpha=0.9, label=f"vertex {i}")

    ax.set_xlim(times[0], times[-1])
    ax.set_ylim(0, min(1.05, populations.max() * 1.15 + 1e-6))
    ax.set_xlabel("t")
    ax.set_ylabel("population")
    ax.set_title(title, fontsize=11, loc="left", color=_INK_HI, pad=10)

    if n_sites <= 8:
        legend = ax.legend(loc="upper right", fontsize=7.5, frameon=False,
                            ncol=min(n_sites, 4))
        for text in legend.get_texts():
            text.set_color(_INK_MID)

    if owns_fig:
        fig.tight_layout()
    return fig
