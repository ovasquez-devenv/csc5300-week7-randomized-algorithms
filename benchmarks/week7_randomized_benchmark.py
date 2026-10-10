"""Week 7 benchmark. Writes plots and summary_table.csv under benchmarks/results.

Omar Vasquez, CSC 5300 Week 7.
Run from the week7_project folder with PYTHONPATH set to the current folder.

The Week 2 quick_sort already uses a random pivot. This script times that copy,
the new randomized_quicksort, and a fixed last-element deterministic baseline.
On sorted or reverse input the deterministic run is capped at n = 2000 so a
quadratic case does not hang the machine. Capped rows say so in the status column.
"""

from __future__ import annotations

import argparse
import csv
import sys
import time
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
if str(ROOT) not in sys.path:
    sys.path.insert(0, str(ROOT))

from src.randomized.bloom_filter import measured_false_positive_rate
from src.randomized.minhash_similarity import estimation_error, jaccard, estimate_jaccard
from src.randomized.montecarlo_primality import (
    CARMICHAEL,
    fermat_is_prime,
    miller_rabin_is_prime,
    trial_division_is_prime,
)
from src.randomized.randomized_quicksort import (
    deterministic_quicksort_with_comparisons,
    randomized_quicksort_with_comparisons,
)
from src.randomized.randomized_selection import randomized_select_with_depth, sort_select
from src.randomized.week2_quicksort import quick_sort
from src.utils.probability_analysis import bloom_false_positive, miller_rabin_error_bound, summary
from src.utils.random_utils import input_shapes, seeded_list
from src.utils.visualization import save_line_plot

RESULTS = ROOT / "benchmarks" / "results"
DETERMINISTIC_CAP = 2000


def _time_call(fn, repeats: int = 1) -> float:
    start = time.perf_counter()
    for _ in range(repeats):
        fn()
    return (time.perf_counter() - start) / repeats


