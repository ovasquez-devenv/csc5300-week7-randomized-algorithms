"""Week 7 benchmark with repeated seeded runs. Writes CSV files and plots under benchmarks/results.

Omar Vasquez, CSC 5300 Week 7.
Run from the week7_project folder with PYTHONPATH set to the current folder.

How the trials work:
Every configuration runs R trials (default 5, change it with --trials). Trial t
uses seed 5300 + t, and the seeds are written into each CSV. The input list for
each n is built once from a fixed seed (5300 + n), so every trial sorts or
searches the same data. Only the algorithm's own random choices change from one
trial to the next. That means the standard deviation shows the spread caused by
the randomness (plus normal timing noise), not by different inputs.

The Week 2 quick_sort uses the global random module, so it gets
random.seed(trial seed) right before each trial.

The fixed last-element deterministic baseline runs the same trials. Its
comparison count never changes, so its time spread is only timing noise. On
sorted or reverse input it is capped at n = 2000 so a quadratic case does not
hang the machine.

The duplicates shape only has the values 0 to 6. Lomuto partition sends every
key equal to the pivot to one side, so this shape is quadratic for every pivot
rule. Above n = 10000 it runs once, randomized sort only, and the status column
says so. The Week 2 copy and the deterministic baseline skip those rows.

Mean and sample standard deviation are reported for each configuration.
summary_table.csv also lists the sample variance.
"""

from __future__ import annotations

import argparse
import csv
import math
import random
import sys
import time
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
if str(ROOT) not in sys.path:
    sys.path.insert(0, str(ROOT))

from src.randomized.bloom_filter import BloomFilter, measured_false_positive_rate
from src.randomized.minhash_similarity import estimate_jaccard, jaccard
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
from src.utils.probability_analysis import (
    bloom_false_positive,
    mean,
    miller_rabin_error_bound,
    std_dev,
    variance,
)
from src.utils.random_utils import BASE_SEED, input_shapes, seeded_list, trial_seeds
from src.utils.visualization import save_errorbar_plot, save_panel_plot

RESULTS = ROOT / "benchmarks" / "results"
DETERMINISTIC_CAP = 2000
DUPLICATES_CAP = 10000
SORT_ALGORITHMS = ("randomized", "week2", "deterministic")
SORT_LABELS = {"randomized": "randomized", "week2": "week2 copy", "deterministic": "deterministic"}

# More Carmichael numbers past the six in montecarlo_primality.py. The bigger
# ones have large prime factors, so a random base rarely shares a factor with
# them and the Fermat test is fooled more often.
EXTRA_CARMICHAEL = (
    8911, 10585, 15841, 29341, 41041, 46657, 52633, 62745, 63973, 75361,
    101101, 115921, 126217, 162401, 172081, 188461, 252601, 278545, 294409,
    314821, 334153, 340561, 399001, 410041, 449065, 488881, 512461,
    1024651, 1152271,
)
PRIMES = (7919, 10007, 10009, 104729, 1000003, 1299709, 1299721)
PLAIN_COMPOSITES = (10403, 999999, 1000001, 1234567, 1299711, 1299713)
LARGE_TIMING_REPEATS = 50


def _fmt(value, digits: int = 6) -> str:
    if value is None or value == "":
        return ""
    return f"{value:.{digits}f}"


def _sci(value) -> str:
    if value is None or value == "":
        return ""
    return f"{value:.3e}"


def _seed_text(seeds) -> str:
    return " ".join(str(seed) for seed in seeds)


def _add_summary(summary_rows, part, config, metric, values, status="ok") -> None:
    """One long format row: mean, sample std dev, and sample variance of a metric."""
    if not values:
        summary_rows.append(
            {"part": part, "config": config, "metric": metric, "trials": 0,
             "mean": "", "std": "", "variance": "", "status": status}
        )
        return
    # A single run has no spread, so std and variance stay blank instead of 0.
    spread = len(values) > 1
    summary_rows.append(
        {
            "part": part,
            "config": config,
            "metric": metric,
            "trials": len(values),
            "mean": f"{mean(values):.6g}",
            "std": f"{std_dev(values):.6g}" if spread else "",
            "variance": f"{variance(values):.6g}" if spread else "",
            "status": status,
        }
    )


