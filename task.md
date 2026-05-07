A estrutura atual ainda trata tudo como playlist simples.

Precisamos transformar o sistema em uma estrutura IPTV/VOD real compatível com apps IPTV modernos.

Objetivo:

Separar completamente:
- TV ao vivo
- Filmes (VOD)
- Séries

Criar a seguinte arquitetura:

/output/live/
/output/movies/
/output/series/

Regras:

1. TV ao vivo:
- apenas canais lineares
- categorias:
  sports
  news
  kids
  entertainment
  documentaries
  regional

2. Movies:
- detectar automaticamente conteúdos VOD
- separar por gênero
- remover canais live

3. Series:
- detectar automaticamente episódios
- identificar padrões:
  S01E01
  season
  episode
  temporada
- separar séries corretamente

4. Corrigir a classificação atual:
- filmes não podem aparecer em Live TV
- séries não podem aparecer em canais
- canais lineares não podem aparecer em movies

5. Gerar playlists independentes:
- /output/live/index.m3u
- /output/movies/index.m3u
- /output/series/index.m3u

6. Criar categorias compatíveis com apps IPTV:
- TiviMate
- IPTV Smarters
- OTT Navigator

7. Melhorar heurísticas de parsing e classificação.

8. Explicar como o parser atual classifica conteúdo e por que está misturando tipos.