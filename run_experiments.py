"""
Sorting_Assignment — main code file (course requirement).

Implements: Insertion (3), Merge (4), Quick (5); timing experiments; CLI.
Outputs: result1.png (Part B, random arrays) or result2.png (Part C, nearly sorted + noise).

Dependencies: matplotlib (see requirements.txt).
"""

from __future__ import annotations

import argparse
import random
import statistics
import sys
import time
from pathlib import Path
from typing import Callable, Iterable, Sequence

import matplotlib.pyplot as plt

SortFn = Callable[[list], None]

QUADRATIC_ALGORITHM_IDS: frozenset[int] = frozenset({1, 2, 3})
MAX_N_QUADRATIC   = 50_000     # hard cap for quadratic algorithms (Insertion, Bubble, Selection)
HARD_LIMIT_SYSTEM = 1_000_000  # hard cap for all algorithms

# ---------------------------------------------------------------------------
# Part A: sorting algorithms (in-place)
# ---------------------------------------------------------------------------

def insertion_sort(arr: list) -> None:
    for i in range(1, len(arr)):
        key = arr[i]
        j = i - 1
        while j >= 0 and arr[j] > key:
            arr[j + 1] = arr[j]
            j -= 1
        arr[j + 1] = key


def merge_sort(arr: list) -> None:
    if len(arr) <= 1:
        return
    aux = arr.copy()
    _merge_sort_range(arr, aux, 0, len(arr))


def _merge_sort_range(arr: list, aux: list, lo: int, hi: int) -> None:
    if hi - lo <= 1:
        return
    mid = (lo + hi) // 2
    _merge_sort_range(arr, aux, lo, mid)
    _merge_sort_range(arr, aux, mid, hi)
    _merge(arr, aux, lo, mid, hi)


def _merge(arr: list, aux: list, lo: int, mid: int, hi: int) -> None:
    i, j, k = lo, mid, lo
    while i < mid and j < hi:
        if arr[i] <= arr[j]:
            aux[k] = arr[i]; i += 1
        else:
            aux[k] = arr[j]; j += 1
        k += 1
    while i < mid:
        aux[k] = arr[i]; i += 1; k += 1
    while j < hi:
        aux[k] = arr[j]; j += 1; k += 1
    arr[lo:hi] = aux[lo:hi]


def quick_sort(arr: list) -> None:
    _quick_range(arr, 0, len(arr))


def _quick_range(arr: list, lo: int, hi: int) -> None:
    if hi - lo <= 1:
        return
    if hi - lo == 2:
        if arr[lo] > arr[lo + 1]:
            arr[lo], arr[lo + 1] = arr[lo + 1], arr[lo]
        return
    p = _partition(arr, lo, hi)
    _quick_range(arr, lo, p)
    _quick_range(arr, p + 1, hi)


def _partition(arr: list, lo: int, hi: int) -> int:
    pivot = arr[hi - 1]
    i = lo
    for j in range(lo, hi - 1):
        if arr[j] <= pivot:
            arr[i], arr[j] = arr[j], arr[i]
            i += 1
    arr[i], arr[hi - 1] = arr[hi - 1], arr[i]
    return i


ALGORITHMS: dict[int, tuple[str, SortFn]] = {
    3: ("Insertion Sort", insertion_sort),
    4: ("Merge Sort",     merge_sort),
    5: ("Quick Sort",     quick_sort),
}


def get_algorithm(algorithm_id: int) -> tuple[str, SortFn]:
    if algorithm_id not in ALGORITHMS:
        raise SystemExit(
            f"Unknown algorithm id {algorithm_id}. This project implements ids {sorted(ALGORITHMS)}."
        )
    return ALGORITHMS[algorithm_id]


def sizes_for_algorithm(algorithm_id: int, sizes: Sequence[int]) -> list[int]:
    """Return the sizes this algorithm will actually run.
    Quadratic algorithms are capped at MAX_N_QUADRATIC; all algorithms at HARD_LIMIT_SYSTEM.
    """
    limit = MAX_N_QUADRATIC if algorithm_id in QUADRATIC_ALGORITHM_IDS else HARD_LIMIT_SYSTEM
    return [n for n in sizes if n <= limit]


