#!/usr/bin/env python3
"""Validate this documentation package, not application behavior or security.

Checks local Markdown links/anchors, code fence balance, unique document IDs,
context-map references and path routes, and the 38 planned rule IDs.
"""
from __future__ import annotations

import argparse
import json
import re
import sys
from pathlib import Path
from urllib.parse import unquote

ROOT = Path(__file__).resolve().parents[1]
MAP_PATH = ROOT / 'docs/architecture/context-map.json'
LINK = re.compile(r'(?<!!)\[[^\]\n]+\]\(([^)\s]+)(?:\s+"[^"]*")?\)')
DOC_ID = re.compile(r'> ID: `([^`]+)`')
RULE_ID = re.compile(r'^\| ((?:COM|JAVA|PY|JS|TS)-\d{3}) \|', re.MULTILINE)


def without_fences(text: str) -> tuple[str, bool]:
    outside: list[str] = []
    in_fence = False
    for line in text.splitlines():
        if line.lstrip().startswith('```'):
            in_fence = not in_fence
            continue
        if not in_fence:
            outside.append(line)
    return '\n'.join(outside), not in_fence


def heading_anchors(text: str) -> set[str]:
    outside, _ = without_fences(text)
    result: set[str] = set()
    for line in outside.splitlines():
        if re.match(r'^#{1,6}\s+', line):
            label = re.sub(r'^#{1,6}\s+', '', line).strip().rstrip('#').strip()
            label = re.sub(r'[`*_]', '', label).lower()
            label = re.sub(r'[^\w\s-]', '', label)
            result.add(re.sub(r'\s', '-', label))
    result.update(re.findall(r'<a\s+(?:id|name)="([^"]+)"', text))
    return result


