"""RecompLauncher's setup step (recomplauncher.json "prepare"): the command-line installer without a window.

    python -m installer.recomplauncher --prepare --game PATH --dest DIR [--keys FILE] [--lang CODE] [--root DIR]
                                       [--temp DIR]

--game is the player's copy: a folder holding the base game and the update, or one of the two files (the other is then
looked for beside it). --keys is prod.keys; without it the file is looked for in that folder, then in ~/.switch. The
language defaults to the one the install folder records, else en-US.

Runs the same steps as `python -m installer` (cli.py) on --dest and turns its JSON events into the lines the launcher
reads, `progress <0..1> <text>`, with the English text of installer/text/en.json. An error is one line on stderr.
Exit codes are cli.py's: 0 done, 1 failed, 2 bad command line, 3 cancelled. Nothing else starts this module: the setup
window and `python -m installer` are unchanged.
"""
import argparse
import json
import sys
from pathlib import Path

from . import cli
from . import state as statefile
from .events import load_catalog, render
from .runner import InstallError
from .steps import GAME, Check, load_keys, ncz

GAME_SUFFIXES = ('.nsp', '.nsz', '.xci', '.xcz')
DEFAULT_LANG = 'en-US'


class Problem(Exception):
    """The player's copy cannot be used as given; the text says why."""


def kind_of(path, keys):
    """'base' or 'update' for a game file of this game, None for anything else. The title id in the file name decides
    when it is there; else the file is opened with the keys as the check step does (a compressed file cannot be: an
    XCZ is a base game, an NSZ without a title id in its name is left to the caller)."""
    name = path.name.upper()
    if GAME['update_title'] in name:
        return 'update'
    if GAME['base_title'] in name:
        return 'base'
    if path.suffix.lower() in ('.xci', '.xcz'):
        return 'base'
    try:
        if ncz.compressed(path) is not None:
            return None
    except (ValueError, OSError):
        return None
    for kind, is_update in (('base', False), ('update', True)):
        try:
            with path.open('rb') as f:
                Check.open_input(f, path, keys, kind, is_update)
            return kind
        except (InstallError, OSError):
            continue
    return None


def find_keys(folder, given):
    """prod.keys: --keys, else in the game's folder, else ~/.switch/prod.keys."""
    if given:
        if not given.is_file():
            raise Problem(f'File not found (keys): {given}')
        return given
    for path in (folder / 'prod.keys', *sorted(folder.glob('*.keys')), Path.home() / '.switch' / 'prod.keys'):
        if path.is_file():
            return path
    raise Problem(f'prod.keys was not found. Put your console\'s prod.keys in {folder} and try again.')


def find_inputs(game, keys_path):
    """(base, update, keys) for --game, a folder or one of the two files."""
    game = game.resolve()
    if not game.exists():
        raise Problem(f'Not found: {game}')
    folder = game if game.is_dir() else game.parent
    keys_path = find_keys(folder, keys_path)
    try:
        keys = load_keys(keys_path)
    except (ValueError, OSError, UnicodeDecodeError):
        raise Problem(render(load_catalog(), 'check.keys_unreadable')) from None
    found = {'base': [], 'update': []}
    files = sorted(p for p in folder.iterdir() if p.is_file() and p.suffix.lower() in GAME_SUFFIXES)
    for path in files:
        kind = kind_of(path, keys)
        if kind:
            found[kind].append(path)
    del keys
    versions = ' / '.join(GAME['supported'])
    for kind, what in (('base', f'the base game ({GAME["base_version"]})'), ('update', f'the {versions} update')):
        if game.is_file() and game in found[kind]:
            found[kind] = [game]
        if not found[kind]:
            raise Problem(f'{what[0].upper()}{what[1:]} of {GAME["name"]} was not found in {folder}. The folder needs '
                          f'the base game (NSP, XCI, NSZ or XCZ) and the {versions} update (NSP or NSZ).')
        if len(found[kind]) > 1:
            names = ', '.join(p.name for p in found[kind])
            raise Problem(f'More than one file looks like {what} in {folder}: {names}. Keep only one there.')
    return found['base'][0], found['update'][0], keys_path