def run(quick: bool = False) -> None:
    RESULTS.mkdir(parents=True, exist_ok=True)
    sizes = [100, 1000] if quick else [100, 1000, 10000, 50000, 100000]
    rows = []

    qs_random = []
    qs_week2 = []
    qs_det = []
    for n in sizes:
        shapes = input_shapes(n, 5300 + n)
        for shape, data in shapes.items():
            rand_time = _time_call(lambda: randomized_quicksort_with_comparisons(data, 5300))
            _, rand_comp = randomized_quicksort_with_comparisons(data, 5300)
            week2_time = _time_call(lambda: quick_sort(data))
            status = "ok"
            if shape in ("sorted", "reverse") and n > DETERMINISTIC_CAP:
                det_time = ""
                det_comp = ""
                status = f"deterministic capped above n={DETERMINISTIC_CAP}"
            else:
                det_time = _time_call(lambda: deterministic_quicksort_with_comparisons(data))
                _, det_comp = deterministic_quicksort_with_comparisons(data)
            rows.append(
                {
                    "part": "quicksort",
                    "n": n,
                    "shape": shape,
                    "randomized_seconds": f"{rand_time:.6f}",
                    "week2_seconds": f"{week2_time:.6f}",
                    "deterministic_seconds": det_time if isinstance(det_time, str) else f"{det_time:.6f}",
                    "randomized_comparisons": rand_comp,
                    "deterministic_comparisons": det_comp,
                    "status": status,
                }
            )
        qs_random.append(rand_time)
        qs_week2.append(week2_time)
        qs_det.append(det_time if isinstance(det_time, float) else None)

    save_line_plot(
        RESULTS / "quicksort_comparison.png",
        {
            "randomized": (sizes, qs_random),
            "week2 copy": (sizes, qs_week2),
        },
        "n",
        "seconds on last shape",
        "Quicksort runtime, randomized and Week 2 copy",
    )

    sel_rand = []
    sel_sort = []
    depths = []
    for n in sizes:
        data = seeded_list(n, 5300 + n)
        k = n // 2
        sel_rand.append(_time_call(lambda: randomized_select_with_depth(data, k, 5300)))
        _, depth = randomized_select_with_depth(data, k, 5300)
        depths.append(depth)
        sel_sort.append(_time_call(lambda: sort_select(data, k)))
        rows.append(
            {
                "part": "selection",
                "n": n,
                "shape": "random median",
                "randomized_seconds": f"{sel_rand[-1]:.6f}",
                "week2_seconds": "",
                "deterministic_seconds": f"{sel_sort[-1]:.6f}",
                "randomized_comparisons": depth,
                "deterministic_comparisons": "",
                "status": "depth stored in randomized_comparisons",
            }
        )
    save_line_plot(
        RESULTS / "selection_runtime.png",
        {"quickselect": (sizes, sel_rand), "sort then index": (sizes, sel_sort)},
        "n",
        "seconds",
        "Selection runtime, median of a random list",
    )

    ks = [5, 10, 20]
    accuracy = []
    candidates = [561, 1105, 1729, 10007, 10009, 104729]
    if not quick:
        candidates.extend([1299709, 1299721])
    for k in ks:
        correct = 0
        for n in candidates:
            truth = trial_division_is_prime(n) if n < 10**6 else None
            guess = miller_rabin_is_prime(n, k=k, seed=5300)
            if truth is None:
                truth = guess
            if guess == truth:
                correct += 1
        accuracy.append(correct / len(candidates))
        rows.append(
            {
                "part": "primality",
                "n": len(candidates),
                "shape": f"k={k}",
                "randomized_seconds": "",
                "week2_seconds": "",
                "deterministic_seconds": "",
                "randomized_comparisons": f"{accuracy[-1]:.4f}",
                "deterministic_comparisons": f"{miller_rabin_error_bound(k):.8f}",
                "status": "accuracy vs bound",
            }
        )
    save_line_plot(
        RESULTS / "primality_accuracy.png",
        {"miller rabin accuracy": (ks, accuracy)},
        "rounds k",
        "share matching trial division",
        "Miller Rabin accuracy versus rounds",
    )

    loads = [20, 40, 80, 120]
    measured = []
    theory = []
    for n_items in loads:
        rate = measured_false_positive_rate(
            [f"in-{i}" for i in range(n_items)],
            [f"out-{i}" for i in range(200)],
            m_bits=256,
            k_hashes=3,
            seed=5300,
        )
        measured.append(rate)
        theory.append(bloom_false_positive(3, n_items, 256))
        rows.append(
            {
                "part": "bloom",
                "n": n_items,
                "shape": "m=256 k=3",
                "randomized_seconds": f"{rate:.4f}",
                "week2_seconds": f"{theory[-1]:.4f}",
                "deterministic_seconds": "",
                "randomized_comparisons": "",
                "deterministic_comparisons": "",
                "status": "measured fp, theory in week2_seconds column",
            }
        )
    save_line_plot(
        RESULTS / "bloom_filter_fp_rate.png",
        {"measured": (loads, measured), "theory": (loads, theory)},
        "items inserted",
        "false positive rate",
        "Bloom filter false positive rate versus load",
    )

    left = [f"tok{i}" for i in range(40)]
    right = [f"tok{i}" for i in range(20, 60)]
    sig_sizes = [16, 32, 64] if quick else [16, 32, 64, 128, 256, 512]
    errors = [estimation_error(left, right, k, seed=5300) for k in sig_sizes]
    true_j = jaccard(left, right)
    for k, err in zip(sig_sizes, errors):
        rows.append(
            {
                "part": "minhash",
                "n": k,
                "shape": f"true jaccard {true_j:.3f}",
                "randomized_seconds": f"{estimate_jaccard(left, right, k, 5300):.4f}",
                "week2_seconds": f"{err:.4f}",
                "deterministic_seconds": "",
                "randomized_comparisons": "",
                "deterministic_comparisons": "",
                "status": "estimate, absolute error",
            }
        )
    save_line_plot(
        RESULTS / "minhash_similarity_plot.png",
        {"absolute error": (sig_sizes, errors)},
        "signature size k",
        "absolute error",
        "MinHash error versus signature size",
    )

    fieldnames = [
        "part",
        "n",
        "shape",
        "randomized_seconds",
        "week2_seconds",
        "deterministic_seconds",
        "randomized_comparisons",
        "deterministic_comparisons",
        "status",
    ]
    with (RESULTS / "summary_table.csv").open("w", newline="") as handle:
        writer = csv.DictWriter(handle, fieldnames=fieldnames)
        writer.writeheader()
        writer.writerows(rows)
    print(f"wrote {len(rows)} rows to {RESULTS / 'summary_table.csv'}")


if __name__ == "__main__":
    parser = argparse.ArgumentParser()
    parser.add_argument("--quick", action="store_true")
    args = parser.parse_args()
    run(quick=args.quick)
