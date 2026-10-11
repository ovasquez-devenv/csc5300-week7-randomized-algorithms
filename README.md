# CSC 5300 Week 7: Randomized Algorithms (Embracing Uncertainty for Certainty)

Omar Vasquez
Concordia University Texas MCS

This project builds a small library of randomized algorithms (randomized QuickSort, QuickSelect, Fermat and Miller-Rabin primality tests, a Bloom filter, and MinHash similarity), tests each one with pytest, and benchmarks them against deterministic versions. The technical report is in `analysis/week7_report.md`.

I built and ran it on Windows 11 with plain Python 3.14.7 (not Anaconda).

## Setup

```
git clone https://github.com/ovasquez-devenv/csc5300-week7-randomized-algorithms.git
cd csc5300-week7-randomized-algorithms
python -m pip install -r requirements.txt
```

Set PYTHONPATH to the project folder before running anything:

```
set PYTHONPATH=.            (Command Prompt)
$env:PYTHONPATH="."         (PowerShell)
```

## How to run

```
python examples\week7_demo.py
python -m pytest -v
python benchmarks\week7_randomized_benchmark.py
python benchmarks\week7_randomized_benchmark.py --quick
python benchmarks\week7_randomized_benchmark.py --trials 10
```

The full benchmark takes about 1.5 minutes on my laptop (91 seconds on my last run). Most of that is two single runs of the duplicates input. `--quick` uses n = 100 and 1000 with 3 trials and finishes in a few seconds. `--trials` sets how many seeded trials each configuration gets (default 5).

The test suite has 22 tests and all of them pass.

Each part can also be tested by itself:

```
python -m pytest tests\test_randomized_quicksort.py -v
python -m pytest tests\test_randomized_selection.py -v
python -m pytest tests\test_montecarlo_primality.py -v
python -m pytest tests\test_bloom_filter.py -v
python -m pytest tests\test_minhash_similarity.py -v
python -m pytest tests\test_randomized_benchmark.py -v
```

## What is in here

`src\randomized` has the Week 7 pieces.

- `week2_quicksort.py` is my Week 2 quick_sort copied from that submission. It already picks a random pivot with random.randint, uses Lomuto partition, and cuts off at 10 items for insertion sort. Because my Week 2 code is already randomized, it is not the deterministic baseline the Week 7 instructions ask for.
- `randomized_quicksort.py` is the Week 7 randomized sort. It picks a random pivot and returns a comparison count. `deterministic_quicksort` in the same file is the fixed last-element pivot baseline, with the same Lomuto partition and cutoff.
- `randomized_selection.py` is QuickSelect with a random pivot, plus a fixed-pivot select and a sort-then-index comparison. k is 0-based. It records recursion depth.
- `montecarlo_primality.py` has the Fermat test, Miller-Rabin, and trial division. Carmichael numbers 561, 1105, 1729, 2465, 2821, and 6601 are included so Fermat can be shown failing.
- `bloom_filter.py` is a bit array with k hashes. add and check are the required methods. measured_false_positive_rate compares absent queries with the theoretical rate.
- `minhash_similarity.py` estimates Jaccard similarity. The book mentions MinHash in the Chapter 6 introduction and does not give it a section, so the estimate is built from k independent hashes and tied to universal hashing in Amakobe section 6.4.2.

`src\utils` has `random_utils.py` (base seed 5300), `probability_analysis.py` (mean, variance, Bloom formula, Miller-Rabin bound), and `visualization.py`.

`benchmarks\week7_randomized_benchmark.py` runs every configuration 5 times and reports the mean and sample standard deviation. It writes these files into `benchmarks\results`:

- `quicksort_results.csv`: time and comparison count for the randomized sort, the Week 2 copy, and the fixed-pivot sort, for each n and input shape (random, sorted, reverse, duplicates).
- `selection_results.csv`: QuickSelect and sort-then-index for the min, median, and max, with time and recursion depth.
- `primality_results.csv`: Miller-Rabin and Fermat accuracy for k = 1, 2, 5, 10, 20, the share of Carmichael numbers that fool Fermat, the 4^-k error bound, and Miller-Rabin vs trial division time for numbers above 10^6. Trial division is the ground truth for every number.
- `bloom_results.csv`: measured and theoretical false positive rate and load factor for 20 to 120 items.
- `minhash_results.csv`: mean estimate and absolute error for signature sizes 16 to 512, with the theory standard deviation.
- `summary_table.csv`: one row per metric with trials, mean, standard deviation, and variance.
- Five plots with one standard deviation error bars: `quicksort_comparison.png`, `selection_runtime.png`, `primality_accuracy.png`, `bloom_filter_fp_rate.png`, and `minhash_similarity_plot.png`.

Rows that hit a limit say so in the status column instead of showing a time.

`tests\` has the six pytest files named in the assignment. `examples\week7_demo.py` is a short smoke run.

## Seeds and reproducibility

Trial t uses seed 5300 + t, so a normal run uses seeds 5300 to 5304, and each CSV lists the seeds it used. The input list for each n is built once from seed 5300 + n, so every trial uses the same data and only the algorithm's own random choices change. The Bloom filter and MinHash hash with hashlib (blake2b) instead of the built-in hash(), because Python salts hash() differently every time it starts. With hashlib the same seed gives the same result on every run and every machine.

## Book sections

Blackboard lists Amakobe Chapter 6 sections 6.1 to 6.8. In my copy, randomized QuickSort is section 6.2, selection is section 6.3, and Bloom filters are section 6.4.3. I cite the numbers printed in the book.

## Limits

The deterministic sorted and reverse cases are capped at n = 2000 because the fixed pivot goes quadratic there.

The duplicates input (values mod 7) is quadratic for every version, because Lomuto partition puts all keys equal to the pivot on one side. Above n = 10000 it runs once, randomized sort only, and the Week 2 and fixed-pivot rows are skipped. The n = 100000 run takes about a minute by itself. A three-way partition would fix this, but I kept the algorithms as they are and discuss it in the report.

## AI disclosure

I used AI to help me format this documentation.