def validate_adrs(data: dict, texts: dict[str, str]) -> list[str]:
    """Check ADR registry, area routing, lifecycle and migration coverage."""
    errors: list[str] = []
    areas = data.get('adr_areas', {})
    records = data.get('adr_records', [])
    by_id = {r['id']: r for r in records}
    if len(by_id) != len(records):
        errors.append('중복 ADR ID')
    statuses = {'PROPOSED', 'ACCEPTED', 'BASELINE', 'REJECTED', 'SUPERSEDED'}
    registered = {r['path'] for r in records}
    actual: set[str] = set()
    for path, text in texts.items():
        matches = DOC_ID.findall(text)
        if any(re.fullmatch(r'ADR-[A-Z]+-\d{3}', x) for x in matches):
            actual.add(path)
    if registered != actual:
        errors.append('ADR 파일/등록 목록 불일치')
    for area, config in areas.items():
        if config['owner_document'] not in texts:
            errors.append(f'{area}: ADR 소유 문서 없음')
        task = data['tasks'].get('adr-' + area.lower(), {})
        if not any(r['prefix'] == config['directory'] and r['task'] == 'adr-' + area.lower()
                   for r in data['path_routes']):
            errors.append(f'{area}: ADR 경로 매핑 없음')
        for record in (r for r in records if r['area'] == area):
            if record['path'] not in task.get('documents', []):
                errors.append(f'{record["id"]}: 영역 읽기 목록 누락')
    index = texts.get('docs/architecture/decisions/DECISIONS.md', '')
    for ident, record in by_id.items():
        area = record['area']
        if area not in areas or not re.fullmatch(r'ADR-' + re.escape(area) + r'-[0-9]{3}', ident) or ident.endswith('-000'):
            errors.append(f'{ident}: ADR 영역/번호 오류')
            continue
        path = record['path']
        if Path(path).parent.as_posix() != areas[area]['directory'] or not Path(path).name.startswith(ident + '-'):
            errors.append(f'{ident}: ADR 경로/파일명 오류')
        text = texts.get(path, '')
        if record['status'] not in statuses or f'- 상태: `{record["status"]}`' not in text:
            errors.append(f'{ident}: ADR 상태 불일치')
        for heading in ['배경', '결정', '대안', '영향과 한계', '소유 문서와 검증']:
            if f'## {heading}' not in text:
                errors.append(f'{ident}: 필수 항목 없음: {heading}')
        if f'[{ident}]' not in index:
            errors.append(f'{ident}: 결정 맵 누락')
        if record['status'] == 'SUPERSEDED' and not record['superseded_by']:
            errors.append(f'{ident}: 대체 ADR 누락')
        if record['superseded_by'] and record['status'] != 'SUPERSEDED':
            errors.append(f'{ident}: 대체 상태 누락')
        for key, reverse in [('supersedes', 'superseded_by'), ('superseded_by', 'supersedes')]:
            for other in record[key]:
                if other == ident or other not in by_id or ident not in by_id[other][reverse]:
                    errors.append(f'{ident}: 잘못된 대체 관계 {other}')
                if f'[{other}](' not in text:
                    errors.append(f'{ident}: 대체 ADR 문서 링크 누락 {other}')
    # A replacement cycle would make the current decision ambiguous.
    def visit(ident: str, stack: set[str]) -> None:
        if ident in stack:
            errors.append(f'{ident}: ADR 대체 순환')
            return
        for other in by_id[ident]['supersedes']:
            if other in by_id:
                visit(other, stack | {ident})
    for ident in by_id:
        visit(ident, set())
    migrated = {old for r in records for old in r['legacy_ids']}
    expected = {f'D-{n:03d}' for n in range(1, 13)} | {f'C-{n:03d}' for n in range(1, 8)}
    if not expected <= migrated:
        errors.append('기존 D/C 결정의 ADR 이관 누락')
    return errors


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--report', help='패키지 내부 JSON 보고서 상대 경로')
    args = parser.parse_args()
    errors: list[str] = []
    warnings: list[str] = []
    try:
        data = json.loads(MAP_PATH.read_text(encoding='utf-8'))
        markdown = sorted(ROOT.rglob('*.md'))
        text_by_path = {p.resolve(): p.read_text(encoding='utf-8') for p in markdown}
        ids: dict[str, str] = {}
        references = 0
        for path, text in text_by_path.items():
            rel = path.relative_to(ROOT).as_posix()
            if not text.startswith('# '):
                errors.append(f'{rel}: H1 제목 없음')
            outside, balanced = without_fences(text)
            if not balanced:
                errors.append(f'{rel}: code fence 미닫힘')
            if len(text) > 8000:
                warnings.append(f'{rel}: {len(text)}자, 필요 시 분할 검토(자동 실패 아님)')
            for doc_id in DOC_ID.findall(text):
                if doc_id in ids:
                    errors.append(f'중복 문서 ID {doc_id}: {ids[doc_id]} / {rel}')
                ids[doc_id] = rel
            for target in LINK.findall(outside):
                if re.match(r'^[a-zA-Z][a-zA-Z0-9+.-]*:', target):
                    continue
                references += 1
                path_part, _, anchor = unquote(target).partition('#')
                resolved = (path.parent / path_part).resolve() if path_part else path
                if not resolved.is_relative_to(ROOT):
                    errors.append(f'{rel}: 패키지 외부 상대 링크 {target}')
                elif not resolved.is_file():
                    errors.append(f'{rel}: 없는 상대 링크 {target}')
                elif anchor and resolved.suffix == '.md':
                    target_text = text_by_path.get(resolved) or resolved.read_text(encoding='utf-8')
                    if anchor not in heading_anchors(target_text):
                        errors.append(f'{rel}: 없는 heading anchor {target}')
        registered: set[str] = set()
        for entry in data['documents']:
            path = entry['path']
            if path in registered:
                errors.append(f'문서 경로 중복 등록: {path}')
            registered.add(path)
            if ids.get(entry['id']) != path:
                errors.append(f'문서 ID/경로 불일치: {entry["id"]} → {path}')
        expected_registry = {p.relative_to(ROOT).as_posix() for p in markdown
                             if p.relative_to(ROOT).as_posix().startswith('docs/architecture/')}
        for p in sorted(expected_registry - registered):
            errors.append(f'등록되지 않은 architecture 문서: {p}')
        for p in sorted(registered - expected_registry):
            errors.append(f'존재하지 않는 architecture 문서 등록: {p}')
        all_refs = list(data['base_documents']) + list(data['edit_documents'])
        for task_name, task in data['tasks'].items():
            if not task['documents']:
                errors.append(f'빈 작업 문서: {task_name}')
            all_refs.extend(task['documents'])
        for ref in all_refs:
            resolved = (ROOT/ref).resolve()
            if not resolved.is_relative_to(ROOT) or not resolved.is_file():
                errors.append(f'context-map의 잘못된 문서 경로: {ref}')
        prefixes: set[str] = set()
        for route in data['path_routes']:
            prefix = route['prefix']
            if prefix in prefixes:
                errors.append(f'중복 path route: {prefix}')
            prefixes.add(prefix)
            if route['task'] not in data['tasks']:
                errors.append(f'path route의 미등록 task: {route}')
        all_rules = [rid for p,t in text_by_path.items() if '/analysis/rules/' in p.as_posix()
                     for rid in RULE_ID.findall(t)]
        expected_rules = {f'{prefix}-{i:03d}' for prefix,n in [('COM',10),('JAVA',8),('PY',8),('JS',6),('TS',6)]
                          for i in range(1,n+1)}
        if len(all_rules) != len(set(all_rules)):
            errors.append('중복 Rule ID 존재')
        if set(all_rules) != expected_rules:
            errors.append(f'Rule 목록 불일치: missing={sorted(expected_rules-set(all_rules))}, extra={sorted(set(all_rules)-expected_rules)}')
        errors.extend(validate_adrs(data, {p.relative_to(ROOT).as_posix(): t for p, t in text_by_path.items()}))
        # Catch accidental untranslated drafting fragments in this Korean edition.
        for path,text in text_by_path.items():
            if re.search(r'[\u3040-\u30ff]', text):
                errors.append(f'{path.relative_to(ROOT)}: 검토되지 않은 일본어 문자')
        report = {
            'status':'PASS' if not errors else 'FAIL',
            'scope':'documentation_integrity_only',
            'markdown_files':len(markdown), 'registered_document_ids':len(ids),
            'local_links_checked':references, 'routing_tasks':len(data['tasks']),
            'path_routes':len(prefixes), 'planned_rule_ids':len(all_rules),
            'adr_records':len(data['adr_records']),
            'total_markdown_characters':sum(map(len,text_by_path.values())),
            'errors':errors, 'warnings':warnings,
            'not_verified':['application implementation','live GitHub/Render integration','runtime security','performance','model-specific token counts'],
        }
        if args.report:
            target = (ROOT/args.report).resolve()
            if not target.is_relative_to(ROOT) or target.suffix.lower() != '.json':
                raise ValueError('--report에는 패키지 내부 .json 경로를 사용하세요.')
            target.parent.mkdir(parents=True,exist_ok=True)
            target.write_text(json.dumps(report,ensure_ascii=False,indent=2)+'\n',encoding='utf-8')
        print(json.dumps(report,ensure_ascii=False,indent=2))
        return 0 if not errors else 1
    except (OSError,ValueError,KeyError,TypeError) as exc:
        print(f'검증 도구 오류: {exc}',file=sys.stderr)
        return 2


if __name__ == '__main__':
    raise SystemExit(main())
