"""Stage manifest-listed local files without including pack data in the repo.

Manifest is JSON: {"files": [{"source": "pack/path.pdf", "destination":
"letters/hold.pdf", "sha256": "optional expected hash"}]}. No glob expansion.
"""
import argparse
import hashlib
import json
import re
import shutil
import tempfile
from pathlib import Path
try:
    from .eval_provenance import tree_hash, digest
except ImportError:
    from eval_provenance import tree_hash, digest

ROOT = Path(__file__).resolve().parents[1]

def inside(root, name):
    path = Path(name)
    if not name or path.is_absolute() or '..' in path.parts or '\\' in name:
        raise ValueError(f'Unsafe manifest path: {name!r}')
    target = (root/path).resolve()
    target.relative_to(root.resolve())
    return target


def check_cutoff(manifest):
    """Forecast manifests name a cutoff submission; refuse any later source.

    The sequence is the first four-digit folder in the source path (eCTD layout),
    so a manifest cannot stage the held-back filing, or anything filed after the
    cutoff, by mistake. Sources without a sequence folder are refused too.
    """
    cutoff = manifest.get('cutoff_sequence')
    if cutoff is None:
        return
    if not re.fullmatch(r'\d{4}', str(cutoff)):
        raise ValueError('cutoff_sequence must be a four-digit sequence')
    for entry in manifest['files']:
        sequence = next((part for part in Path(entry['source']).parts if re.fullmatch(r'\d{4}', part)), None)
        if sequence is None or sequence > cutoff:
            raise ValueError(f'Source is not at or before cutoff {cutoff}: {entry["source"]}')


def stage(task, pack_root, destination=None):
    task, pack_root = Path(task), Path(pack_root).resolve()
    manifest = json.loads((task/'workspace.manifest').read_text())
    entries = manifest['files']
    if not isinstance(entries, list) or not entries:
        raise ValueError('Manifest must list at least one file')
    check_cutoff(manifest)
    dest = Path(destination) if destination else task/'environment/workspace'
    dest.parent.mkdir(parents=True, exist_ok=True)
    planned, seen = [], set()
    for entry in entries:
        name = entry['source']
        if name.startswith('public:'):
            name = name.removeprefix('public:')
            source = inside(ROOT/'public', name)
            name = 'public/' + name
        else:
            source = inside(pack_root, name)
        relative = Path(entry.get('destination', name)).as_posix()
        inside(dest.resolve(), relative)
        if relative in seen or not source.is_file():
            raise ValueError('Duplicate destination or missing source in manifest')
        seen.add(relative)
        file_digest = hashlib.sha256(source.read_bytes()).hexdigest()
        if entry.get('sha256') and entry['sha256'] != file_digest:
            raise ValueError(f'Hash mismatch: {entry["source"]}')
        planned.append((source, relative))
    # Validate the full manifest first; replace stale workspaces only on success.
    with tempfile.TemporaryDirectory(prefix='stage-', dir=dest.parent) as tmp:
        staged = Path(tmp)/'workspace'; staged.mkdir()
        for source, relative in planned:
            target = staged/relative
            target.parent.mkdir(parents=True, exist_ok=True)
            shutil.copyfile(source, target)
        if dest.is_symlink():
            raise ValueError('Workspace destination cannot be a symlink')
        if dest.exists():
            shutil.rmtree(dest)
        shutil.move(str(staged), str(dest))
    workspace_hash, files = tree_hash(dest)
    receipt = {'manifest_sha256': digest(task/'workspace.manifest'),
               'workspace_sha256': workspace_hash, 'files': files,
               'note': 'Hashes describe staged bytes, not scientific correctness'}
    (dest.parent/'workspace.receipt.json').write_text(json.dumps(receipt, indent=2)+'\n')
    return len(planned)


if __name__ == '__main__':
    ap = argparse.ArgumentParser(description=__doc__)
    ap.add_argument('--pack-root', type=Path, required=True)
    ap.add_argument('--task', type=Path, action='append', required=True)
    args = ap.parse_args()
    for task in args.task:
        print(f'Staged {stage(task, args.pack_root)} files into {task}/environment/workspace')