class Lines:
    """Stands in for stdout while cli.main runs: each JSON event becomes at most one launcher line on the real stdout."""

    def __init__(self, out, err):
        self.out, self.err, self.catalog = out, err, load_catalog()
        self.steps, self.index, self.buffer, self.last, self.high = [], 0, '', None, 0.0

    def write(self, text):
        self.buffer += text
        while '\n' in self.buffer:
            line, self.buffer = self.buffer.split('\n', 1)
            try:
                event = json.loads(line)
            except ValueError:
                continue
            if isinstance(event, dict):
                self.event(event)
        return len(text)

    def flush(self):
        self.out.flush()

    def say(self, fraction, text):
        # a step's phases each count from the step's start (hash, copy, merge, verify): the bar never goes back
        self.high = min(max(fraction, self.high), 1.0)
        line = f'progress {self.high:.3f} {text}'
        if line != self.last:
            self.last = line
            self.out.write(line + '\n')
            self.out.flush()

    def at(self, within=0.0):
        return (self.index + within) / max(len(self.steps), 1)

    def event(self, e):
        kind = e.get('type')
        if kind == 'start':
            self.steps = e.get('steps') or []
        elif kind == 'step':
            if e['step'] in self.steps:
                self.index = self.steps.index(e['step'])
            if e['state'] == 'started':
                self.say(self.at(), render(self.catalog, 'step.' + e['step']))
            else:
                self.index += 1
        elif kind == 'progress':
            total, done = e.get('total'), e.get('done')
            self.say(self.at(done / total if total and done is not None else 0.0),
                     render(self.catalog, f'phase.{e["step"]}.{e["phase"]}'))
        elif kind == 'error':
            self.err.write(render(self.catalog, e['id'], e.get('params')) + '\n')
            self.err.flush()
        elif kind == 'end' and e.get('result') == 'ok':
            self.say(1.0, 'Ready to play')


def main(argv=None):
    ap = argparse.ArgumentParser(prog='python -m installer.recomplauncher', description=__doc__.splitlines()[0])
    ap.add_argument('--prepare', action='store_true', help='accepted for the launcher; this module does nothing else')
    ap.add_argument('--game', type=Path, required=True, help='folder with the base game and the update, or one of them')
    ap.add_argument('--keys', type=Path, help='prod.keys (default: in the game folder, then ~/.switch/prod.keys)')
    ap.add_argument('--lang', help='game language, a Switch language code (default: the recorded one, else en-US)')
    ap.add_argument('--dest', type=Path, required=True, help='install folder')
    ap.add_argument('--root', type=Path, help='release folder or repository (default: the folder above installer/)')
    ap.add_argument('--temp', type=Path, help='temp folder (default: as python -m installer)')
    args = ap.parse_args(argv)

    out = sys.stdout
    lines = Lines(out, sys.stderr)
    lines.say(0.0, 'Looking for the game files')
    try:
        base, update, keys = find_inputs(args.game, args.keys)
    except Problem as e:
        print(e, file=sys.stderr, flush=True)
        return 1
    try:
        recorded = (statefile.load(args.dest.resolve()) or {}).get('lang')
    except statefile.StateError:
        recorded = None   # cli.main reports the unreadable file
    command = ['--base', str(base), '--update', str(update), '--keys', str(keys), '--dest', str(args.dest),
               '--lang', args.lang or recorded or DEFAULT_LANG]
    for name in ('root', 'temp'):
        if getattr(args, name):
            command += ['--' + name, str(getattr(args, name))]
    sys.stdout = lines
    try:
        return cli.main(command)
    finally:
        sys.stdout = out


if __name__ == '__main__':
    sys.exit(main())
