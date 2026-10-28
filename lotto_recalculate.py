#!/usr/bin/env python3
"""
Download all Lotto 6/45 draw results from a public JSON mirror, validate the
draw sequence, and recalculate number frequencies from the six main numbers
(bonus numbers excluded).

Usage:
    python lotto_recalculate.py
    python lotto_recalculate.py --out lotto_analysis

Requires:
    pip install requests
"""
import argparse
import collections
import json
import math
import sys
from pathlib import Path

import requests

URL = "https://smok95.github.io/lotto/results/all.json"


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("--out", default="lotto_analysis", help="output directory")
    args = parser.parse_args()
    out = Path(args.out)
    out.mkdir(parents=True, exist_ok=True)

    response = requests.get(URL, timeout=60)
    response.raise_for_status()
    raw = response.json()
    if not isinstance(raw, list) or not raw:
        raise ValueError("Expected a non-empty JSON list")

    draws = sorted(raw, key=lambda d: int(d["draw_no"]))
    draw_ids = [int(d["draw_no"]) for d in draws]
    expected = list(range(draw_ids[0], draw_ids[-1] + 1))
    if draw_ids != expected:
        missing = sorted(set(expected) - set(draw_ids))
        raise ValueError(f"Draw sequence has gaps; missing draw numbers: {missing[:30]}")

    freq = collections.Counter()
    bonus_freq = collections.Counter()
    for draw in draws:
        nums = [int(n) for n in draw["numbers"]]
        if len(nums) != 6 or len(set(nums)) != 6 or not all(1 <= n <= 45 for n in nums):
            raise ValueError(f"Invalid main numbers in draw {draw['draw_no']}: {nums}")
        freq.update(nums)
        bonus = draw.get("bonus_no")
        if bonus is not None:
            bonus_freq[int(bonus)] += 1

    latest = draws[-1]
    total_main_numbers = len(draws) * 6
    expected_freq = len(draws) * 6 / 45
    rows = []
    for n in range(1, 46):
        rows.append({
            "number": n,
            "main_number_hits": freq[n],
            "hit_rate_percent": round(freq[n] / len(draws) * 100, 3),
            "bonus_hits_separate": bonus_freq[n],
        })

    # Pick six highest-frequency numbers, tie-break by lower number.
    # This is a descriptive frequency pick, not a claim of higher future odds.
    top6 = sorted(sorted(range(1, 46), key=lambda n: (-freq[n], n))[:6])

    # Recent 100-draw frequency as a separate descriptive view.
    recent = draws[-min(100, len(draws)):]
    recent_freq = collections.Counter(
        n for d in recent for n in map(int, d["numbers"])
    )
    recent_top6 = sorted(sorted(range(1, 46), key=lambda n: (-recent_freq[n], n))[:6])

    # Pair frequencies over all historical draws.
    pair_freq = collections.Counter()
    for d in draws:
        nums = sorted(map(int, d["numbers"]))
        for i in range(6):
            for j in range(i + 1, 6):
                pair_freq[(nums[i], nums[j])] += 1

    # Verify all main-number appearances total exactly 6 per draw.
    assert sum(freq.values()) == total_main_numbers

    csv_path = out / "number_frequencies.csv"
    with csv_path.open("w", encoding="utf-8-sig", newline="") as f:
        import csv
        writer = csv.DictWriter(f, fieldnames=rows[0].keys())
        writer.writeheader()
        writer.writerows(rows)

    draws_path = out / "all_draws.json"
    draws_path.write_text(json.dumps(draws, ensure_ascii=False, indent=2), encoding="utf-8")

    report = []
    report.append(f"Draws analyzed: {len(draws)} (draw {draw_ids[0]}–{draw_ids[-1]})")
    report.append(f"Latest draw date: {latest.get('date', 'unknown')}")
    report.append(f"Main-number observations: {total_main_numbers}")
    report.append(f"Expected frequency per number under a fair draw: {expected_freq:.2f}")
    report.append("")
    report.append("ALL-TIME TOP 15 (bonus excluded):")
    for n in sorted(range(1, 46), key=lambda n: (-freq[n], n))[:15]:
        report.append(f"  {n:2d}: {freq[n]} hits ({freq[n] / len(draws) * 100:.2f}% of draws)")
    report.append("")
    report.append(f"Frequency-based six-number candidate: {top6}")
    report.append(f"Recent-{len(recent)}-draw frequency candidate: {recent_top6}")
    report.append("")
    report.append("TOP 15 NUMBER PAIRS:")
    for (a, b), count in pair_freq.most_common(15):
        report.append(f"  {a:2d}-{b:2d}: {count}")
    report.append("")
    report.append("Interpretation: historical frequencies describe past draws only.")
    report.append("Every distinct 6-number combination still has the same first-prize odds.")
    report_text = "\n".join(report) + "\n"
    (out / "report.txt").write_text(report_text, encoding="utf-8")
    print(report_text)
    print(f"Saved: {csv_path}")
    print(f"Saved: {draws_path}")
    print(f"Saved: {out / 'report.txt'}")


if __name__ == "__main__":
    try:
        main()
    except Exception as exc:
        print(f"ERROR: {exc}", file=sys.stderr)
        raise