def _write_csv(path: Path, rows: list) -> int:
    with path.open("w", newline="", encoding="utf-8") as handle:
        writer = csv.DictWriter(handle, fieldnames=list(rows[0].keys()))
        writer.writeheader()
        writer.writerows(rows)
    return len(rows)


def quicksort_trial(algorithm: str, data: list, seed: int) -> tuple:
    """Run one sort with one seed. Returns (sorted list, seconds, comparisons or None)."""
    if algorithm == "week2":
        random.seed(seed)
        start = time.perf_counter()
        result = quick_sort(data)
        return result, time.perf_counter() - start, None
    start = time.perf_counter()
    if algorithm == "randomized":
        result, comparisons = randomized_quicksort_with_comparisons(data, seed)
    else:
        result, comparisons = deterministic_quicksort_with_comparisons(data)
    return result, time.perf_counter() - start, comparisons


def _quicksort_plan(algorithm: str, shape: str, n: int, trials: int) -> tuple:
    """How many trials this row gets, and its status text."""
    if algorithm == "deterministic" and shape in ("sorted", "reverse") and n > DETERMINISTIC_CAP:
        return 0, f"deterministic capped above n={DETERMINISTIC_CAP} (quadratic)"
    if shape == "duplicates" and n > DUPLICATES_CAP:
        if algorithm == "randomized":
            return 1, f"duplicates single run above n={DUPLICATES_CAP} (quadratic)"
        return 0, f"duplicates skipped above n={DUPLICATES_CAP} (quadratic), see randomized row"
    return trials, "ok"


def run_quicksort(sizes, seeds, summary_rows) -> list:
    rows = []
    points = {}
    for n in sizes:
        print(f"  quicksort n={n}", flush=True)
        shapes = input_shapes(n, BASE_SEED + n)
        for shape, data in shapes.items():
            expected = sorted(data)
            for algorithm in SORT_ALGORITHMS:
                count, status = _quicksort_plan(algorithm, shape, n, len(seeds))
                if count == 1 and len(seeds) > 1:
                    print(f"    {shape} {algorithm}: one run, this one is slow", flush=True)
                used = seeds[:count]
                times = []
                comps = []
                for seed in used:
                    result, seconds, comparisons = quicksort_trial(algorithm, data, seed)
                    if result != expected:
                        raise RuntimeError(f"{algorithm} did not sort n={n} {shape}")
                    times.append(seconds)
                    if comparisons is not None:
                        comps.append(comparisons)
                rows.append(
                    {
                        "part": "quicksort",
                        "n": n,
                        "shape": shape,
                        "algorithm": algorithm,
                        "trials": len(used),
                        "seeds": _seed_text(used) if algorithm != "deterministic" else "none (fixed pivot)",
                        "mean_seconds": _fmt(mean(times)) if times else "",
                        "std_seconds": _fmt(std_dev(times)) if len(times) > 1 else "",
                        "mean_comparisons": _fmt(mean(comps), 1) if comps else "",
                        "std_comparisons": _fmt(std_dev(comps), 1) if len(comps) > 1 else "",
                        "status": status,
                    }
                )
                config = f"n={n} {shape} {algorithm}"
                _add_summary(summary_rows, "quicksort", config, "seconds", times, status)
                if algorithm != "week2":
                    _add_summary(summary_rows, "quicksort", config, "comparisons", comps, status)
                if times:
                    xs, ys, errs = points.setdefault((shape, algorithm), ([], [], []))
                    xs.append(n)
                    ys.append(mean(times))
                    errs.append(std_dev(times))

    panels = {}
    for shape in ("random", "sorted", "reverse", "duplicates"):
        panels[f"{shape} input"] = {
            SORT_LABELS[algorithm]: points.get((shape, algorithm), ([], [], []))
            for algorithm in SORT_ALGORITHMS
        }
    save_panel_plot(
        RESULTS / "quicksort_comparison.png",
        panels,
        "n",
        "mean seconds",
        f"Quicksort mean runtime by input shape, {len(seeds)} seeded trials, bars are 1 std dev",
        logx=True,
        logy=True,
    )
    return rows


