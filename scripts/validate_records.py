"""Check byte-preserved imported records separately from current architecture documents."""
import hashlib
import json
import re
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
    quality_root = ROOT / 'records/quality-evaluations'
    summary = json.loads((quality_root / 'quality-0929-summary.json').read_text(encoding='utf-8'))
    evaluated = set()
    for entry in summary['runs']:
        name, digest = entry['run'], entry['sha256']
        if not re.fullmatch(r'[a-z0-9-]+\.json', name) or name in evaluated:
            raise ValueError('Invalid or duplicate evaluation record')
        if not re.fullmatch(r'[a-f0-9]{64}', digest):
            raise ValueError('Invalid evaluation digest')
        target = quality_root / name
        if target.is_symlink() or target.resolve().parent != quality_root.resolve():
            raise ValueError('Evaluation path escaped')
        if hashlib.sha256(target.read_bytes()).hexdigest() != digest:
            raise ValueError(f'Changed evaluation: {name}')
        evaluated.add(name)
    print(f'PASS: {len(evaluated)} original evaluation result byte hashes')


if __name__ == '__main__':
    main()
