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
# Owner ruling 2026-11-24 ("PIC-18 only"): the audit frame is the PIC-18 owners and their sites.
STRATA = {"PIC-18": 0.05}
# Owner ruling 2026-11-24 (look-back): the gate counts k, a record with a contradicted core field.
# Unconfirmed claims (u) are reported by field and never counted. The numbers below only measure
# the open owner choices (OWNER_CHOICES.md); they decide nothing.
STOP_OPTIONS = (2, 3, 4, 5)  # smoke stops at the m-th record with a contradicted core field
CORE_RATES = (0.02, 0.05, 0.08)  # true shares of PIC-18 records with a contradicted core field
DESC_RATES = (0.0, 0.05, 0.10, 0.20)  # true shares with a contradicted descriptive field
UNCONFIRMED_SHARES = (0.10, 0.20, 392 / 1000)  # 74 of 189 audit 12 records (old unit, any field)
CEILINGS = (8, 12, 16)  # records of the smoke with an unconfirmed core claim (20%, 30%, 40%)
CORE = {"name", "status", "street", "county", "polymer_relevance"}


def grade_record(verdicts):
    """Apply the 2026-11-24 unit to one record's (field kind, verdict) pairs.

    Returns (k, unconfirmed fields, contradicted descriptive fields). A blank value is not a
    claim and never appears. UNRESOLVED is never an error; a core contradiction makes k one.
    """
    k = int(any(f in CORE and v in {"FIELD_ERROR", "CREATION_ERROR"} for f, v in verdicts))
    unconfirmed = sorted(f for f, v in verdicts if v == "UNRESOLVED")
    descriptive = sorted(
        f for f, v in verdicts if f not in CORE and v in {"FIELD_ERROR", "CREATION_ERROR"}
    )
    return k, unconfirmed, descriptive


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


def powered_plan(boundary, good, wilson_target=None):
    """First fixed n meeting the boundary risk and good-rate power requirements."""
    allowed = -1
    for n in range(1, 2001):
        while cdf(n, allowed + 1, boundary) <= 0.025 and (
            wilson_target is None or upper(allowed + 1, n) <= wilson_target
        ):
            allowed += 1
        if allowed >= 0 and cdf(n, allowed, good) >= 0.80:
            return n, allowed
    raise ValueError("No qualifying fixed design in size search")


def exact_upper(k, n):
    low, high = 0.0, 1.0
    for _ in range(55):
        mid = (low + high) / 2
        if cdf(n, k, mid) > 0.025:
            low = mid
        else:
            high = mid
    return high


def choices():
    primaries = [calibration(HIST[f]) for f in ("Astra", "Hydrogen")]
    mean = max(row[0] for row in primaries)
    stress = max(row[2] for row in primaries)
    checked = mean * (1 - SHARE * (1 - max(calibration(h)[0] for h in HIST.values())))
    plants, misses = powered_plan(0.20, mean)
    plant_cost = [plants * 0.05, plants * 0.10, 0.0]
    lines = [
        "## Decision rule",
        "",
        "Power means probability of a PIC-18 PASS conditional on reaching the draw. k counts records with a contradicted core field.",
        "Power triplets are at true record error rates of 1%, 2%, 3%, in that order. Boundary risks use no second-reader rescue.",
        "",
        "| Rule | Frame | n | Allow k / fail on | Power, perfect | Power, single + checks | PASS at target, 20% miss | PASS at target, stress | PASS at 1.5× target, 20% miss / stress |",
        "|---|---|---:|---:|---|---|---:|---:|---|",
    ]
    budgets = []
    for label in ("Stress-safe", "Plant-calibrated"):
        total = 0
        for t, region in [(0.05, "PIC-18")]:
            n, k = (
                (size(t, stress), ALLOW)
                if label == "Stress-safe"
                else powered_plan(t * 0.8, 0.02, t)
            )
            total += n
            powers = [
                " / ".join(f"{cdf(n, k, p * (1 - m)):.1%}" for p in (0.01, 0.02, 0.03))
                for m in (0, checked)
            ]
            risks = [cdf(n, k, t * (1 - m)) for m in (0.2, stress)]
            higher = [cdf(n, k, 1.5 * t * (1 - m)) for m in (0.2, stress)]
            lines.append(
                f"| {label} | {region} | {n} | {k} / {k + 1} | "
                + " | ".join(powers)
                + f" | {risks[0]:.3%} | {risks[1]:.3%} | {higher[0]:.3%} / {higher[1]:.3%} |"
            )
        costs = spend(total + SMOKE, 9)
        if label == "Plant-calibrated":
            costs = [a + b for a, b in zip(costs, plant_cost)]
        budgets.append((label, costs))
    lines.extend(
        [
            "",
            "Select the shortest fixed plant trial giving ≥80% qualification per primary at the worse historical mean miss,",
            "with a one-sided exact 97.5% upper limit ≤20% for each family (Bonferroni simultaneous coverage ≥95%).",
            f"Before drawing, score {plants} fresh distinct plants per primary family, {2 * plants} calls total. Allow ≤{misses} misses in each;",
            f"at that cutoff the upper endpoint is {exact_upper(misses, plants):.2%}. At {mean:.2%} true miss, each family qualifies with probability {cdf(plants, misses, mean):.1%}.",
            "Stop on the first excess miss or missing output. A failed calibration returns to the owner without a draw or repeat trial.",
            "Choose the smallest n allowing ≥80% power at true 2% under perfect reads, Wilson within target,",
            "and ≤2.5% boundary PASS at 20% miss. Keep k throughout; the first count above the allowance stops the draw.",
            "",
            "| Option (M input tokens) | OpenAI | Google | Anthropic | Total |",
            "|---|---:|---:|---:|---:|",
        ]
    )
    for label, costs in [
        ("Extra calibration alone", plant_cost),
        *budgets,
        ("Defer rule, smoke only", spend(SMOKE, 3)),
    ]:
        lines.append(
            f"| {label} | "
            + " | ".join(f"{v:.2f}" for v in [*costs, sum(costs)])
            + " |"
        )
    lines.append(
        "Draw-option totals include smoke, routine controls and all planned records. The calibrated total also includes the extra calibration."
    )
    return "\n".join(lines) + "\n"