# ---------------------------------------------------------------------------
# Experiments
# ---------------------------------------------------------------------------

def random_array(size: int, rng: random.Random | None = None) -> list:
    rng = rng or random
    return [rng.randint(-(2**31), 2**31 - 1) for _ in range(size)]


def nearly_sorted_with_noise(size: int, noise_fraction: float, rng: random.Random) -> list:
    arr = list(range(size))
    swaps = max(1, int(size * noise_fraction)) if size > 0 else 0
    for _ in range(swaps):
        i, j = rng.randrange(size), rng.randrange(size)
        arr[i], arr[j] = arr[j], arr[i]
    return arr


def time_sort(sort_fn: SortFn, arr: list) -> float:
    work = arr.copy()
    t0 = time.perf_counter()
    sort_fn(work)
    return time.perf_counter() - t0


def run_trial(sort_fn: SortFn, size: int, experiment_code: int, rng: random.Random) -> float:
    if experiment_code == 0:
        arr = random_array(size, rng)
    elif experiment_code in (1, 2):
        frac = 0.05 if experiment_code == 1 else 0.20
        arr = nearly_sorted_with_noise(size, frac, rng)
    else:
        raise ValueError(f"Unsupported experiment code: {experiment_code}")
    return time_sort(sort_fn, arr)


def run_batch(
    sort_fn: SortFn,
    sizes: Iterable[int],
    experiment_code: int,
    repetitions: int,
    seed: int | None = None,
) -> dict[int, tuple[float, float]]:
    rng = random.Random(seed)
    result: dict[int, tuple[float, float]] = {}
    for size in sizes:
        times = [run_trial(sort_fn, size, experiment_code, rng) for _ in range(repetitions)]
        result[size] = (statistics.mean(times), statistics.pstdev(times) if len(times) > 1 else 0.0)
    return result


# ---------------------------------------------------------------------------
# Plots
# ---------------------------------------------------------------------------

def plot_comparison(
    series: dict[str, dict[int, tuple[float, float]]],
    title: str,
    outfile: str | Path,
    ylabel: str = "Time (seconds)",
) -> None:
    outfile = Path(outfile)
    fig, ax = plt.subplots(figsize=(10, 6))
    colors = [p["color"] for p in plt.rcParams["axes.prop_cycle"]]

    for idx, (label, by_size) in enumerate(series.items()):
        color = colors[idx % len(colors)]
        sizes = sorted(by_size)
        means = [by_size[s][0] for s in sizes]
        stds  = [by_size[s][1] for s in sizes]
        lo = [max(m - sd, 0) for m, sd in zip(means, stds)]
        hi = [m + sd          for m, sd in zip(means, stds)]
        ax.plot(sizes, means, marker="o", color=color, linestyle="-", label=label)
        ax.fill_between(sizes, lo, hi, color=color, alpha=0.15)

    ax.set_xlabel("Array size (n)"); ax.set_ylabel(ylabel); ax.set_title(title)
    ax.legend(); ax.grid(True, linestyle=":", alpha=0.6)
    fig.tight_layout(); fig.savefig(outfile, dpi=150); plt.close(fig)


def plot_part_c_two_noises(
    data: dict[str, tuple[dict[int, tuple[float, float]], dict[int, tuple[float, float]]]],
    title: str,
    outfile: str | Path,
) -> None:
    outfile = Path(outfile)
    fig, ax = plt.subplots(figsize=(10, 6))
    colors = [p["color"] for p in plt.rcParams["axes.prop_cycle"]]

    for idx, (label, (s5, s20)) in enumerate(data.items()):
        color = colors[idx % len(colors)]
        for suffix, stats, style in (
            (" (5% noise)",  s5,  "-"),
            (" (20% noise)", s20, "--"),
        ):
            sizes = sorted(stats)
            means = [stats[s][0] for s in sizes]
            stds  = [stats[s][1] for s in sizes]
            lo = [max(m - sd, 0) for m, sd in zip(means, stds)]
            hi = [m + sd          for m, sd in zip(means, stds)]
            ax.plot(sizes, means, marker="o", color=color, linestyle=style, label=label + suffix)
            ax.fill_between(sizes, lo, hi, color=color, alpha=0.12)

    ax.set_xlabel("Array size (n)"); ax.set_ylabel("Time (seconds)"); ax.set_title(title)
    ax.legend(); ax.grid(True, linestyle=":", alpha=0.6)
    fig.tight_layout(); fig.savefig(outfile, dpi=150); plt.close(fig)


