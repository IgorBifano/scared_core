# IPTV System

Projeto pessoal para consolidar playlists IPTV locais, integrar `plus.m3u`, remover entradas inválidas e gerar saídas organizadas por país, categoria e canal.

## Arquitetura Atual

Antes da refatoração, o projeto usava uma stack TypeScript herdada do `iptv-org`: parser em `scripts/core/playlistParser.ts`, merge e geração em `scripts/commands/playlist/generate.ts` e fontes em `streams/*.m3u`. As saídas eram publicadas em uma estrutura `.gh-pages/`, com forte acoplamento a workflows, testes e metadados do projeto upstream.

Agora o fluxo foi simplificado para um pipeline Python:

- `scripts/merge_lists.py`: orquestra leitura, merge, deduplicação e geração
- `scripts/iptv_core.py`: parser M3U, heurísticas de país/categoria/canal, normalização e serialização
- `playlists/`: fontes locais
- `output/`: artefatos finais para consumo direto

## Fluxo De Geração

1. O script lê `playlists/**/*.m3u`
2. Detecta `plus.m3u` automaticamente
3. Lê URLs opcionais de `config/sources.txt`
4. Faz parsing de `#EXTINF` + URL
5. Normaliza `tvg-id`, `tvg-name`, `tvg-logo` e `group-title`
6. Remove entradas vazias, inválidas e duplicadas
7. Classifica por país, categoria e canal/rede
8. Gera `output/all_channels.m3u`, `output/index.m3u` e os recortes derivados

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

- `output/all_channels.m3u`
- `output/index.m3u`
- `output/countries/*.m3u`
- `output/categories/*.m3u`
- `output/channels/*.m3u`
- `output/channels/disney_channel.m3u`
- `countries/<pais>/playlist.m3u`
- `channels/<canal>/playlist.m3u`
- `sports/playlist.m3u`, `movies/playlist.m3u`, `series/playlist.m3u`, `kids/playlist.m3u`, `news/playlist.m3u`, `live/playlist.m3u`, `vod/playlist.m3u`
- `output/report.json`

## GitHub Pages

O `index.m3u` principal é gerado com base pública padrão:

```text
https://igorbifano.github.io/scared_core/output
```

Se a URL pública mudar:

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

- A detecção de país e categoria é heurística, baseada em `name`, `group-title` e `tvg-id`
- O script prioriza entradas da `plus.m3u` em conflitos de duplicidade
- A checagem de links offline é opcional porque pode ser lenta e depende de acesso de rede
