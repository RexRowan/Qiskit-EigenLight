import numpy as np
import pytest

from qiskit_eigenlight import (
    build_cayley_adjacency,
    is_connected_cyclic,
    girth,
    spectral_gap,
    spectral_lines,
    ctqw_populations,
)


def test_adjacency_symmetric_and_zero_diagonal():
    A = build_cayley_adjacency(8, {1, 2})
    assert np.allclose(A, A.T)
    assert np.all(np.diag(A) == 0)


def test_adjacency_degree():
    # generator set without a self-paired element (n/2) gives degree 2*|S|
    A = build_cayley_adjacency(8, {1, 3})
    assert np.all(A.sum(axis=1) == 4)


def test_self_paired_generator_reduces_degree():
    # n=8, s=4 is self-paired (4 == 8-4), contributes only 1 to degree
    A = build_cayley_adjacency(8, {4})
    assert np.all(A.sum(axis=1) == 1)


def test_generators_normalized_mod_n():
    A1 = build_cayley_adjacency(8, {1})
    A2 = build_cayley_adjacency(8, {9})  # 9 mod 8 == 1
    assert np.allclose(A1, A2)


def test_rejects_empty_generating_set():
    with pytest.raises(ValueError):
        build_cayley_adjacency(8, {0})


def test_is_connected_cyclic():
    assert is_connected_cyclic(8, {1})
    assert is_connected_cyclic(8, {1, 2})
    assert not is_connected_cyclic(8, {2, 4})  # gcd(8,2,4) = 2, disconnected


def test_girth_of_cycle_graph():
    # Cay(Z_n, {1}) is exactly the n-cycle, girth = n
    for n in (5, 6, 9):
        A = build_cayley_adjacency(n, {1})
        assert girth(A) == n


def test_girth_of_complete_graph():
    # Cay(Z_n, {1..n//2}) is the complete graph K_n, girth = 3 for n >= 3
    n = 7
    A = build_cayley_adjacency(n, set(range(1, n // 2 + 1)))
    assert girth(A) == 3


def test_spectral_gap_matches_sorted_eigs():
    A = build_cayley_adjacency(10, {1, 3})
    evals = np.linalg.eigh(A)[0]
    gap = spectral_gap(evals)
    vals = np.sort(evals)
    assert np.isclose(gap, vals[-1] - vals[-2])


def test_spectral_lines_count_and_normalization():
    A = build_cayley_adjacency(6, {1, 2})
    lines = spectral_lines(A, start_vertex=0)
    n = A.shape[0]
    assert len(lines) == n * (n - 1) // 2
    assert max(ln.normalized for ln in lines) == pytest.approx(1.0)
    assert all(ln.normalized >= 0 for ln in lines)


def test_ctqw_populations_conserve_probability():
    A = build_cayley_adjacency(8, {1, 2})
    times, pops = ctqw_populations(A, start_vertex=0, num_steps=100)
    totals = pops.sum(axis=1)
    assert np.allclose(totals, 1.0, atol=1e-8)


def test_ctqw_starts_localized():
    A = build_cayley_adjacency(8, {1, 2})
    times, pops = ctqw_populations(A, start_vertex=3, num_steps=50)
    assert pops[0, 3] == pytest.approx(1.0)
    assert np.allclose(np.delete(pops[0], 3), 0.0, atol=1e-10)
