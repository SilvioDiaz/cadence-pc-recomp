# MUA3 port: estado e plano

Port por recompilação estática de Marvel Ultimate Alliance 3 (Switch) para Windows x86-64, usando este fork do
TotK recomp como base. Uso pessoal, a partir de um dump do próprio console.

## Layout

- `D:\Games\Marvel Ultimate Alliance 3\mua3-recomp\`: este projeto (clone local do TotK recomp; remote `totk-upstream`).
- `D:\Games\Marvel Ultimate Alliance 3\refs\totk-pc-recomp\`, `refs\LASRecomp\`: cópias de referência, só leitura.
- `D:\Games\Marvel Ultimate Alliance 3\toolchain\`: Python gerenciado pelo uv e cache do uv.

## Ambiente (preparado em 2026-11-03)

- MSYS2 UCRT64 em `C:\msys64`: clang/lld 23.1.4, ninja, gcc, make, sdl3, opus, libvpx, zstd, vulkan-devel, VMA,
  validation layers, shaderc, spirv-tools.
- `.venv` (Python 3.12) e `.venv-py314` (Python 3.14) com `tools/requirements*.txt`.
- uv: o app do Claude virtualiza `%APPDATA%`, o que quebra os junctions do uv. Antes de usar `uv`, definir
  `UV_PYTHON_INSTALL_DIR=D:\Games\Marvel Ultimate Alliance 3\toolchain\uv-python` e
  `UV_CACHE_DIR=D:\Games\Marvel Ultimate Alliance 3\toolchain\uv-cache`.
- .NET SDK 10.0.101 já instalado.

## Pendente no ambiente

- `hactool`: `.venv\Scripts\python tools\build_hactool.py` (precisa ser rodado pelo usuário ou liberado nas permissões).
- Visual Studio Build Tools (C++ e Windows SDK): só para compilar o tradutor de shaders `totk_xlate.exe`.
- Opcional, para engenharia reversa: Ghidra + Ghidra-Switch-Loader + JDK 21.

## Dump

- Base `010060700AC50000` v0, update `010060700AC50800` v524288, DLC Expansion Pass (ainda não usado). NSZ em
  `D:\Games\Marvel Ultimate Alliance 3\`, convertidos para `build\unpacked\{base,update}.nsp` com `tools/ncz.py`.
- Módulos: main, sdk, subsdk0, subsdk1, rtld. O update só troca o `main` (11,5 MB -> 14,5 MB NSO).
- Hashes em `build\extracted\hashes.json`; `build\extracted\expected-upd.json` é o formato que `build_game.py` lê.

## Comandos (a partir de `mua3-recomp\`)

```
.venv-py314\Scripts\python -I tools\mua3_extract.py --base build\unpacked\base.nsp --update build\unpacked\update.nsp --keys "D:\Games\Marvel Ultimate Alliance 3\prod.keys"
.venv\Scripts\python recomp\gen.py --exefs build\extracted\upd\exefs --out generated\upd --modules main,subsdk0,subsdk1,sdk
.venv\Scripts\python tools\build_game.py --game mua3 --version upd --gen generated\upd --out build\upd --exefs build\extracted\upd\exefs --romfs build\extracted\upd\romfs --expected build\extracted\expected-upd.json
build\upd\totk.exe --selftest
```

`build_game.py` e `gen.py` não rodam com `python -I` (importam módulos irmãos).

## Estado (2026-11-03)

- Extração: ExeFS ok; RomFS base ok; merge do update em andamento.
- Lift: 104.614 funções, 567 MB de C, 0 instruções não suportadas, 250 s.
- Compilação: 569 objetos, 0 erros, 236 s. Link: `build\upd\totk.exe` (151,5 MB). `--selftest` passa.
- Runtime ainda é o do TotK sem nenhuma adaptação (patches, versão, gráficos).

## O que o MUA3 usa (log do Ryujinx 1.3.3, v4.0.1, boot até gameplay)

- Nome interno do programa: "Cube" (motor da Team Ninja). Guest log via `lm` (memory.cpp no boot).
- 3 núcleos (0 a 2), áudio `audren` REV6, `hid` com giroscópio e vibração, `vi` com 1 layer gerenciado.
- Módulos: `subsdk0` é a biblioteca `movie` da Nintendo (port do stagefright do Android, decodifica pelo NvDec via
  `mm:u`); `subsdk1` é o `glslc` (compilador de shaders NVN em tempo de execução); `sdk` exporta os 447 `nn::` que o
  `main` importa.
- Vídeos: 127 `.mp4` no RomFS (o TotK usa VP9 via libvpx). Vai precisar de decodificador H.264 no host.
- RomFS: formatos da Koei Tecmo (`.g1t`, `.kslt`, `.ktsl2asbin`, `.zl_`); o jogo decodifica tudo sozinho.
- Serviços vistos (CMIF): am/oe, acc (BAAS), aoc (DLC), fs (RomFS por `OpenDataStorageByCurrentProcess`, save),
  hid, nvdrv, vi + HOSBinder, time (relógio de rede), settings, pctl, friends, bcat, apm, mm, lm, audren, audout dev.
- SVCs vistas (27): todas comuns; conferir contra as 38 do runtime.
- `nn::` importados pelo main: 447, dos quais 62 o runtime do TotK já substitui. Faltam sobretudo socket, ldn, bcat,
  nifm, friends, err, ssl (online, podem virar "sem rede"), e partes de os, audio, hid, account, vi, time.

## Rodada de adaptação 1 (2026-11-03)

Primeira execução: parou no boot, `nn::init::Start` do SDK do MUA3 tem 2 callbacks (`_ZN2nn4init5StartEmmPFvvES2_`).
Mudanças no runtime, todas atrás de `--game mua3` (`RT_MUA3`, `rt_game_mua3` em modules.c) ou por nome de símbolo:

- `boot.c`: aceita `nn::init::Start` de 2 callbacks; DT_INIT de todos os módulos sem contagens do TotK; checkpoints
  só registram o chamador.
- `frame_rate.c` (posição do jogador do TotK) e `resolution.c` (patch page do TotK): desligados no MUA3.
- `RT_PROGRAM_ID` (host.h): `svc.c` GetInfo e `fs_host.c` save_exists usam o id do MUA3.
- `ov_offline.c` (novo): nifm, socket, ldn, bcat, friends, nsd, ssl, ec, err::ShowError(variant) respondem offline.
- `ov_input.c`: formas antigas do hid (`GetNpadState`, sem `detail::`).
- `fs_host.c`: `CommitSaveData`, `GetDirectoryEntryCount`, `MountAddOnContent` (sem DLC), cache de DLC.
- `ov_system.c`: `OpenPreselectedUser`, conta de rede offline, `AsyncContext`, aoc (0 DLC, evento),
  `oe::GetDisplayVersion` ("4.0.1"), relógio de rede, `detail::UnexpectedDefaultImpl` (fatal com mensagem).
- `ov_gfx.c`: `vi` Close/Destroy/Finalize, `nv::FinalizeGraphics`, `SetLayerScalingMode`.
- `ipc.c`: `TOTK_IPC_SOFT=1` responde "não registrado" a serviços desconhecidos em vez de parar.

Ainda não feito: vídeo (`movie`/`mm`, H.264), `glslc` em tempo de execução, DLC de verdade, `swkbd` do SDK antigo.

## Rodada de adaptação 2 (2026-11-03): primeira imagem

Execuções 2 a 13. O jogo passa boot, constructors, nnMain, inicializa NVN/Vulkan, áudio (SDL), controle, conta e
save, e aos ~45 s de jogo mostra o logo da Marvel (`build\upd\shot13.png`). Mudanças:

- `fs_host.c`: `SetAllocator` (o do SDK antigo abre fsp-srv).
- `ov_system.c`: `settings::LanguageCode::Make` (tabela fixa).
- `ov_offline.c`: `crypto::GenerateCryptographicallyRandomBytes` (plat_random), `~DeliveryCacheFile`.
- NVN: `nvnQueueWaitSync` (ordem de submit), `nvnQueueAcquireTexture`, `nvnDeviceApplyDeferredFinalizes` (novas
  linhas no fim de `nvn_procs.inc`), `nvnCommandBufferSetCopyImageStride` (`p_copy_stride.image`),
  `nvnTexturePoolRegisterImage` (= RegisterTexture).
- `vk_exec_draw.c`: **programa por estágio** (`stage_prog[6]`, `prog_of`). O MUA3 cria um programa por estágio e
  liga VS e FS separados; antes só o último ficava e todo draw era descartado (tela preta).
- Tradutor de shaders compilado (`build\xlate\totk_xlate.exe`; VS Build Tools 2022/18 já estavam instalados).

Ferramentas úteis: `TOTK_SHOTS=w0-45:3 TOTK_SHOTS_DIR=dir` (prints por segundo de jogo), `--seconds S --shot f.png`,
`TOTK_DUMP=<frame>` (passes.txt), `TOTK_TRACE=fs|gfx`. Análises em scratchpad: svc_reach.py (imports que chegam a
GetServiceHandle), nvn_gap.py.

## Próximos marcos

1. Carregamento de ~30 s com o ícone girando antes do logo: medir se é normal ou espera de algo (vídeo/mm?).
2. Passar dos logos até o título; vídeos (`movie`/`mm`, H.264) devem aparecer aí.
2. Logs de um emulador derivado do Ryujinx (serviços e stubs usados pelo MUA3) como roteiro do runtime.
3. Tirar do caminho do MUA3 o que é específico do TotK no runtime (patches por endereço, tabelas de versão).
4. Implementar as funções `nn::*`, serviços e SVCs que faltarem até o primeiro boot.
