"""Print the proposed audit design. Default calculations need no draw, network or private data."""

import argparse
import csv
import re
import runpy
from collections import Counter, defaultdict
from math import isclose, log, sqrt
from pathlib import Path

HERE = Path(__file__).resolve().parent
PREVIOUS = runpy.run_path(
    str(HERE.parent / "blind-audit-12-protocol-2026-11-23/sizes.py")
)
cdf, upper = PREVIOUS["cdf"], PREVIOUS["wilson_upper"]
# Anonymous histogram: (missed, completed calls on the same plant, number of plants).
HIST = {
    "Astra": [(0, 6, 12), (1, 6, 1), (2, 6, 4), (6, 6, 1)],
    "Hydrogen": [
        (0, 2, 1),
        (0, 3, 4),
        (0, 4, 2),
        (0, 5, 6),
        (0, 6, 1),
        (1, 2, 1),
        (1, 3, 1),
        (1, 5, 1),
        (3, 3, 1),
    ],
    "Sonnet": [
        (0, 2, 2),
        (0, 3, 1),
        (1, 2, 3),
        (1, 3, 2),
        (1, 4, 5),
        (2, 2, 2),
        (2, 3, 1),
        (2, 4, 1),
        (3, 4, 1),
    ],
}
ASSIGNED = {"Astra": 108, "Hydrogen": 108, "Sonnet": 69}
SHARE = 0.15
ALLOW = 2
SMOKE = 40
STRATA = {
    "PIC-18": 0.05,
    "Rest of Ohio": 0.10,
    "Rest of country": 0.10,
    "Researchers": 0.10,
    "Programs": 0.10,
    "Events and participation": 0.10,
}


def calibration(hist):
    plants = sum(freq for _, _, freq in hist)
    mean = sum(freq * misses / reads for misses, reads, freq in hist) / plants
    radius = sqrt(log(2 / 0.05) / (2 * plants))
    return mean, max(0.0, mean - radius), min(1.0, mean + radius)


def size(target, miss):
    n = ALLOW + 1
    while upper(ALLOW, n) > target or cdf(n, ALLOW, target * (1 - miss)) > 0.025:
        n += 1
    return n


def spend(n, plants):
    # Budget scenario, independent of statistical sizing. Plants go to each provider.
    second = n * (0.10 + 0.90 * SHARE)
    calls = (0.70 * n + 0.30 * second, 0.30 * n + 0.45 * second, 0.25 * second)
    return [(c + plants) * price for c, price in zip(calls, (0.05, 0.10, 0.10))]


def report():
    lines = [
        "## Decision numbers",
        "",
        "Smoke: 40 random PIC-18 records. Stop on the third k+u (3/40 = 7.5% of the planned sample).",
        "Continue only after all 40 with k+u ≤ 2, complete replay accounting and valid controls.",
        "Check each unflagged record independently with probability 15%. Every flagged record gets a second read.",
        "Full draw: allow 2 adverse records per stratum, fail immediately on 3; no early PASS.",
        "Final PASS also requires the two-sided 95% Wilson upper bound at k+u ≤ the target.",
        "",
        "| Family | Assigned plant calls | Returned | Detected on planted field | Mean miss by plant | 95% interval |",
        "|---|---:|---:|---:|---:|---:|",
    ]
    estimates = {}
    for name, hist in HIST.items():
        mean, low, high = calibration(hist)
        estimates[name] = mean, high
        reads = sum(r * f for _, r, f in hist)
        hits = reads - sum(m * f for m, _, f in hist)
        lines.append(
            f"| {name} | {ASSIGNED[name]} | {reads} | {hits} | {mean:.1%} | {low:.1%}–{high:.1%} |"
        )
    primary = max(estimates[n][0] for n in ("Astra", "Hydrogen"))
    stress = max(estimates[n][1] for n in ("Astra", "Hydrogen"))
    second = max(m for m, _ in estimates.values())
    checked = primary * (1 - SHARE * (1 - second))
    lines.extend(
        [
            "",
            f"Planning miss probabilities: single {primary:.2%}, single plus checks {checked:.2%}, stress {stress:.2%}.",
            "Minimum n satisfying Wilson and ≤2.5% boundary PASS in the stress model. Percentages below are",
            "P(final PASS), conditional on starting the draw in the independent-record model. Each pair is at target / 1.5× target.",
            "",
            "| Stratum | Target | n | Stop / fail | Perfect reads | Single | Single + checks | Stress, no rescue |",
            "|---|---:|---:|---:|---:|---:|---:|---:|",
        ]
    )
    total = 0
    for name, t in STRATA.items():
        n = size(t, stress)
        total += n
        cells = [
            f"{100 * cdf(n, ALLOW, t * (1 - m)):.4f}% / {100 * cdf(n, ALLOW, 1.5 * t * (1 - m)):.4f}%"
            for m in (0, primary, checked, stress)
        ]
        lines.append(f"| {name} | {t:.0%} | {n} | 3 | " + " | ".join(cells) + " |")
    lines.extend(
        [
            "",
            "Operating cost of the tight acceptance line: at a true 2% error rate and perfect reads,",
            f"PIC-18 passes {cdf(size(0.05, stress), ALLOW, 0.02):.1%} of draws and each other stratum passes {cdf(size(0.10, stress), ALLOW, 0.02):.1%};",
            f"at a 5% true adverse rate the smoke gate alone advances {cdf(SMOKE, ALLOW, 0.05):.1%} of the time (perfect reads).",
            "Small displayed percentages are rounded; the binomial tail is positive.",
        ]
    )
    lines.extend(
        [
            "",
            "## Input-token budget",
            "",
            "Audit 12 long-thread input per record read: Astra ~0.13M, Sonnet ~0.65M, Gemini ~1.0M (unverified).",
            "Audit 12 total ~450M. Fresh-call hypotheses: Astra 0.05M, Hydrogen 0.10M, Sonnet 0.10M.",
            "Scenario: 70/30% primary Astra/Hydrogen. Second reads split 30/45/25% Astra/Hydrogen/Sonnet.",
            "Assume 10% flagged, plus 15% of the remainder. Counts of checks and routing shares are expectations.",
            "Add 3 blind plant calls per provider for smoke and 6 more per provider for the full draw.",
            "",
            "| Stage (M input tokens) | Real records | OpenAI | Google | Anthropic | Total |",
            "|---|---:|---:|---:|---:|---:|",
        ]
    )
    for label, n, plants in [
        ("Smoke only", SMOKE, 3),
        ("Draw only", total, 6),
        ("Smoke + full draw", total + SMOKE, 9),
    ]:
        costs = spend(n, plants)
        lines.append(
            f"| {label} | {n} | "
            + " | ".join(f"{v:.2f}" for v in [*costs, sum(costs)])
            + " |"
        )
    return "\n".join(lines) + "\n"