# ---------------------------------------------------------------------------
# CLI
# ---------------------------------------------------------------------------

def build_parser() -> argparse.ArgumentParser:
    p = argparse.ArgumentParser(
        description="Compare sorting algorithms — Data Structures Python Assignment 1.",
        formatter_class=argparse.ArgumentDefaultsHelpFormatter,
    )
    p.add_argument("-a", nargs="+", type=int, metavar="ID", default=[3, 4, 5],
        help="Algorithm IDs: 1 Bubble, 2 Selection, 3 Insertion, 4 Merge, 5 Quick.")
    p.add_argument("-s", nargs="+", type=int, metavar="N",
        default=[100, 500, 1_000, 5_000, 10_000],
        help=f"Array sizes (max {HARD_LIMIT_SYSTEM:,}; quadratic algorithms capped at {MAX_N_QUADRATIC:,}).")
    p.add_argument("-e", nargs="+", type=int, metavar="E", default=[0],
        help="0=random (result1.png). 1=nearly-sorted+5%% noise. 2=nearly-sorted+20%% noise. "
             "Use 1 2 together for Part C (result2.png).")
    p.add_argument("-r", type=int, default=20, help="Repetitions per size.")
    p.add_argument("--seed", type=int, default=None, help="Random seed for reproducibility.")
    p.add_argument("--out", default=None, help="Output PNG path.")
    return p


def main(argv: list[str] | None = None) -> None:
    args = build_parser().parse_args(argv)
    algo_ids = args.a
    sizes    = [n for n in args.s if n <= HARD_LIMIT_SYSTEM]
    modes    = args.e
    out      = args.out

    if not sizes:
        raise SystemExit(f"All requested sizes exceed the system limit of {HARD_LIMIT_SYSTEM:,}.")
    if 0 in modes and len(set(modes)) > 1:
        raise SystemExit("Use only -e 0 for random arrays, or 1 / 2 / `1 2` for nearly-sorted.")

    if modes == [0]:
        series: dict[str, dict[int, tuple[float, float]]] = {}
        for aid in algo_ids:
            name, sort_fn = get_algorithm(aid)
            algo_sizes = sizes_for_algorithm(aid, sizes)
            if algo_sizes:
                series[name] = run_batch(sort_fn, algo_sizes, 0, args.r, args.seed)
        outfile = out or "result1.png"
        plot_comparison(series, "Random arrays — mean time ± stdev", outfile)
        print(f"Wrote {outfile}")
        return

    if set(modes) <= {1, 2}:
        if set(modes) == {1, 2}:
            data: dict[str, tuple[dict[int, tuple[float, float]], dict[int, tuple[float, float]]]] = {}
            for aid in algo_ids:
                name, sort_fn = get_algorithm(aid)
                algo_sizes = sizes_for_algorithm(aid, sizes)
                if algo_sizes:
                    data[name] = (
                        run_batch(sort_fn, algo_sizes, 1, args.r, args.seed),
                        run_batch(sort_fn, algo_sizes, 2, args.r, args.seed),
                    )
            outfile = out or "result2.png"
            plot_part_c_two_noises(data, "Nearly sorted arrays — 5% vs 20% random swaps", outfile)
            print(f"Wrote {outfile}")
            return

        ec = modes[0]
        series_single: dict[str, dict[int, tuple[float, float]]] = {}
        for aid in algo_ids:
            name, sort_fn = get_algorithm(aid)
            algo_sizes = sizes_for_algorithm(aid, sizes)
            if algo_sizes:
                series_single[name] = run_batch(sort_fn, algo_sizes, ec, args.r, args.seed)
        outfile = out or f"result_noise_{ec}.png"
        plot_comparison(series_single, f"Nearly sorted — {'5%' if ec == 1 else '20%'} noise", outfile)
        print(f"Wrote {outfile}")
        return

    raise SystemExit(f"Unsupported -e values: {modes}")


if __name__ == "__main__":
    main()
