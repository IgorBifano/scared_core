# IPTV System

Catálogo `Family Media` para consolidar playlists IPTV, integrar `plus.m3u`, remover entradas inválidas e gerar saídas organizadas por tipo de conteúdo, país, categoria e canal.

## Arquitetura Atual

Antes da refatoração, o projeto usava uma stack TypeScript herdada do `iptv-org`: parser em `scripts/core/playlistParser.ts`, merge e geração em `scripts/commands/playlist/generate.ts` e fontes em `streams/*.m3u`. As saídas eram publicadas em uma estrutura `.gh-pages/`, com forte acoplamento a workflows, testes e metadados do projeto upstream.

Agora o fluxo foi simplificado para um pipeline Python:

- `scripts/merge_lists.py`: orquestra leitura, merge, deduplicação e geração
- `scripts/iptv_core.py`: parser M3U, heurísticas de tipo de conteúdo, país, categoria/canal, normalização e serialização
- `playlists/`: fontes locais
- `output/`: artefatos finais para consumo direto

## Separação De Conteúdo

O parser agora separa explicitamente:

- `live`: canais lineares
- `movies`: VOD de filmes
- `series`: episódios e catálogos seriados

Saídas principais com streams diretos:

- `index.m3u`
- `output/index.m3u`
- `output/live/index.m3u`
- `output/movies/index.m3u`
- `output/series/index.m3u`

## Fluxo De Geração

1. O script lê `playlists/**/*.m3u`
2. Detecta `plus.m3u` automaticamente
3. Lê URLs opcionais de `config/sources.txt`
4. Faz parsing de `#EXTINF` + URL
5. Resolve primeiro o `content_type` (`live`, `movies`, `series`)
6. Normaliza `tvg-id`, `tvg-name`, `tvg-logo` e `group-title`
7. Remove entradas vazias, inválidas e duplicadas
8. Classifica live por categoria, movies por gênero e series por gênero
9. Classifica por país e canal/rede apenas quando fizer sentido
10. Gera `index.m3u`, `output/index.m3u`, `output/all_channels.m3u` e os recortes derivados

## Por Que A Versão Anterior Não Funcionava Bem

O problema principal não era só a classificação. O `index.m3u` principal era publicado como uma playlist de referências para outros arquivos `.m3u`, e não como uma playlist com streams reais. Players IPTV tratam cada item como algo reproduzível; eles não navegam a estrutura do GitHub Pages como se fosse um diretório.

Na classificação, o erro central era a ordem das decisões:

- antes ele tentava inferir `category` diretamente
- depois agrupava por nome de marca como `globo`, `disney`, `hbo`
- isso deixava VOD e episódios escaparem para playlists de canais lineares

Exemplo real:

- uma série com nome de rede ou uma novela 24h podia cair em `live` ou `channels`
- um filme com metadado fraco podia cair em `live` só porque não batia nas heurísticas de VOD

Agora a regra é:

1. decidir se a entrada é `live`, `movie` ou `series`
2. reescrever `group-title` para grupos consistentes que os players entendem
3. só então aplicar os agrupamentos específicos desse tipo

## Pontos Críticos E Gargalos

- `plus.m3u` é a maior fonte e domina o volume total
- checagem online de streams é cara e por isso ficou opcional
- classificação por país em listas VOD é naturalmente menos precisa
- listas de filmes/séries exigem heurísticas diferentes de canais lineares

## Estrutura

```text
iptv/
├── backup/                    # snapshot do projeto legado antes da limpeza
├── categories/                # playlists geradas por categoria
├── channels/                  # playlists geradas por canal conhecido
├── config/
│   └── sources.txt            # URLs extras opcionais
├── countries/                 # playlists geradas por país
├── kids/                      # atalho para categoria gerada
├── live/                      # atalho para categoria gerada
├── logos/                     # reservado para logos locais
├── movies/                    # atalho para categoria gerada
├── news/                      # atalho para categoria gerada
├── output/                    # saídas finais
├── playlists/
│   └── local/
│       └── legacy_streams/    # playlists herdadas do projeto anterior
├── scripts/
│   ├── iptv_core.py
│   └── merge_lists.py
├── series/                    # atalho para categoria gerada
├── sports/                    # atalho para categoria gerada
├── task.md
└── vod/                       # atalho para categoria gerada
```

## Fontes lidas pelo sistema

O script `scripts/merge_lists.py` lê:

1. Todas as playlists locais em `playlists/**/*.m3u`
2. `plus.m3u` na raiz do projeto ou um nível acima da raiz do repositório
3. URLs listadas em `config/sources.txt`

## Como executar

```bash
python scripts/merge_lists.py
```

Validação opcional de conectividade dos streams:

```bash
python scripts/merge_lists.py --check-streams --limit 500
```

Opções úteis:

```bash
python scripts/merge_lists.py --help
```

## Saídas geradas

- `index.m3u` (playlist principal com streams reais)
- `output/index.m3u` (espelho da playlist principal)
- `output/all_channels.m3u` (somente TV ao vivo)
- `output/live/*.m3u`
- `output/movies/*.m3u`
- `output/series/*.m3u`
- `output/countries/*.m3u` (somente TV ao vivo)
- `output/categories/*.m3u`
- `output/channels/*.m3u` (somente TV ao vivo)
- `output/channels/disney_channel.m3u`
- `countries/<pais>/playlist.m3u`
- `channels/<canal>/playlist.m3u`
- `sports/playlist.m3u`, `movies/playlist.m3u`, `series/playlist.m3u`, `kids/playlist.m3u`, `news/playlist.m3u`, `live/playlist.m3u`, `vod/playlist.m3u`
- `output/report.json`

## GitHub Pages

O `index.m3u` principal é utilizável diretamente em players IPTV:

```text
https://igorbifano.github.io/scared_core/index.m3u
```

Os recortes derivados continuam publicados sob:

```text
https://igorbifano.github.io/scared_core/output
```

Se a base pública dos recortes mudar:

```bash
python scripts/merge_lists.py --base-url https://seu-dominio/output
```

O workflow automático está em `.github/workflows/generate-playlists.yml`.

## Como adicionar novas listas

1. Coloque arquivos `.m3u` dentro de `playlists/`
2. Adicione URLs remotas em `config/sources.txt`, uma por linha
3. Atualize `plus.m3u` quando necessário
4. Rode `python scripts/merge_lists.py`

## Como atualizar playlists

- Substitua ou acrescente fontes em `playlists/`
- Edite `config/sources.txt`
- Rode novamente o script para reconstruir todos os recortes

## Observações

- A detecção de tipo, país e categoria é heurística, baseada em `name`, `group-title`, `tvg-id` e URL
- O script prioriza entradas da `plus.m3u` em conflitos de duplicidade
- A checagem de links offline é opcional porque pode ser lenta e depende de acesso de rede
- O `group-title` é o campo usado pelos players para montar grupos como `Sports`, `News`, `Movies`, `Netflix` e `Drama`
- O parser agora publica `group-title` composto quando faz sentido, como `Sports | ESPN`, `Open TV | Globo`, `Movies | Action` e `Series | HBO`
- Apps como TiviMate, IPTV Smarters, OTT Navigator, VLC e Kodi consomem diretamente `index.m3u`, `output/live/index.m3u`, `output/movies/index.m3u` e `output/series/index.m3u`
- Para manter os arquivos publicados menores, os recortes `all_channels`, `countries` e `channels` agora publicam apenas conteúdo linear live