START, END = "<!-- sizes begin -->\n", "<!-- sizes end -->"


def check():
    assert isclose(spend(SMOKE, 3)[0], 1.691) and sum(spend(SMOKE, 3)) < 4.16
    assert SHARE == 0.15 and ALLOW == 2 and SMOKE == 40
    assert cdf(2, 0, 0.5) == 0.25 and round(upper(0, 20), 6) == 0.161125
    for h in HIST.values():
        assert sum(freq for _, _, freq in h) == 18
    stress = max(calibration(HIST[f])[2] for f in ("Astra", "Hydrogen"))
    for t in STRATA.values():
        n = size(t, stress)
        assert (
            cdf(n, ALLOW, t * (1 - stress))
            <= 0.025
            < cdf(n - 1, ALLOW, t * (1 - stress))
        )
        assert upper(ALLOW, n) <= t
    result = report()
    assert (HERE / "SIZES.md").read_text() == result, (
        "SIZES.md differs from calculation"
    )
    before, body = (HERE / "PROTOCOL.md").read_text().split(START)
    printed, after = body.split(END)
    assert printed == result, "PROTOCOL.md differs from calculation"
    # All numeric prose belongs in the computed block. Links are source locators.
    assert not re.search(r"\d", re.sub(r"\]\([^)]*\)", "]", before + after)), (
        "untraced protocol number"
    )
    print("sizes selftest: PASS")


def check_private(root):
    """Reproduce the aggregate calibration without printing record-level information."""

    def read(path):
        with path.open(newline="") as stream:
            return list(csv.DictReader(stream))

    plants = {
        r["record_id"]: r["field"]
        for r in read(root / "audit12-draw-985ed36/plants.csv")
    }
    assert len(plants) == 18
    for prefix, family in [
        ("astra", "Astra"),
        ("gemini", "Hydrogen"),
        ("sonnet", "Sonnet"),
    ]:
        per_plant = defaultdict(list)
        assigned = 0
        for lane in (root / "audit12-read-985ed36").glob(prefix + "-*"):
            grades = defaultdict(list)
            for verdict in read(lane / "out/verdicts.csv"):
                grades[verdict["blind_id"]].append(verdict)
            for packet in read(lane / "blind.csv"):
                key = packet["record_id"]
                if key not in plants:
                    continue
                assigned += 1
                responses = grades[packet["blind_id"]]
                if responses:
                    hit = any(
                        v["field"] == plants[key]
                        and v["verdict"] in {"FIELD_ERROR", "UNRESOLVED"}
                        and "withheld" not in v["note"].lower()
                        for v in responses
                    )
                    per_plant[key].append(hit)
        histogram = Counter((len(v) - sum(v), len(v)) for v in per_plant.values())
        assert assigned == ASSIGNED[family] and histogram == {
            (m, r): f for m, r, f in HIST[family]
        }, family
    print("private calibration: PASS")


if __name__ == "__main__":
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--selftest", action="store_true")
    parser.add_argument(
        "--check-private",
        type=Path,
        metavar="PRIVATE_ROOT",
        help="verify frozen plant histograms locally",
    )
    args = parser.parse_args()
    if args.check_private:
        check_private(args.check_private)
    elif args.selftest:
        check()
    else:
        print(report(), end="")