def owner_figures():
    comparison = choices().splitlines()
    # Keep the decision memo's PIC-18 power and provider budgets tied to the full tables.
    rows = [
        "| PIC-18 rule | Perfect reads at 1% / 2% / 3% | Single + checks at 1% / 2% / 3% |",
        "|---|---|---|",
    ]
    for row in comparison:
        if "| PIC-18 |" in row:
            cells = [c.strip() for c in row.strip("|").split("|")]
            rows.append(f"| {cells[0]} | {cells[4]} | {cells[5]} |")
    first = next(i for i, r in enumerate(comparison) if r.startswith("| Option (M"))
    return "\n".join(rows + [""] + comparison[first : first + 6]) + "\n"


def smoke_tables(stress):
    """Measured consequences of the open smoke choices (binomial, independent records)."""
    lines = [
        "### Smoke options (answered 2026-11-24; kept for the record)",
        "",
        "smoke-stop: P(smoke reaches the end of its 40 records) at a true share of PIC-18 records with a contradicted core field.",
        "A stop at the m-th k advances with at most m−1 of 40. Perfect reads, then the stress miss.",
        "",
        "| Stop at the m-th k | " + " | ".join(f"core {p:.0%}" for p in CORE_RATES) + " | "
        + " | ".join(f"core {p:.0%}, stress" for p in CORE_RATES) + " |",
        "|---:|" + "---:|" * (2 * len(CORE_RATES)),
    ]
    for m in STOP_OPTIONS:
        cells = [f"{cdf(SMOKE, m - 1, p * (1 - miss)):.1%}" for miss in (0, stress) for p in CORE_RATES]
        lines.append(f"| {m} | " + " | ".join(cells) + " |")
    lines.extend(
        [
            "",
            "descriptive-stop: if a contradicted descriptive field also counted toward the stop at the third. Perfect reads;",
            "core and descriptive errors independent. Columns are true descriptive shares.",
            "",
            "| True core share | " + " | ".join(f"descriptive {d:.0%}" for d in DESC_RATES) + " |",
            "|---:|" + "---:|" * len(DESC_RATES),
        ]
    )
    for p in CORE_RATES[:2]:
        cells = [f"{cdf(SMOKE, 2, 1 - (1 - p) * (1 - d)):.1%}" for d in DESC_RATES]
        lines.append(f"| {p:.0%} | " + " | ".join(cells) + " |")
    lines.extend(
        [
            "",
            "unconfirmed-ceiling: P(more than the ceiling of the 40 records have an unconfirmed core claim), by true share.",
            "The 39.2% column is audit 12's any-field share under the old unit (74 of 189); the core-only share is lower and unmeasured.",
            "",
            "| Ceiling (records of 40) | " + " | ".join(f"true {q:.1%}" for q in UNCONFIRMED_SHARES) + " |",
            "|---:|" + "---:|" * len(UNCONFIRMED_SHARES),
        ]
    )
    for c in CEILINGS:
        lines.append(f"| {c} | " + " | ".join(f"{1 - cdf(SMOKE, c, q):.1%}" for q in UNCONFIRMED_SHARES) + " |")
    return lines


