"""Content-address task definitions and visible files; no source text in receipts."""
import hashlib
import json
from pathlib import Path


def digest(path):
    return hashlib.sha256(Path(path).read_bytes()).hexdigest()


def tree_hash(root, exclude=()):
    root = Path(root)
    entries = {}
    if root.exists():
        for path in sorted(root.rglob('*')):
            if path.is_symlink():
                raise ValueError('Symlinks are not allowed in reproducible task trees')
            if path.is_file() and '__pycache__' not in path.parts and path.suffix != '.pyc':
                relative = path.relative_to(root).as_posix()
                if relative not in exclude:
                    entries[relative] = digest(path)
    encoded = json.dumps(entries, sort_keys=True, separators=(',', ':')).encode()
    return hashlib.sha256(encoded).hexdigest(), entries


def task_fingerprint(task):
    task = Path(task)
    definition = {}
    for name in ('task.toml', 'instruction.md', 'answer.schema.json', 'workspace.manifest'):
        if (task/name).exists(): definition[name] = digest(task/name)
    for section in ('tests', 'solution', 'environment'):
        for path in sorted((task/section).rglob('*')):
            if not path.is_file() or '__pycache__' in path.parts or 'workspace' in path.relative_to(task).parts:
                continue
            if path.is_symlink(): raise ValueError('Symlink in task definition')
            definition[path.relative_to(task).as_posix()] = digest(path)
    workspace_digest, files = tree_hash(task/'environment/workspace')
    content = {'definition': definition, 'workspace_sha256': workspace_digest, 'workspace_files': files}
    content['task_sha256'] = hashlib.sha256(json.dumps(content, sort_keys=True).encode()).hexdigest()
    return content
