"""Extract Marvel Ultimate Alliance 3 (base game and one update) into build/extracted.

The extraction code in tools/vendor/macnativegames and tools/extract.py only accepts the Tears of the Kingdom title
ids. This script keeps that code unchanged and swaps in program_nca_mua3, which picks the Program NCA of MUA3 instead,
then runs the same steps in-process:

1. ExeFS (code modules) of the base game  -> build/extracted/v0/exefs
2. Base RomFS, all six IVFC levels verified -> build/extracted/v0/romfs
3. ExeFS of the update                       -> build/extracted/upd/exefs
4. Update RomFS merged by hactool (BKTR)     -> build/extracted/upd/romfs

Nothing is compared with reference hashes yet: the SHA-256 of every extracted code module is written to
build/extracted/hashes.json, which later steps can pin. Inputs must be plain NSP or XCI (unpack an NSZ with
tools/ncz.py first). Runs under .venv-py314. Key values are read from the keys file and never printed.

usage: mua3_extract.py --base base.nsp --update update.nsp --keys prod.keys [--work build] [--skip-romfs]
"""
import argparse
import hashlib
import json
import os
import shutil
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(ROOT / 'tools' / 'vendor' / 'macnativegames'))
sys.path.insert(0, str(ROOT / 'tools'))
import extract_exefs  # noqa: E402
import extract_romfs  # noqa: E402
import extract  # noqa: E402

require = extract_exefs.require
BASE_TITLE = '010060700AC50000'
UPDATE_TITLE = '010060700AC50800'
EXEFS_CODE = ('main', 'sdk', 'rtld')


def program_nca_mua3(records, update=False):
    """The (record, header) of the one Program NCA in a MUA3 base game or update package.

    Same checks as extract_exefs.program_nca (MacNativeGames), with the MUA3 title ids. An update's Program NCA keeps
    the base title id; its Meta NCA carries the update id."""
    programs = [(r, h) for r, h in records if r['content_type'] == 0]
    if update:
        require(len(programs) == 1, 'Expected one update Program NCA; combined packages are unsupported')
        record, hdr = programs[0]
        require(record['title_id'] == BASE_TITLE, f'Update belongs to another game ({record["title_id"]})')
        require(any(hdr[0x400 + i * 512 + 4] == 4 for i in range(4)), 'Expected a BKTR update, not a base game')
        require(all(r['title_id'] in (BASE_TITLE, UPDATE_TITLE) for r, _ in records), 'Mixed-title update package')
        return record, hdr
    metadata = [r for r, _ in records if r['content_type'] == 1]
    require(len(metadata) <= 1 and all(r['title_id'] == BASE_TITLE for r in metadata),
            'Expected MUA3 base game metadata; updates, DLC and combined packages are unsupported')
    require(len(programs) == 1, 'Expected one base Program NCA')
    record, hdr = programs[0]
    require(record['title_id'] == BASE_TITLE, f'Expected the MUA3 base game {BASE_TITLE}, got {record["title_id"]}')
    return record, hdr


# extract_romfs and extract imported program_nca by name, so each module's binding is replaced.
for module in (extract_exefs, extract_romfs, extract):
    module.program_nca = program_nca_mua3


def run_vendor(main, argv):
    """Run a vendored script's main() in this process, so the replaced program_nca applies."""
    saved = sys.argv
    sys.argv = [main.__module__, *map(str, argv)]
    try:
        main()
    finally:
        sys.argv = saved


def sha256(path):
    with path.open('rb') as f:
        return hashlib.file_digest(f, 'sha256').hexdigest()


def exefs(game, keys, out, *, update):
    target = out / 'exefs'
    if target.exists():
        shutil.rmtree(target)
    out.mkdir(parents=True, exist_ok=True)
    run_vendor(extract_exefs.main, [game, '--keys', keys, '--output', target, *(['--update'] if update else [])])
    return target


def main():
    parser = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    parser.add_argument('--base', type=Path, required=True)
    parser.add_argument('--update', type=Path)
    parser.add_argument('--keys', type=Path, required=True)
    parser.add_argument('--work', type=Path, default=ROOT / 'build')
    parser.add_argument('--hactool', type=Path,
                        default=ROOT / 'toolchain' / 'hactool' / ('hactool.exe' if os.name == 'nt' else 'hactool'))
    parser.add_argument('--skip-romfs', action='store_true', help='extract only the code (ExeFS)')
    parser.add_argument('--title', help='base title id of another game (default 010060700AC50000, MUA3); its update '
                                        'is the same id with 0x800 added')
    args = parser.parse_args()
    if args.title:
        global BASE_TITLE, UPDATE_TITLE   # read by program_nca_mua3
        BASE_TITLE = args.title.upper()
        UPDATE_TITLE = f'{int(BASE_TITLE, 16) + 0x800:016X}'
    extracted, logs = args.work / 'extracted', args.work / 'logs'
    logs.mkdir(parents=True, exist_ok=True)
    hashes = {}

    print('Base game: ExeFS', flush=True)
    base_exefs = exefs(args.base, args.keys, extracted / 'v0', update=False)
    hashes['v0'] = {p.name: sha256(p) for p in sorted(base_exefs.iterdir())}
    if not args.skip_romfs:
        print('Base game: RomFS', flush=True)
        romfs = extracted / 'v0' / 'romfs'
        if romfs.exists():
            shutil.rmtree(romfs)
        run_vendor(extract_romfs.main, ['--keys', args.keys, '--manifest', extracted / 'v0' / 'extraction-manifest.json',
                                        '--output', romfs])

    if args.update:
        print('Update: ExeFS', flush=True)
        upd_exefs = exefs(args.update, args.keys, extracted / 'upd', update=True)
        hashes['upd'] = {p.name: sha256(p) for p in sorted(upd_exefs.iterdir())}
        if not args.skip_romfs:
            print('Update: RomFS merge', flush=True)
            extract.merge_update_romfs(args.base, args.update, args.keys, args.hactool,
                                       extracted / 'upd' / 'romfs', logs)

    (extracted / 'hashes.json').write_text(json.dumps(hashes, indent=2) + '\n')
    for version, files in hashes.items():
        print(f'{version}: ' + ', '.join(f'{n} {d[:12]}' for n, d in files.items() if n in EXEFS_CODE or 'subsdk' in n))


if __name__ == '__main__':
    try:
        main()
    except ValueError as error:
        sys.exit(f'error: {error}')
