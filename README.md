# Cadence of Hyrule Recomp

A static recompilation of *Cadence of Hyrule – Crypt of the NecroDancer Featuring The Legend of Zelda* (Nintendo Switch) into a native x86-64 Windows executable.

<a href="https://recomplauncher.com/game/cadence-pc-recomp"><picture><source media="(prefers-color-scheme: dark)" srcset="https://recomplauncher.com/assets/press/launcher/badge-light.svg"><img alt="Get it on RecompLauncher" src="https://recomplauncher.com/assets/press/launcher/badge-dark.svg" height="48"></picture></a>

> [!WARNING]
> **This project was made by AI.** Nearly all of the code, the porting work and this documentation were written by an AI coding agent (Claude Code, by Anthropic) at the repository owner's request; the owner tested the builds on their own PC.
>
> **It is based on [totk-pc-recomp](https://github.com/valentderah/totk-pc-recomp)** by Valiantsin Dzerakh (the *Tears of the Kingdom* recomp). The lifter, the runtime, the installer and almost everything else come from there; this repository only adapts it to another game. The original credits and licenses still apply (see [Credits](#credits)).
>
> **It is far from 100%.** The game starts, plays its movies and reaches gameplay, but it has had little testing: expect visual bugs, crashes, things that do not work and menu options that do nothing. There is no guarantee the game can be finished.

> [!IMPORTANT]
> **No game files are included.** You need your own copy of the game, dumped from your own console. Instructions for obtaining those files will not be provided.
>
> The game is built from your files on your machine, so the result contains the game. It is for your own use. Do not share the installed folder.

## What works (so far)

- Starts, shows the opening movies and reaches gameplay at 60 fps
- Shadows and the picture are the right way up
- Keyboard, mouse and gamepad (inherited from TotK Recomp)
- DLC (Character Pack, Melody Pack, Symphony of the Mask, Season Pass) from your own files
- In-game settings menu (F1) and performance overlay (F10); options that only made sense for TotK are hidden

## What does not work or is untested

- Only version **1.5.0** (base game 1.0.0 + the 1.5.0 update).
- Only **Windows** has been tested.
- TotK's mods, cheats, DLSS and shader preparation do not apply to this game.
- There may be stutter the first time each effect appears, because shaders are translated during play.
- Saves, long play sessions, local multiplayer and most of the game's areas have not been checked.

## Installing (Windows)

Requirements: Windows 10 or later, an x86-64 CPU with SSE4.2, a GPU with Vulkan 1.3, and about 12 GB free during setup.

You need:

- the base game (version 1.0.0) as NSP, XCI, NSZ or XCZ
- the 1.5.0 update as NSP or NSZ
- your console's `prod.keys`
- optional: your DLC as NSP or NSZ, in the base game's folder or a subfolder of it; the setup finds and installs them

Steps:

1. Download the `.zip` from [Releases](../../releases/latest) and unpack it.
2. Start `Cadence-Setup.exe`. If SmartScreen warns about an unsigned app, choose *More info*, then *Run anyway*.
3. Pick the game files, `prod.keys`, the language and an install folder, and press *Start*. The setup checks the files by hash, extracts them, turns the game's code into C and compiles everything with the compiler bundled in the package. This takes a few minutes and only needs to be done once.
4. Play `cadence.exe` from the install folder.

Settings are in the in-game menu (F1) and in `cadence.ini`.

## Building from source

The process is the same as in the original project ([docs/building.md](docs/building.md)), with `--game cadence` for `tools/build_game.py` and `--modules main,subsdk0,subsdk1,sdk` for `recomp/gen.py`. The game profile (title ids, versions, expected hashes) is in [tools/game_profile.py](tools/game_profile.py) and [tools/data/cadence](tools/data/cadence). The release package is built by `tools/make_release.py`.

Everything the build writes stays under `build\` and `generated\`, which git ignores. Run `tools/check_content.py` before every commit so that no game content enters the repository.

## Credits

- [totk-pc-recomp](https://github.com/valentderah/totk-pc-recomp) by Valiantsin Dzerakh: the base of this whole project
- The projects totk-pc-recomp builds on, listed with their licenses in [THIRD_PARTY_NOTICES.md](THIRD_PARTY_NOTICES.md): LAS Recomp, MacNativeGames, Ryujinx, deko3d, hactool, SDL 3, Dear ImGui, AMD FSR 1, Vulkan Memory Allocator, libopus, libvpx, Zstandard, Switchbrew and the Switch homebrew community

## License

The project's code is under the original project's [MIT License](LICENSE); third-party code keeps its own license ([THIRD_PARTY_NOTICES.md](THIRD_PARTY_NOTICES.md)). The license grants nothing for the game.

An independent, non-commercial fan project, not affiliated with or endorsed by Nintendo, Brace Yourself Games or Spike Chunsoft. *The Legend of Zelda*, *Cadence of Hyrule* and *Nintendo Switch* are trademarks of Nintendo; *Crypt of the NecroDancer* is a trademark of Brace Yourself Games.
