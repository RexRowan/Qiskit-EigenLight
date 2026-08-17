"""
Integration bridge for qiskit-stateviz.

This module is the *only* place in qiskit-eigenlight that is written with
another package's calling conventions in mind. Importing `qiskit_eigenlight`
itself never touches this file or requires qiskit-stateviz to be installed;
you only reach it by explicitly importing
`qiskit_eigenlight.integrations.stateviz`.

Intended wiring, on the qiskit-stateviz side:

    # inside qiskit_stateviz/plotting.py, alongside plot_spin_rotation_interactive
    from qiskit_eigenlight.integrations.stateviz import plot_evolution_spectrum

so that from a user's perspective it reads as a native stateviz function:

    from qiskit_stateviz import plot_spin_rotation_interactive, plot_evolution_spectrum

qiskit-stateviz should list qiskit-eigenlight as an optional dependency
(extras_require) rather than a hard one, and guard the import, since not
every stateviz user needs the emission-spectrum view.
"""

from __future__ import annotations

from typing import Iterable, Optional

import matplotlib.pyplot as plt
import numpy as np

from ..core import build_cayley_adjacency, girth, spectral_gap, spectral_lines, ctqw_populations
from ..render import plot_emission_spectrum, plot_ctqw_populations, _BG

__all__ = ["plot_evolution_spectrum"]


def plot_evolution_spectrum(
    n: int,
    generators: Iterable[int],
    start_vertex: int = 0,
    transition_operator: Optional[np.ndarray] = None,
    figsize: tuple = (9, 6.4),
):
    """Combined two-panel figure: emission spectrum over CTQW population dynamics.

    This is the function meant to be re-exported by qiskit-stateviz, sitting
    alongside `plot_spin_rotation_interactive`. Same shape of contract: takes
    plain parameters describing the system, returns a ready-to-display
    matplotlib Figure, and does its own internal diagonalization -- the
    caller doesn't need to know about `qiskit_eigenlight.core` at all.

    Parameters
    ----------
    n : group order for the cyclic group Z_n underlying the Cayley graph.
    generators : generating set S (iterable of ints in [1, n-1]).
    start_vertex : where the walk / initial state is localized.
    transition_operator : optional (n, n) array overriding the default
        uniform all-pairs probe used to compute the emission spectrum.
    figsize : matplotlib figsize for the combined figure.

    Returns
    -------
    matplotlib.figure.Figure with two stacked axes (spectrum, populations).
    Also carries `fig.eigenlight_meta` -- a dict with `girth` and
    `spectral_gap` for callers (e.g. stateviz) that want to display those
    numbers alongside the plot without recomputing them.
    """
    A = build_cayley_adjacency(n, generators)
    evals = np.linalg.eigh(A)[0]

    lines = spectral_lines(A, start_vertex, transition_operator=transition_operator)
    times, pops = ctqw_populations(A, start_vertex)

    fig, (ax_spec, ax_pop) = plt.subplots(2, 1, figsize=figsize, dpi=140)
    fig.patch.set_facecolor(_BG)

    plot_emission_spectrum(lines, ax=ax_spec,
                           title=f"Cay(Z{n}, {sorted(set(g % n for g in generators))}) -- emission spectrum")
    plot_ctqw_populations(times, pops, ax=ax_pop)

    fig.subplots_adjust(hspace=0.55)

    fig.eigenlight_meta = {
        "girth": girth(A),
        "spectral_gap": spectral_gap(evals),
        "n": n,
        "generators": sorted(set(g % n for g in generators)),
        "start_vertex": start_vertex,
    }
    return fig
