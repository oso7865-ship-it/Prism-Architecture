#!/usr/bin/env python3
"""Select a small architecture reading set; never concatenate source documents.

Python 3.10+, standard library only. All paths are relative to the package root.
Use --mode edit for code changes and repeat --task/--path to combine scopes.
"""
from __future__ import annotations

import argparse
import json
import sys
from pathlib import Path, PurePosixPath
from typing import Any

ROOT = Path(__file__).resolve().parents[1]
MAP_PATH = ROOT / 'docs/architecture/context-map.json'


def normalized_path(value: str) -> str:
    value = value.replace('\\', '/').strip()
    while value.startswith('./'):
        value = value[2:]
    p = PurePosixPath(value)
    if not value or p.is_absolute() or '..' in p.parts or ':' in value:
        raise ValueError(f'저장소 내부의 상대 경로를 사용하세요: {value!r}')
    return p.as_posix().rstrip('/')


def safe_file(relative_path: str) -> Path:
    path = (ROOT / normalized_path(relative_path)).resolve()
    if not path.is_relative_to(ROOT):
        raise ValueError(f'문서 경로가 패키지 밖을 가리킵니다: {relative_path}')
    if not path.is_file():
        raise ValueError(f'문서 파일이 없습니다: {relative_path}')
    return path


def route_path(value: str, routes: list[dict[str, str]]) -> str:
    path = normalized_path(value)
    matches = [r for r in routes if path == r['prefix']
               or path.startswith(r['prefix'].rstrip('/') + '/')]
    if not matches:
        raise ValueError(f'매핑되지 않은 경로입니다: {path}. --list로 작업을 선택하거나 context-map.json을 갱신하세요.')
    return max(matches, key=lambda r: len(r['prefix']))['task']


def select_context(data: dict[str, Any], tasks: list[str], paths: list[str],
                   mode: str) -> dict[str, Any]:
    task_names = list(dict.fromkeys(tasks + [route_path(p, data['path_routes']) for p in paths]))
    unknown = [t for t in task_names if t not in data['tasks']]
    if unknown:
        raise ValueError(f'알 수 없는 작업: {", ".join(unknown)}. --list를 확인하세요.')
    docs = list(data['base_documents'])
    if mode == 'edit':
        docs.extend(data['edit_documents'])
    for task in task_names:
        docs.extend(data['tasks'][task]['documents'])
    docs = list(dict.fromkeys(docs))
    entries = []
    for relative in docs:
        text = safe_file(relative).read_text(encoding='utf-8')
        entries.append({'path': relative, 'characters': len(text),
                        'lines': len(text.splitlines())})
    all_docs = list(ROOT.rglob('*.md'))
    return {
        'mode': mode, 'tasks': task_names, 'documents': entries,
        'selected_document_count': len(entries),
        'selected_characters': sum(d['characters'] for d in entries),
        'all_markdown_characters': sum(len(p.read_text(encoding='utf-8')) for p in all_docs),
        'note': '글자 수는 토큰 수가 아닙니다. 이미 읽은 불변 문서는 재전송하지 않아도 됩니다. 관련 계약을 바꾸면 그 소유 문서를 추가하세요.',
    }


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--task', action='append', default=[], help='작업 ID, 여러 번 지정 가능')
    parser.add_argument('--path', action='append', default=[], help='수정 코드 상대 경로, 여러 번 지정 가능')
    parser.add_argument('--mode', choices=['read', 'edit'], default='read')
    parser.add_argument('--list', action='store_true', help='사용할 수 있는 작업 보기')
    parser.add_argument('--json', action='store_true', help='기계 판독용 JSON 출력')
    args = parser.parse_args()
    try:
        data = json.loads(MAP_PATH.read_text(encoding='utf-8'))
        if args.list:
            for name, task in data['tasks'].items():
                print(f'{name:16} {task["description"]}')
            return 0
        if not args.task and not args.path:
            parser.error('--task 또는 --path를 지정하세요. 작업 목록은 --list입니다.')
        result = select_context(data, args.task, args.path, args.mode)
        if args.json:
            print(json.dumps(result, ensure_ascii=False, indent=2))
        else:
            print(f'작업: {", ".join(result["tasks"])} / 모드: {result["mode"]}')
            print('읽을 문서:')
            for item in result['documents']:
                print(f'  {item["path"]}  ({item["characters"]:,}자)')
            print(f'\n선택 {result["selected_document_count"]}개 / {result["selected_characters"]:,}자')
            print(f'전체 Markdown: {result["all_markdown_characters"]:,}자')
            print(result['note'])
        return 0
    except (OSError, ValueError, KeyError, TypeError) as exc:
        print(f'오류: {exc}', file=sys.stderr)
        return 1


if __name__ == '__main__':
    raise SystemExit(main())
