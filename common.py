import hashlib, json
from pathlib import Path

def read(p):
    return json.loads(Path(p).read_text(encoding='utf-8'))

def digest(p):
    return hashlib.sha256(Path(p).read_bytes()).hexdigest()

def save(p, value):
    p = Path(p)
    p.parent.mkdir(parents=True, exist_ok=True)
    with p.open('x', encoding='utf-8', newline='\n') as f:
        json.dump(value, f, ensure_ascii=False, indent=2)
        f.write('\n')

def validate():
    for p, h in read('freeze.json')['hashes'].items():
        if digest(p) != h:
            raise ValueError('Frozen file changed: ' + p)
    return read('manifest.json')

def raw_records():
    manifest = validate()
    rows = []
    for entry in manifest:
        p = Path('raw') / (entry['id'] + '.json')
        if p.exists():
            if digest(p) != read(str(p)+'.sha256.json')['sha256']:
                raise ValueError('Raw data changed: '+str(p))
            row = read(p)
            for key in entry:
                if row[key] != entry[key]:
                    raise ValueError('Raw entry differs from manifest')
            rows.append(row)
    return rows
