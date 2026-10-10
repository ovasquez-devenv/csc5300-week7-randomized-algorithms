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
```

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

`benchmarks\week7_randomized_benchmark.py` writes the five plots and `summary_table.csv` into `benchmarks\results`. On sorted or reverse input the fixed-pivot sort is capped at n = 2000, and those rows say "deterministic capped above n=2000" instead of a time.

`tests\` has the six pytest files named in the assignment. `examples\week7_demo.py` is a short smoke run.

## Book sections

Blackboard lists Amakobe Chapter 6 sections 6.1 to 6.8. In my copy, randomized QuickSort is section 6.2, selection is section 6.3, and Bloom filters are section 6.4.3. I cite the numbers printed in the book.

## Limits

The deterministic sorted and reverse cases are capped at n = 2000 because the fixed pivot goes quadratic there.

## AI disclosure

I used AI to help me format this documentation.
