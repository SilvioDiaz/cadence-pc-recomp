"""The game this checkout's installer and extraction build: title ids, supported versions, expected hashes and the
parts of the TotK pipeline the game uses. tools/build_game.py --game names the same games (its GAMES table holds the
runtime side). This repository builds Cadence of Hyrule; TOTK_GAME=totk selects the TotK profile.
"""
import os
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent

PROFILES = {
    'totk': {
        'game': 'totk',                       # build_game.py --game
        'name': 'TotK',
        'file': 'totk',                       # <file>.exe, <file>.ini, <file>-install.json
        'setup': 'TotK-Setup',                # the installer's executable and the release's name
        'base_title': '0100F2C0115B6000',
        'update_title': '0100F2C0115B6800',
        'data': ROOT / 'tools' / 'data',      # expected-v<display version>.json
        'base_version': '1.0.0',
        'supported': ('1.2.1', '1.4.3', '1.1.0'),
        'modules': 'main,subsdk0,sdk',
        'patches': True,                      # recomp/patches-v<version>.txt, cheats and ExeFS patches of mods
        'fonts': True,                        # the Switch shared fonts for Chinese and Korean text
        'prepare': True,                      # RomFS patches and the shader list (MacNativeGames)
        'dlss': True,                         # NVIDIA DLSS for the 3D scene (vk_dlaa.c)
        'dlc': False,                         # add-on content installed into dlc/ (fs_host.c mounts it)
    },
    'cadence': {
        'game': 'cadence',
        'name': 'Cadence of Hyrule',
        'file': 'cadence',
        'setup': 'Cadence-Setup',
        'base_title': '01000B900D8B0000',
        'update_title': '01000B900D8B0800',
        'data': ROOT / 'tools' / 'data' / 'cadence',
        'base_version': '1.0.0',
        'supported': ('1.5.0',),
        'modules': 'main,subsdk0,subsdk1,sdk',
        'patches': False,
        'fonts': False,
        'prepare': False,
        'dlss': False,
        'dlc': True,
    },
}

DEFAULT = 'cadence'
GAME = PROFILES[os.environ.get('TOTK_GAME', DEFAULT)]
