"""Check byte-preserved imported records separately from current architecture documents."""
import hashlib
import json
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]


def main():
    manifest = json.loads((ROOT / 'records/manifest.json').read_text(encoding='utf-8'))
    seen = set()
    for entry in manifest['files']:
        repository, relative = entry['repository'], entry['path']
        if repository not in {'backend', 'frontend'} or '\\' in relative or ':' in relative:
            raise ValueError('Invalid archive path')
        if any(part in {'', '.', '..', '.git'} for part in relative.split('/')):
            raise ValueError('Unsafe archive path')
        key = repository, relative
        if key in seen:
            raise ValueError('Duplicate archive record')
        seen.add(key)
        root = ROOT / 'records' / repository
        target = root / relative
        if not target.resolve().is_relative_to(root.resolve()) or target.is_symlink():
            raise ValueError('Archive path escaped')
        if hashlib.sha256(target.read_bytes()).hexdigest() != entry['sha256']:
            raise ValueError(f'Changed archive: {repository}/{relative}')
    print(f'PASS: {len(seen)} preserved records; historical link semantics unchanged')


if __name__ == '__main__':
    main()
