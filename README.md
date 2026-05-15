# IPTV System

Arquitetura limpa para gerar uma unica playlist IPTV em `output/index.m3u`.

## Estrutura

- `scripts/`: geracao, sanitizacao e validacao
- `playlists/source/`: fontes M3U mantidas no repositorio
- `config/sources.txt`: reservado para futuras fontes publicas
- `output/index.m3u`: playlist final unica
- `output/report.json`: relatorio de validacao
- `.github/workflows/`: workflows necessarios

## Regras

- O catalogo final usa apenas `group-title`
- Prefixos obrigatorios:
  - `TV AO VIVO | Categoria`
  - `SERIES | Categoria`
  - `FILMES | Categoria`
- Entradas com usuario, senha, token ou URLs privadas sao descartadas

## Execucao

```bash
python scripts/merge_lists.py
```

O script:

1. Migra uma base publica inicial para `playlists/source/` se a pasta estiver vazia
2. Reclassifica item por item
3. Gera `output/index.m3u`
4. Gera `output/report.json`
5. Exibe contagem de categorias e inconsistencias no terminal
