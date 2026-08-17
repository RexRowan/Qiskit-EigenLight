# EigenLight

**Turn a quantum system's eigenvalues into light instead of sound.**

There's a well-worn idea in the ecosystem of sonifying quantum state evolution — mapping amplitudes and phases to pitch, timbre, rhythm. `qiskit-eigenlight` takes the same underlying object (a Hamiltonian's eigenspectrum, probed by a continuous-time evolution) and asks what it looks like instead of what it sounds like: rendered as an **emission spectrum**, with spectral lines positioned at true eigenvalue gaps and colored/intensity-scaled from the actual coherence structure of the evolving state.

It is not a music-to-image converter. There is no audio anywhere in this package. The physics is the same substrate a sonification would use — this is just the other rendering of it.

## What it actually computes

Given a Hamiltonian `H` (real symmetric, e.g. the adjacency matrix of a graph) and an initial state:

1. Diagonalize `H = V Λ V^T` (via `numpy.linalg.eigh`).
2. Evolve under the free Hamiltonian: `|ψ(t)⟩ = V exp(-iΛt) V^T |ψ(0)⟩`.
3. Decompose `⟨T(t)⟩` for a probe operator `T` into its Fourier components — each component sits at a frequency `ω_kl = |λ_k − λ_l|`, with amplitude `|c_k c_l ⟨k|T|l⟩|`.
4. Render those components as spectral lines: position = true energy gap, height/color = true coherence amplitude.

This is the actual linear-response decomposition of an observable's dynamics — not a stylized approximation of one. The one deliberate simplification: `T` defaults to a uniform all-pairs coupling (every eigenstate pair is treated as equally "dipole-allowed") rather than something derived from the physical transition operator of a real atom. That's a real limitation if you're trying to reproduce an actual physical spectrum, and it's stated here rather than buried — pass your own `T` if you have one that means something.

The package also supports **continuous-time quantum walks (CTQW)** directly: build `H` as the adjacency matrix of `Cay(G, S)` for a finite group `G` and generating set `S`, and the same machinery gives you the walk's mixing/return-probability dynamics on one panel and its emission spectrum on the other. Girth and spectral gap are computed exactly (BFS-based cycle detection, not estimated).

## Install

```bash
pip install qiskit-eigenlight
```

or from source:

```bash
git clone https://github.com/RexRowan/qiskit-eigenlight
cd qiskit-eigenlight
pip install -e .
```

## Quick start

```python
from qiskit_eigenlight import build_cayley_adjacency, spectral_lines, ctqw_populations
from qiskit_eigenlight import plot_emission_spectrum, plot_ctqw_populations

# Cay(Z_12, {1, 5}) -- a circulant graph
A = build_cayley_adjacency(n=12, generators={1, 5})

lines = spectral_lines(A, start_vertex=0)
fig = plot_emission_spectrum(lines)
fig.savefig("emission_spectrum.png", dpi=150)

times, pops = ctqw_populations(A, start_vertex=0)
fig2 = plot_ctqw_populations(times, pops)
```

## Current scope

- **Adjacency construction:** cyclic groups `Z_n` only, via `build_cayley_adjacency`. Products of cyclic groups (`Z_n1 x Z_n2 x ...`) are not yet supported — that's the natural next step for tying this to non-`F_2^n` abelian group work, and is tracked as an open item rather than silently assumed to work.
- **No dissipation.** Everything here is unitary evolution; spectral lines are infinitely sharp. If you want linewidth broadening from a real decoherence model, that's a layer to add on top, not something this package currently does.
- **Girth is graph girth**, not the "non-backtracking zero-sumfree" variant under investigation elsewhere — it's a useful number to watch change as you vary `S`, but the package doesn't (yet) compute anything about non-backtracking walks specifically. Don't over-read the girth readout as answering a distance-bound question it isn't wired to answer.

## Relationship to other packages in this portfolio

This package is intentionally standalone for now — no dependency on `qiskit-stateviz`, `qiskit-graph-walks`, or anything else. An integration layer that lets `qiskit-stateviz` call into this package's rendering directly lives in `qiskit_eigenlight.integrations.stateviz`, documented separately, and is opt-in: importing `qiskit_eigenlight` on its own pulls in only `numpy` and `matplotlib`.

If you're looking for the CTQW mixing-signature analysis this shares math with, see `qiskit-graph-walks`. If you're looking for the SU(2)/spinor visual work this shares an aesthetic lineage with, see `Spinor-Topology`.

## License

Apache 2.0.
