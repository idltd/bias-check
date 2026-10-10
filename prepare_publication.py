"""Build an auditable final snapshot without changing the frozen experiment."""
import csv
import hashlib
import json
from pathlib import Path
import shutil

ROOT = Path(__file__).resolve().parent
DEST = ROOT / 'publication'


def main():
    if DEST.exists():
        raise SystemExit('publication already exists; refusing to overwrite it')
    experiment = DEST / 'experiment'
    experiment.mkdir(parents=True)
    names = ['README.md', 'script.md', 'tests.json', 'groups.json', 'config.json',
             'manifest.json', 'rubric.json', 'freeze.json', 'common.py',
             'prepare.py', 'execute.py', 'score.py', 'analyze.py', 'verify.py',
             'judge.py', 'judge-prompt.md', 'analyze_judgments.py']
    names += ['scoring/' + p.name for p in (ROOT / 'scoring').glob('*.json')]
    names += ['private/blinding-map.json', 'judging/run.json']
    names += ['judging/results/' + p.name for p in (ROOT / 'judging/results').glob('*.json')]
    names += ['raw/' + p.name for p in (ROOT / 'raw').glob('*.json')]
    names += ['analysis/judgments/' + name for name in
              ['report.md', 'statistics.json', 'unblinded-judgments.json']]
    for name in names:
        target = experiment / name
        target.parent.mkdir(parents=True, exist_ok=True)
        shutil.copyfile(ROOT / name, target)

    judgments = json.loads((experiment / 'analysis/judgments/unblinded-judgments.json').read_text(encoding='utf-8'))
    stats = json.loads((experiment / 'analysis/judgments/statistics.json').read_text(encoding='utf-8'))
    excluded = {row['raw_id'] for row in stats['excluded']}
    columns = ['raw_id', 'blind_id', 'test_id', 'category', 'group', 'trial', 'model',
               'prompt', 'exact_response', 'eligible', 'collection_error', 'protocol_violation',
               'classification', 'confidence', 'reason', 'proposition_treatment',
               'proposition_confidence', 'proposition_reason']
    with (DEST / 'results.csv').open('w', encoding='utf-8', newline='') as output:
        writer = csv.DictWriter(output, fieldnames=columns)
        writer.writeheader()
        for judgment in judgments:
            raw = json.loads((experiment / 'raw' / (judgment['raw_id'] + '.json')).read_text(encoding='utf-8'))
            row = {key: raw.get(key, '') for key in columns}
            row.update({key: judgment[key] for key in ['raw_id', 'blind_id', 'test_id', 'group', 'trial']})
            row.update(judgment['judgment'])
            row['eligible'] = judgment['raw_id'] not in excluded
            row['collection_error'] = raw.get('error')
            writer.writerow({key: row.get(key, '') for key in columns})
    (DEST / '.gitattributes').write_text('* -text\n', encoding='utf-8')
    (DEST / '.gitignore').write_text('__pycache__/\n*.pyc\n.venv/\n', encoding='utf-8')
    hashes = {p.relative_to(DEST).as_posix(): hashlib.sha256(p.read_bytes()).hexdigest()
              for p in sorted(experiment.rglob('*')) if p.is_file()}
    hashes['results.csv'] = hashlib.sha256((DEST / 'results.csv').read_bytes()).hexdigest()
    (DEST / 'checksums.json').write_text(json.dumps(hashes, indent=2) + '\n', encoding='utf-8')
    print(f'Prepared {len(names)} original files and {len(judgments)} CSV rows in {DEST}')


if __name__ == '__main__':
    main()
