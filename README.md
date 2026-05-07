# IPTV System

Projeto pessoal para consolidar playlists IPTV locais, integrar `plus.m3u`, remover entradas inválidas e gerar saídas organizadas por país, categoria e canal.

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
- `output/countries/*.m3u`
- `output/categories/*.m3u`
- `output/channels/*.m3u`
- `countries/<pais>/playlist.m3u`
- `channels/<canal>/playlist.m3u`
- `sports/playlist.m3u`, `movies/playlist.m3u`, `series/playlist.m3u`, `kids/playlist.m3u`, `news/playlist.m3u`, `live/playlist.m3u`, `vod/playlist.m3u`
- `output/report.json`

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