def run_selection(sizes, seeds, summary_rows) -> list:
    rows = []
    panels = {}
    for n in sizes:
        data = seeded_list(n, BASE_SEED + n)
        ordered = sorted(data)
        for position, k in (("min", 0), ("median", n // 2), ("max", n - 1)):
            quick_times = []
            depths = []
            for seed in seeds:
                start = time.perf_counter()
                value, depth = randomized_select_with_depth(data, k, seed)
                quick_times.append(time.perf_counter() - start)
                depths.append(depth)
                if value != ordered[k]:
                    raise RuntimeError(f"quickselect wrong at n={n} k={k}")
            sort_times = []
            for _ in seeds:
                start = time.perf_counter()
                sort_select(data, k)
                sort_times.append(time.perf_counter() - start)
            for method, times, depth_values, seed_text in (
                ("quickselect", quick_times, depths, _seed_text(seeds)),
                ("sort then index", sort_times, [], "none (no randomness)"),
            ):
                rows.append(
                    {
                        "part": "selection",
                        "n": n,
                        "position": position,
                        "k": k,
                        "method": method,
                        "trials": len(times),
                        "seeds": seed_text,
                        "mean_seconds": _fmt(mean(times)),
                        "std_seconds": _fmt(std_dev(times)),
                        "mean_depth": _fmt(mean(depth_values), 2) if depth_values else "",
                        "std_depth": _fmt(std_dev(depth_values), 2) if depth_values else "",
                        "status": "ok",
                    }
                )
                config = f"n={n} {position} {method}"
                _add_summary(summary_rows, "selection", config, "seconds", times)
                if depth_values:
                    _add_summary(summary_rows, "selection", config, "recursion depth", depth_values)
                series = panels.setdefault(f"k = {position}", {})
                xs, ys, errs = series.setdefault(method, ([], [], []))
                xs.append(n)
                ys.append(mean(times))
                errs.append(std_dev(times))
    save_panel_plot(
        RESULTS / "selection_runtime.png",
        panels,
        "n",
        "mean seconds",
        f"Selection mean runtime, {len(seeds)} seeded trials, bars are 1 std dev",
        logx=True,
        logy=True,
    )
    return rows


def run_primality(seeds, summary_rows) -> list:
    carmichael = sorted(set(CARMICHAEL) | set(EXTRA_CARMICHAEL))
    candidates = sorted(set(carmichael) | set(PRIMES) | set(PLAIN_COMPOSITES))
    # Trial division is the ground truth for every candidate. sqrt(1.3 million)
    # is about 1140, so this is cheap even for the biggest numbers.
    truth = {n: trial_division_is_prime(n) for n in candidates}
    large = [n for n in candidates if n > 10**6]

    def time_large(check) -> float:
        start = time.perf_counter()
        for _ in range(LARGE_TIMING_REPEATS):
            for n in large:
                check(n)
        return (time.perf_counter() - start) / (LARGE_TIMING_REPEATS * len(large))

    trial_times = [time_large(trial_division_is_prime) for _ in seeds]

    rows = []
    mr_series = ([], [], [])
    fermat_series = ([], [], [])
    for k in (1, 2, 5, 10, 20):
        mr_acc = []
        fermat_acc = []
        fooled = []
        mr_times = []
        for seed in seeds:
            mr_right = sum(1 for n in candidates if miller_rabin_is_prime(n, k=k, seed=seed) == truth[n])
            fermat_right = sum(1 for n in candidates if fermat_is_prime(n, k=k, seed=seed) == truth[n])
            passed = sum(1 for n in carmichael if fermat_is_prime(n, k=k, seed=seed))
            mr_acc.append(mr_right / len(candidates))
            fermat_acc.append(fermat_right / len(candidates))
            fooled.append(passed / len(carmichael))
            mr_times.append(time_large(lambda n: miller_rabin_is_prime(n, k=k, seed=seed)))
        rows.append(
            {
                "part": "primality",
                "k": k,
                "numbers_tested": len(candidates),
                "carmichael_tested": len(carmichael),
                "trials": len(seeds),
                "seeds": _seed_text(seeds),
                "mr_mean_accuracy": _fmt(mean(mr_acc), 4),
                "mr_std_accuracy": _fmt(std_dev(mr_acc), 4),
                "fermat_mean_accuracy": _fmt(mean(fermat_acc), 4),
                "fermat_std_accuracy": _fmt(std_dev(fermat_acc), 4),
                "fermat_mean_carmichael_fooled": _fmt(mean(fooled), 4),
                "mr_error_bound_4_to_minus_k": _sci(miller_rabin_error_bound(k)),
                "large_numbers_timed": len(large),
                "mr_mean_seconds_per_large_number": _sci(mean(mr_times)),
                "mr_std_seconds_per_large_number": _sci(std_dev(mr_times)),
                "trial_division_mean_seconds_per_large_number": _sci(mean(trial_times)),
                "trial_division_std_seconds_per_large_number": _sci(std_dev(trial_times)),
                "status": "truth from trial division for every number",
            }
        )
        config = f"k={k}"
        _add_summary(summary_rows, "primality", config, "miller rabin accuracy", mr_acc)
        _add_summary(summary_rows, "primality", config, "fermat accuracy", fermat_acc)
        _add_summary(summary_rows, "primality", config, "fermat share of carmichael fooled", fooled)
        _add_summary(summary_rows, "primality", config, "miller rabin seconds per large number", mr_times)
        for series, values in ((mr_series, mr_acc), (fermat_series, fermat_acc)):
            series[0].append(k)
            series[1].append(mean(values))
            series[2].append(std_dev(values))
    _add_summary(summary_rows, "primality", "n > 10^6", "trial division seconds per large number", trial_times)
    save_errorbar_plot(
        RESULTS / "primality_accuracy.png",
        {"miller rabin": mr_series, "fermat": fermat_series},
        "rounds k",
        "mean share matching trial division",
        f"Primality accuracy versus rounds, {len(candidates)} numbers, {len(seeds)} seeds",
    )
    return rows


def run_bloom(seeds, summary_rows) -> list:
    m_bits = 256
    k_hashes = 3
    query_count = 1000
    inserted_all = [f"in-{i}" for i in range(120)]
    queries = [f"out-{i}" for i in range(query_count)]
    rows = []
    measured_series = ([], [], [])
    theory_series = ([], [], None)
    for n_items in (20, 40, 80, 120):
        inserted = inserted_all[:n_items]
        rates = []
        loads = []
        for seed in seeds:
            rates.append(measured_false_positive_rate(inserted, queries, m_bits, k_hashes, seed))
            bloom = BloomFilter(m_bits, k_hashes, seed)
            for item in inserted:
                bloom.add(item)
            loads.append(bloom.load_factor())
        theory = bloom_false_positive(k_hashes, n_items, m_bits)
        rows.append(
            {
                "part": "bloom",
                "n_items": n_items,
                "m_bits": m_bits,
                "k_hashes": k_hashes,
                "queries": query_count,
                "trials": len(seeds),
                "seeds": _seed_text(seeds),
                "mean_measured_fp": _fmt(mean(rates), 4),
                "std_measured_fp": _fmt(std_dev(rates), 4),
                "theory_fp": _fmt(theory, 4),
                "mean_load_factor": _fmt(mean(loads), 4),
                "std_load_factor": _fmt(std_dev(loads), 4),
                "status": "ok",
            }
        )
        config = f"n_items={n_items} m={m_bits} k={k_hashes}"
        _add_summary(summary_rows, "bloom", config, "measured false positive rate", rates)
        _add_summary(summary_rows, "bloom", config, "load factor", loads)
        measured_series[0].append(n_items)
        measured_series[1].append(mean(rates))
        measured_series[2].append(std_dev(rates))
        theory_series[0].append(n_items)
        theory_series[1].append(theory)
    save_errorbar_plot(
        RESULTS / "bloom_filter_fp_rate.png",
        {"measured mean": measured_series, "theory": theory_series},
        "items inserted",
        "false positive rate",
        f"Bloom filter false positive rate versus load, m=256 k=3, {len(seeds)} seeds",
    )
    return rows


def run_minhash(sig_sizes, seeds, summary_rows) -> list:
    left = [f"tok{i}" for i in range(40)]
    right = [f"tok{i}" for i in range(20, 60)]
    true_j = jaccard(left, right)
    rows = []
    error_series = ([], [], [])
    theory_series = ([], [], None)
    for k in sig_sizes:
        estimates = [estimate_jaccard(left, right, k, seed) for seed in seeds]
        errors = [abs(true_j - value) for value in estimates]
        rows.append(
            {
                "part": "minhash",
                "signature_k": k,
                "trials": len(seeds),
                "seeds": _seed_text(seeds),
                "true_jaccard": _fmt(true_j, 4),
                "mean_estimate": _fmt(mean(estimates), 4),
                "std_estimate": _fmt(std_dev(estimates), 4),
                "mean_abs_error": _fmt(mean(errors), 4),
                "std_abs_error": _fmt(std_dev(errors), 4),
                "theory_std_estimate": _fmt(math.sqrt(true_j * (1 - true_j) / k), 4),
                "status": "ok",
            }
        )
        config = f"signature k={k}"
        _add_summary(summary_rows, "minhash", config, "estimate", estimates)
        _add_summary(summary_rows, "minhash", config, "absolute error", errors)
        error_series[0].append(k)
        error_series[1].append(mean(errors))
        error_series[2].append(std_dev(errors))
        theory_series[0].append(k)
        theory_series[1].append(math.sqrt(true_j * (1 - true_j) / k))
    save_errorbar_plot(
        RESULTS / "minhash_similarity_plot.png",
        {"mean absolute error": error_series, "theory std of estimate": theory_series},
        "signature size k",
        "error",
        f"MinHash error versus signature size, true Jaccard {true_j:.3f}, {len(seeds)} seeds",
        logx=True,
    )
    return rows


def run(quick: bool = False, trials=None) -> None:
    started = time.perf_counter()
    RESULTS.mkdir(parents=True, exist_ok=True)
    if trials is None:
        trials = 3 if quick else 5
    if trials < 1:
        raise ValueError("trials must be at least 1")
    seeds = trial_seeds(trials)
    sizes = [100, 1000] if quick else [100, 1000, 10000, 50000, 100000]
    sig_sizes = [16, 32, 64] if quick else [16, 32, 64, 128, 256, 512]
    print(f"{trials} trials per configuration, seeds {_seed_text(seeds)}", flush=True)

    summary_rows = []
    outputs = {}
    parts = (
        ("quicksort_results.csv", lambda: run_quicksort(sizes, seeds, summary_rows)),
        ("selection_results.csv", lambda: run_selection(sizes, seeds, summary_rows)),
        ("primality_results.csv", lambda: run_primality(seeds, summary_rows)),
        ("bloom_results.csv", lambda: run_bloom(seeds, summary_rows)),
        ("minhash_results.csv", lambda: run_minhash(sig_sizes, seeds, summary_rows)),
    )
    for name, part in parts:
        part_start = time.perf_counter()
        print(f"running {name.replace('_results.csv', '')}", flush=True)
        outputs[name] = _write_csv(RESULTS / name, part())
        print(f"  done in {time.perf_counter() - part_start:.1f} s", flush=True)
    outputs["summary_table.csv"] = _write_csv(RESULTS / "summary_table.csv", summary_rows)

    print()
    print(f"results folder: {RESULTS}")
    for name, count in outputs.items():
        print(f"  {name}: {count} rows")
    print("  plots: quicksort_comparison.png, selection_runtime.png, primality_accuracy.png,")
    print("         bloom_filter_fp_rate.png, minhash_similarity_plot.png")
    print(f"total runtime {time.perf_counter() - started:.1f} s")


if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="Week 7 randomized algorithms benchmark")
    parser.add_argument("--quick", action="store_true", help="small sizes and 3 trials")
    parser.add_argument("--trials", type=int, default=None, help="trials per configuration (default 5, or 3 with --quick)")
    args = parser.parse_args()
    run(quick=args.quick, trials=args.trials)
