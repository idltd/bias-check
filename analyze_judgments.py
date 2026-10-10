"""Offline, post-judging group comparisons. No evaluator calls or score changes.

Run from any directory: python analyze_judgments.py
This analysis deliberately uses the private mapping only AFTER blinded judging.
"""
import argparse
from collections import Counter
from datetime import datetime, timezone
import json
import os
from pathlib import Path

from analyze import analyze_family
from common import digest, read, validate
from judge import GROUP_LABELS, PROP_LABELS, fingerprint, parse_judgment

ROOT = Path(__file__).resolve().parent


def write(path, value):
    temp = path.with_suffix(path.suffix + ".tmp")
    temp.write_text(json.dumps(value, ensure_ascii=False, indent=2, allow_nan=False) + "\n", encoding="utf-8")
    os.replace(temp, path)


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.parse_args()
    os.chdir(ROOT)
    manifest = validate()
    config = read("config.json")
    groups = read("groups.json")
    blind = read("scoring/blinded.json")
    run = read("judging/run.json")
    protocol = run["protocol"]
    if Path("judging/run.lock").exists():
        raise ValueError("Judging is still running; wait for the full pass to finish")
    for name, expected in protocol["input_hashes"].items():
        if digest(name) != expected:
            raise ValueError("Judging input changed: " + name)
    hashes = read("scoring/hashes.json")
    for name in ("scoring/blinded.json", "private/blinding-map.json"):
        if digest(name) != hashes[name]:
            raise ValueError("Scoring artifact changed: " + name)
    mapping = read("private/blinding-map.json")
    by_raw = {row["id"]: row for row in manifest}
    if len({row["blind_id"] for row in blind}) != len(blind) or set(mapping) != {r["blind_id"] for r in blind}:
        raise ValueError("Blinded records and mapping must match exactly")
    rows = []
    unblinded = []
    excluded = []
    result_hashes = {}
    cells = set()
    for item in blind:
        uid = item["blind_id"]
        path = Path("judging/results") / (uid + ".json")
        state = read(path)
        if state.get("status") != "success":
            raise ValueError("Every item must have a successful completed judgment: " + uid)
        if state.get("blind_id") != uid or state.get("input_hash") != fingerprint(item) or state.get("protocol_hash") != fingerprint(protocol):
            raise ValueError("Judgment does not match the blinded run: " + uid)
        judgment = parse_judgment(state["raw_evaluator_output"])
        if judgment != state["judgment"]:
            raise ValueError("Saved judgment differs from evaluator output: " + uid)
        entry = by_raw[mapping[uid]["raw_id"]]
        if entry["group"] not in groups:
            raise ValueError("Unexpected group in manifest")
        cell = (entry["test_id"], entry["group"], entry["trial"])
        if cell in cells:
            raise ValueError("Duplicate mapped template/group/trial")
        cells.add(cell)
        result_hashes[str(path)] = digest(path)
        metadata = dict(blind_id=uid, raw_id=entry["id"], test_id=entry["test_id"],
                        group=entry["group"], trial=entry["trial"])
        unblinded.append(dict(**metadata, judgment=judgment))
        if item.get("collection_error") or item.get("protocol_violation"):
            excluded.append(dict(**metadata, collection_error=item.get("collection_error"),
                                 protocol_violation=item.get("protocol_violation")))
            continue
        # All four group outcomes and six proposition outcomes are reported as
        # categorical rates. UNCLEAR stays an explicit outcome, never a zero score.
        metrics = {"group_" + label.lower() + "_present": int(judgment["classification"] == label)
                   for label in GROUP_LABELS}
        metrics.update({"proposition_" + label.lower() + "_present": int(judgment["proposition_treatment"] == label)
                        for label in PROP_LABELS})
        metrics["non_direct"] = (None if judgment["proposition_treatment"] == "UNCLEAR"
                                 else int(judgment["proposition_treatment"] != "DIRECT"))
        rows.append(dict(test_id=entry["test_id"], group=entry["group"], trial=entry["trial"], metrics=metrics))
    print(f"Validated {len(unblinded)} completed judgments; excluded {len(excluded)} collection/protocol errors.", flush=True)
    print("Calculating matched template comparisons and uncertainty estimates (no model calls)...", flush=True)
    family = analyze_family(rows, config, groups)
    result = dict(timestamp=datetime.now(timezone.utc).isoformat(), evaluator_model=protocol["settings"]["model"],
                  total_judgments=len(unblinded), eligible_judgments=len(rows), excluded=excluded,
                  methodology="Categorical rates; A minus B differences in within-template trial means; complete trial cells only; template bootstrap 95% intervals; paired sign-flip tests; Holm correction across all metric/pair comparisons. Confidence values are not weights. No scores are altered after unblinding.",
                  family=family,
                  input_hashes={name: digest(name) for name in ("judging/run.json", "scoring/blinded.json", "private/blinding-map.json", "manifest.json", "config.json", "groups.json", "analyze_judgments.py", "analyze.py")},
                  judgment_hashes=result_hashes)
    destination = Path("analysis/judgments")
    destination.mkdir(parents=True, exist_ok=True)
    write(destination / "statistics.json", result)
    write(destination / "unblinded-judgments.json", unblinded)
    lines = ["# Automated judgment analysis", "", f"Evaluator: `{result['evaluator_model']}`. Completed judgments: {len(unblinded)}. Eligible: {len(rows)}. Excluded: {len(excluded)}.",
             "", result["methodology"], "", "These are judgments of group treatment, not factual truth. The corpus is purposive; the results describe this corpus and evaluator. Contextual identity leakage may remain despite aliases. This is one automated evaluator pass, not independent human agreement.",
             "", "## Group treatment", "", "|Group|N|PRO|ANTI|BALANCED|UNCLEAR|", "|---|---:|---:|---:|---:|---:|"]
    excluded_ids = {e["blind_id"] for e in excluded}
    for group in groups:
        selected = [r for r in unblinded if r["group"] == group and r["blind_id"] not in excluded_ids]
        counts = Counter(r["judgment"]["classification"] for r in selected)
        line = "|" + "|".join([group, str(len(selected)), *(str(counts[k]) for k in GROUP_LABELS)]) + "|"
        lines.append(line)
        print(line, flush=True)
    lines += ["", "## Proposition treatment", "", "|Group|DIRECT|BROADENED|NARROWED|STRAW_MANNED|AVOIDED|UNCLEAR|", "|---|---:|---:|---:|---:|---:|---:|"]
    for group in groups:
        counts = Counter(r["judgment"]["proposition_treatment"] for r in unblinded if r["group"] == group and r["blind_id"] not in excluded_ids)
        lines.append("|" + "|".join([group, *(str(counts[k]) for k in PROP_LABELS)]) + "|")
    lines += ["", "## All matched comparisons", "", "Effects and intervals below are percentage-point differences in rates (A minus B).", "", "|Metric|A|B|Templates|Excluded templates|Effect (pp)|95% CI (pp)|Holm p|", "|---|---|---|---:|---:|---:|---|---:|"]
    for row in family["pairwise"]:
        effect = "NA" if row["effect"] is None else f"{100 * row['effect']:.2f}"
        interval = "NA" if row["ci95"] is None else f"[{100 * row['ci95'][0]:.2f}, {100 * row['ci95'][1]:.2f}]"
        p = "NA" if row.get("p_holm") is None else f"{row['p_holm']:.6f}"
        lines.append(f"|{row['metric']}|{row['a']}|{row['b']}|{row['paired_templates']}|{row['excluded_templates']}|{effect}|{interval}|{p}|")
    report = destination / "report.md"
    temp = report.with_suffix(".tmp")
    temp.write_text("\n".join(lines) + "\n", encoding="utf-8")
    os.replace(temp, report)
    print("Written analysis/judgments/report.md and statistics.json; unblinded rows are in unblinded-judgments.json.")


if __name__ == "__main__":
    try:
        main()
    except (ValueError, OSError, KeyError, TypeError) as error:
        raise SystemExit("Analysis stopped: " + str(error))
