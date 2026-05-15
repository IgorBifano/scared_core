# IPTV System

Gera a playlist principal em `output/index.m3u` e playlists auxiliares em:

- `output/live/`
- `output/series/`
- `output/movies/`

## Regras

- A URL final de cada stream e preservada exatamente como veio na fonte
- O script pode ajustar apenas `group-title`, `tvg-name` e o atributo `type`
- `TV AO VIVO` nunca recebe categorias `SERIES` ou `FILMES`
- `SERIES` usa `type="series"`
- `FILMES` usa `type="movie"`

## Estrutura

- `playlists/source/`: fontes M3U
- `scripts/`: parser, classificacao e geracao
- `config/`: configuracoes auxiliares
- `output/index.m3u`: playlist principal
- `output/live/`, `output/series/`, `output/movies/`: playlists por categoria

## Execucao

```bash
python scripts/merge_lists.py
```

O processo limpa `output/` e recria toda a estrutura a partir das fontes em `playlists/source/`.
