# Cadence of Hyrule Recomp

Uma recompilação estática de *Cadence of Hyrule – Crypt of the NecroDancer Featuring The Legend of Zelda* (Nintendo Switch) para um executável nativo x86-64 do Windows.

> [!WARNING]
> **Este projeto foi feito por IA.** Praticamente todo o código, a adaptação e esta documentação foram escritos por um agente de IA (Claude Code, da Anthropic) a pedido do dono do repositório, que testou os builds no próprio PC.
>
> **Ele é baseado no [totk-pc-recomp](https://github.com/valentderah/totk-pc-recomp)** de Valiantsin Dzerakh (o recomp de *Tears of the Kingdom*). O lifter, o runtime, o instalador e quase tudo o mais vêm de lá; aqui só foi adaptado para outro jogo. Os créditos e licenças originais continuam valendo (veja [Créditos](#créditos)).
>
> **Está longe de estar 100%.** O jogo abre, roda os vídeos e chega no gameplay, mas foi pouco testado: espere bugs visuais, travamentos, partes que não funcionam e opções do menu que não fazem nada. Não há garantia de que dá para terminar o jogo.

> [!IMPORTANT]
> **Nenhum arquivo do jogo está incluído.** Você precisa da sua própria cópia do jogo, extraída do seu próprio console. Não serão dadas instruções de como obter esses arquivos.
>
> O jogo é montado a partir dos seus arquivos, na sua máquina, então o resultado contém o jogo. É para uso próprio. Não compartilhe a pasta instalada.

## O que funciona (até agora)

- Abre, mostra os vídeos de abertura e entra no gameplay a 60 fps
- Sombras e imagem na orientação certa
- Teclado, mouse e controle (herdado do TotK Recomp)
- Menu de configurações no jogo (F1) e overlay de desempenho (F10); opções que só faziam sentido no TotK foram escondidas

## O que não funciona ou não foi testado

- Só a versão **1.5.0** (jogo base 1.0.0 + atualização 1.5.0). DLCs não são suportadas.
- Só **Windows** foi testado.
- Mods, cheats, DLSS e a preparação de shaders do TotK não se aplicam a este jogo.
- Pode haver engasgos (stutter) na primeira vez que cada efeito aparece, porque os shaders são traduzidos durante o jogo.
- Save, progresso longo, multiplayer local e muitas áreas do jogo não foram verificados.

## Instalação (Windows)

Requisitos: Windows 10 ou mais novo, CPU x86-64 com SSE4.2, GPU com Vulkan 1.3, e cerca de 12 GB livres durante a instalação.

Você precisa de:

- o jogo base (versão 1.0.0) em NSP, XCI, NSZ ou XCZ
- a atualização 1.5.0 em NSP ou NSZ
- o `prod.keys` do seu console

Passos:

1. Baixe o `.zip` em [Releases](../../releases/latest) e extraia.
2. Abra o `Cadence-Setup.exe`. Se o SmartScreen avisar sobre app sem assinatura, clique em *Mais informações* e depois em *Executar assim mesmo*.
3. Escolha os arquivos do jogo, o `prod.keys`, o idioma e uma pasta de instalação e clique em *Iniciar*. O instalador confere os arquivos pelo hash, extrai, converte o código do jogo em C e compila tudo com o compilador que já vem no pacote. Isso leva um tempo e só precisa ser feito uma vez.
4. Jogue pelo `cadence.exe` na pasta de instalação.

As configurações ficam no menu do jogo (F1) e no `cadence.ini`.

## Compilando a partir do código

O processo é o mesmo do projeto original ([docs/building.md](docs/building.md)), com `--game cadence` no `tools/build_game.py` e `--modules main,subsdk0,subsdk1,sdk` no `recomp/gen.py`. O perfil do jogo (ids de título, versões, hashes esperados) fica em [tools/game_profile.py](tools/game_profile.py) e [tools/data/cadence](tools/data/cadence). O pacote de release é montado por `tools/make_release.py`.

Tudo que o build gera fica em `build\` e `generated\`, que o git ignora. Rode `tools/check_content.py` antes de cada commit para garantir que nenhum conteúdo do jogo entre no repositório.

## Créditos

- [totk-pc-recomp](https://github.com/valentderah/totk-pc-recomp), de Valiantsin Dzerakh: a base de todo este projeto
- Os projetos que o totk-pc-recomp usa, listados com suas licenças em [THIRD_PARTY_NOTICES.md](THIRD_PARTY_NOTICES.md): LAS Recomp, MacNativeGames, Ryujinx, deko3d, hactool, SDL 3, Dear ImGui, AMD FSR 1, Vulkan Memory Allocator, libopus, libvpx, Zstandard, Switchbrew e a comunidade homebrew do Switch

## Licença

O código do projeto está sob a [Licença MIT](LICENSE) do projeto original; código de terceiros mantém a própria licença ([THIRD_PARTY_NOTICES.md](THIRD_PARTY_NOTICES.md)). A licença não concede nenhum direito sobre o jogo.

Projeto de fã, independente e sem fins comerciais, sem ligação com a Nintendo, a Brace Yourself Games ou a Spike Chunsoft, nem endossado por elas. *The Legend of Zelda*, *Cadence of Hyrule* e *Nintendo Switch* são marcas da Nintendo; *Crypt of the NecroDancer* é marca da Brace Yourself Games.
