"""Extract a game's add-on content (DLC) packages into DIR/<index>/, one folder of plain files per DLC.

The runtime (fs_host.c) lists the folders under dlc/ as the installed add-on content and mounts DIR/<index> read-only
for nn::fs::MountAddOnContent. The index is the add-on content's title id minus the base title id's add-on base
(base | 0x1000): 01000B900D8B1003 is index 3 of 01000B900D8B0000.

Each NSP holds one data NCA (content type 5, PublicData; 4 is accepted too) with a RomFS, its Meta NCA and, when rights-managed, a common ticket.
The RomFS is decrypted with the vendored MacNativeGames code, which verifies the FS header and all six IVFC levels.
Inputs must be plain NSP (unpack an NSZ with tools/ncz.py first). Runs under .venv-py314.

usage: extract_dlc.py --base-title 01000B900D8B0000 --keys prod.keys --out DIR dlc1.nsp [dlc2.nsp ...]
"""
import argparse
import json
import shutil
import sys
import tempfile
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(ROOT / 'tools' / 'vendor' / 'macnativegames'))
from extract_exefs import (container_entries, nca_inventory, common_tickets, load_keys, read_at,  # noqa: E402
                           require)
from extract_romfs import index_romfs  # noqa: E402
from extract_shared_fonts import Slice, nca_romfs  # noqa: E402

CONTENT_DATA = (4, 5)   # Data, PublicData (what add-on content uses)


def aoc_index(title_id, base_title):
    tid, base = int(title_id, 16), int(base_title, 16)
    aoc_base = (base & ~0xfff) + 0x1000
    require(aoc_base < tid <= aoc_base + 0x7ff, f'{title_id} is not add-on content of {base_title}')
    return tid - aoc_base


def extract_one(nsp, base_title, keys, out):
    """Write nsp's DLC files to out/<index>; return (index, title id, file count, bytes)."""
    with nsp.open('rb') as f:
        kind, entries = container_entries(f, nsp.stat().st_size)
        require(kind == 'nsp', f'{nsp.name}: expected an NSP')
        data = [(r, h) for r, h in nca_inventory(f, entries, keys) if r["content_type"] in CONTENT_DATA]
        require(len(data) == 1, f'{nsp.name}: expected one Data NCA, found {len(data)}')
        tickets = common_tickets(f, entries)
    record, _ = data[0]
    index = aoc_index(record['title_id'], base_title)
    target = out / str(index)
    if target.exists():
        shutil.rmtree(target)
    with tempfile.TemporaryDirectory(dir=out) as tmp:
        image = Path(tmp) / 'romfs.bin'
        nca_romfs(Slice(nsp, record['nca_offset']), keys, image, tickets)
        files = index_romfs(image)
        staging = Path(tmp) / 'files'
        total = 0
        with image.open('rb') as src:
            for e in files:
                dst = staging / e['path']
                dst.parent.mkdir(parents=True, exist_ok=True)
                dst.write_bytes(read_at(src, e['offset'], e['size']))
                total += e['size']
        staging.mkdir(exist_ok=True)   # a DLC with no files is still installed
        staging.rename(target)
    return index, record['title_id'], len(files), total


def main():
    parser = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    parser.add_argument('--base-title', required=True, help='base game title id, e.g. 01000B900D8B0000')
    parser.add_argument('--keys', type=Path, required=True)
    parser.add_argument('--out', type=Path, required=True)
    parser.add_argument('nsp', type=Path, nargs='+')
    args = parser.parse_args()
    keys = load_keys(args.keys)
    args.out.mkdir(parents=True, exist_ok=True)
    report = []
    for nsp in args.nsp:
        index, tid, count, size = extract_one(nsp, args.base_title, keys, args.out)
        report.append(dict(index=index, title_id=tid, files=count, bytes=size, source=nsp.name))
        print(f'dlc {index}: {tid}, {count} files, {size} bytes', flush=True)
    (args.out / 'dlc.json').write_text(json.dumps(sorted(report, key=lambda r: r['index']), indent=2) + '\n')


if __name__ == '__main__':
    main()
