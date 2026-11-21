"""Measure Bubble Sort on descending inputs of several sizes."""

from __future__ import annotations

import csv
import time
from pathlib import Path

import matplotlib.pyplot as plt


BASE_DIR = Path(__file__).resolve().parent
TRIAL_COUNT = 5
TARGET_BATCH_SECONDS = 0.10
MIN_REPETITIONS = 5


def bubble_sort(values: list[int]) -> list[int]:
    """Sort values in place with Bubble Sort and return the same list.

    The early-exit flag avoids unnecessary passes when a list is already
    sorted. A descending list still triggers all required comparisons.
    """
    n = len(values)
    for end in range(n - 1, 0, -1):
        swapped = False
        for index in range(end):
            if values[index] > values[index + 1]:
                values[index], values[index + 1] = values[index + 1], values[index]
                swapped = True
        if not swapped:
            break
    return values


def make_inputs() -> dict[str, list[int]]:
    """Keep the assignment's ascending arrays and derive descending inputs."""
    original_arrays = {
        "Arr1": list(range(1, 6)),
        "Arr2": list(range(1, 11)),
        "Arr3": list(range(1, 51)),
        "Arr4": list(range(1, 101)),
    }
    # Reversing copies preserves the supplied ascending arrays unchanged.
    return {name: list(reversed(values)) for name, values in original_arrays.items()}


def timed_batch(values: list[int], repetitions: int) -> int:
    """Return total sort time in ns; copy setup is outside each timed interval."""
    total_ns = 0
    # These inputs contain each integer from 1 through N exactly once.
    expected = list(range(1, len(values) + 1))
    for _ in range(repetitions):
        working_copy = values.copy()
        start_ns = time.perf_counter_ns()
        bubble_sort(working_copy)
        total_ns += time.perf_counter_ns() - start_ns
        if working_copy != expected:
            raise RuntimeError("Bubble Sort produced an incorrect result.")
    return total_ns


def choose_repetitions(values: list[int]) -> int:
    """Calibrate a batch so each measurement trial has enough timer samples."""
    probe_count = MIN_REPETITIONS
    while True:
        start = time.perf_counter()
        timed_batch(values, probe_count)
        elapsed = time.perf_counter() - start
        if elapsed >= TARGET_BATCH_SECONDS:
            return probe_count
        estimate = max(probe_count + 1, int(probe_count * TARGET_BATCH_SECONDS / max(elapsed, 1e-9)))
        probe_count = min(estimate, probe_count * 10)


def write_csv(rows: list[dict[str, object]]) -> None:
    path = BASE_DIR / "results.csv"
    fieldnames = ["array", "input_size", "repetitions_per_trial", "trial_1_us", "trial_2_us",
                  "trial_3_us", "trial_4_us", "trial_5_us", "average_time_us"]
    with path.open("w", newline="", encoding="utf-8") as csv_file:
        writer = csv.DictWriter(csv_file, fieldnames=fieldnames)
        writer.writeheader()
        writer.writerows(rows)


def write_graph(rows: list[dict[str, object]]) -> None:
    sizes = [int(row["input_size"]) for row in rows]
    averages = [float(row["average_time_us"]) for row in rows]
    fig, axis = plt.subplots(figsize=(8.5, 5.2), constrained_layout=True)
    axis.plot(sizes, averages, color="#2457A7", marker="o", linewidth=2, markersize=7)
    axis.set_title("Bubble Sort Worst-Case Performance", fontsize=14, weight="bold")
    axis.set_xlabel("Input Size (N)")
    axis.set_ylabel("Average Execution Time (Microseconds)")
    axis.set_xticks(sizes)
    axis.grid(True, linestyle="--", alpha=0.45)
    axis.spines[["top", "right"]].set_visible(False)
    fig.savefig(BASE_DIR / "results_graph.png", dpi=180)
    plt.close(fig)


def main() -> None:
    rows: list[dict[str, object]] = []
    for name, descending_values in make_inputs().items():
        repetitions = choose_repetitions(descending_values)
        trial_times_us = [timed_batch(descending_values, repetitions) / repetitions / 1_000
                          for _ in range(TRIAL_COUNT)]
        row: dict[str, object] = {
            "array": name,
            "input_size": len(descending_values),
            "repetitions_per_trial": repetitions,
            **{f"trial_{index + 1}_us": round(value, 6)
               for index, value in enumerate(trial_times_us)},
            "average_time_us": round(sum(trial_times_us) / len(trial_times_us), 6),
        }
        rows.append(row)

    write_csv(rows)
    write_graph(rows)
    print("Bubble Sort empirical results (descending worst-case inputs)")
    print(f"{'Array':<8}{'N':>6}{'Repetitions/trial':>21}{'Average (µs)':>17}")
    for row in rows:
        print(f"{row['array']:<8}{row['input_size']:>6}{row['repetitions_per_trial']:>21,}"
              f"{row['average_time_us']:>17.6f}")
    print("\nCreated results.csv and results_graph.png")


if __name__ == "__main__":
    main()