def report():
    lines = [
        "## Decision numbers",
        "",
        "Smoke: 40 random PIC-18 records (owners and their sites, published values only). k = records with a source-contradicted core field.",
        "Smoke stop count (owner ruling): stop at the 3rd record with a contradicted core field, 3/40 = 7.5% of the planned sample.",
        "A contradicted descriptive field is reported by field and never stops the smoke (owner ruling).",
        "Unconfirmed claims (u) are reported by field and never stop the smoke; there is no ceiling on the unconfirmed share now (owner ruling). The owner sets any ceiling for a draw after the smoke.",
        "Continue only if the stop count is not reached in all 40, with complete replay accounting and valid controls.",
        "Check each unflagged record independently with probability 15%. Every flagged record gets a second read.",
        "Stress-safe draw: allow 2 records with a contradicted core field in the PIC-18 stratum, fail immediately on 3; no early PASS.",
        "Final PASS also requires the two-sided 95% Wilson upper bound at k ≤ the target.",
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
            "Stress-safe rule: minimum n satisfying Wilson and ≤2.5% boundary PASS in the stress model. Percentages below are",
            "P(final PASS), conditional on starting the draw in the independent-record model. Each pair is at target / 1.5× target.",
            "",
            "| Frame | Target | n | Stop / fail | Perfect reads | Single | Single + checks | Stress, no rescue |",
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
            "Operating cost of the tight acceptance line: at a true 2% core-field error rate and perfect reads,",
            f"the PIC-18 draw passes {cdf(size(0.05, stress), ALLOW, 0.02):.1%} of the time.",
            "Small displayed percentages are rounded; the binomial tail is positive.",
        ]
    )
    lines.extend(["", *smoke_tables(stress)])
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
        ("Smoke + full stress-safe draw", total + SMOKE, 9),
    ]:
        costs = spend(n, plants)
        lines.append(
            f"| {label} | {n} | "
            + " | ".join(f"{v:.2f}" for v in [*costs, sum(costs)])
            + " |"
        )
    return "\n".join(lines) + "\n\n" + choices()


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
    # Independent closed-form endpoint for zero misses and exact design boundary checks.
    assert isclose(exact_upper(0, 20), 1 - 0.025 ** (1 / 20))
    plant_n, plant_k = powered_plan(
        0.20, max(calibration(HIST[f])[0] for f in ("Astra", "Hydrogen"))
    )
    assert exact_upper(plant_k, plant_n) <= 0.20 < exact_upper(plant_k + 1, plant_n)
    for t in set(STRATA.values()):
        n, k = powered_plan(t * 0.8, 0.02, t)
        assert cdf(n, k, 0.02) >= 0.80 and upper(k, n) <= t
        assert cdf(n, k, t * 0.8) <= 0.025 < cdf(n, k + 1, t * 0.8)
    # Planted cases for the 2026-11-24 unit: an unconfirmed claim is never an error, a descriptive
    # contradiction never gates, a core contradiction gates once, a blank value is no claim.
    assert grade_record([("street", "UNRESOLVED")]) == (0, ["street"], [])
    assert grade_record([("street", "FIELD_ERROR"), ("county", "UNRESOLVED")]) == (1, ["county"], [])
    assert grade_record([("name", "FIELD_ERROR"), ("status", "FIELD_ERROR")])[0] == 1
    assert grade_record([("process", "FIELD_ERROR")]) == (0, [], ["process"])
    assert grade_record([("name", "CREATION_ERROR")]) == (1, [], [])
    assert grade_record([("name", "AGREE"), ("market", "UNRESOLVED")]) == (0, ["market"], [])
    assert grade_record([]) == (0, [], [])
    # The smoke table reproduces the earlier stop-on-third value at a 5% share, perfect reads.
    assert f"{cdf(SMOKE, 2, 0.05):.1%}" in "\n".join(smoke_tables(stress))
    assert (HERE / "OWNER_CHOICES.md").read_text().split("<!-- choice figures -->\n")[
        1
    ] == "\n".join(smoke_tables(stress)) + "\n"
    assert (HERE / "OWNER_QUESTION.md").read_text().split("<!-- owner figures -->\n")[
        1
    ] == owner_figures()
    result = report()
    assert (HERE / "SIZES.md").read_text() == result, (
        "SIZES.md differs from calculation"
    )
    before, body = (HERE / "PROTOCOL.md").read_text().split(START)
    printed, after = body.split(END)
    assert printed == result, "PROTOCOL.md differs from calculation"
    # All numeric prose belongs in the computed block. Links are source locators.
    assert not re.search(r"\d", re.sub(r"PIC-18", "PIC", re.sub(r"\]\([^)]*\)", "]", before + after))), (
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
