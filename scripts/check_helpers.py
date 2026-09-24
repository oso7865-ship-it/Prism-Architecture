#!/usr/bin/env python3
"""Reproduce documentation helper checks using only the standard library."""
from __future__ import annotations

import argparse
import copy
import json
from pathlib import Path

import context_select as selector
import validate_docs as validator

ROOT = Path(__file__).resolve().parents[1]


def require(condition: bool, message: str) -> None:
    if not condition:
        raise ValueError(message)


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--report', help='Repository-relative JSON output path')
    args = parser.parse_args()
    data = json.loads((ROOT / 'docs/architecture/context-map.json').read_text(encoding='utf-8'))
    texts = {p.relative_to(ROOT).as_posix(): p.read_text(encoding='utf-8')
             for p in ROOT.rglob('*.md')}
    require(not validator.validate_adrs(data, texts), 'Baseline ADR validation failed')
    cases = {
        'duplicate_id': lambda d: d['adr_records'].append(copy.deepcopy(d['adr_records'][0])),
        'unknown_area': lambda d: d['adr_records'][0].update(area='MISSING'),
        'missing_migration': lambda d: d['adr_records'][0].update(legacy_ids=[]),
        'missing_successor': lambda d: d['adr_records'][0].update(status='SUPERSEDED'),
        'self_replacement': lambda d: d['adr_records'][0].update(supersedes=[d['adr_records'][0]['id']]),
        'wrong_filename': lambda d: d['adr_records'][0].update(path='docs/architecture/adr/architecture/wrong.md'),
        'missing_route': lambda d: d.update(path_routes=[r for r in d['path_routes']
                                                        if r['prefix'] != 'docs/architecture/adr/review']),
    }
    for name, mutate in cases.items():
        changed = copy.deepcopy(data)
        mutate(changed)
        require(bool(validator.validate_adrs(changed, texts)), 'Not rejected: ' + name)
    for task in data['tasks']:
        for mode in ('read', 'edit'):
            result = selector.select_context(data, [task], [], mode)
            require(result['selected_document_count'] > 0, 'Empty context: ' + task)
    for record in data['adr_records']:
        result = selector.select_context(data, [], [record['path']], 'read')
        paths = {entry['path'] for entry in result['documents']}
        require(record['path'] in paths, 'Missing ADR: ' + record['id'])
        for other in data['adr_records']:
            if other['area'] != record['area']:
                require(other['path'] not in paths, 'Unrelated ADR: ' + other['id'])
    for route in data['path_routes']:
        require(selector.route_path(route['prefix'], data['path_routes']) == route['task'],
                'Wrong route: ' + route['prefix'])
    invalid_paths = ['../secret', '/absolute/path', 'C:/secret', 'unmapped/file.py']
    for path in invalid_paths:
        try:
            selector.select_context(data, [], [path], 'read')
        except ValueError:
            pass
        else:
            raise ValueError('Unsafe or unknown path accepted: ' + path)
    report = {
        'status': 'PASS', 'scope': 'documentation_helpers_only',
        'task_mode_combinations': len(data['tasks']) * 2,
        'adr_path_routes': len(data['adr_records']),
        'path_routes': len(data['path_routes']),
        'negative_adr_checks': list(cases),
        'invalid_path_checks': len(invalid_paths),
        'not_verified': ['application implementation', 'live integrations'],
    }
    output = json.dumps(report, ensure_ascii=False, indent=2) + '\n'
    if args.report:
        destination = (ROOT / args.report).resolve()
        if not destination.is_relative_to(ROOT) or destination.suffix.lower() != '.json':
            raise ValueError('Report must be a repository-local .json file')
        destination.write_text(output, encoding='utf-8')
    print(output, end='')
    return 0


if __name__ == '__main__':
    raise SystemExit(main())
