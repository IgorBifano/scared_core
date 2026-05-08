Analise completamente o projeto IPTV atual antes de modificar qualquer coisa.

Objetivo:
Transformar o sistema atual em uma estrutura IPTV organizada e compatível com players modernos, utilizando apenas playlists M3U funcionais via GitHub Pages.

IMPORTANTE:
Hoje o sistema separa arquivos fisicamente, mas os players IPTV não navegam diretórios GitHub como pastas. Eles dependem da metadata M3U (#EXTINF, group-title, tvg-id, tvg-logo, etc).

O sistema precisa deixar de pensar como filesystem e passar a funcionar como catálogo IPTV real.

REQUISITOS PRINCIPAIS

1. Corrigir o arquivo principal:

* output/index.m3u
* index.m3u

Eles DEVEM conter canais reais com URLs reais de stream.
NÃO podem conter referências para outras playlists como:

* channels/espn.m3u
* categories/sports.m3u

O index.m3u precisa funcionar diretamente em:

* IPTV Smarters
* TiviMate
* OTT Navigator
* VLC

Formato esperado:

#EXTM3U

#EXTINF:-1 tvg-id="espn.br" tvg-logo="..." group-title="Sports",ESPN
[https://stream.m3u8](https://stream.m3u8)

2. Corrigir a classificação do conteúdo

Separar corretamente:

* TV ao Vivo
* Filmes
* Séries

Regras:

LIVE TV:

* canais lineares
* streams contínuos
* ESPN
* SporTV
* Globo
* Discovery
* CNN
* Premiere
* HBO
* etc

MOVIES:

* filmes VOD
* detectar:
  1080p
  BluRay
  WEB-DL
  Movie
  títulos de filmes

SERIES:

* detectar:
  S01E01
  Season
  Episode
  Temporada
  Capítulo

3. Corrigir o uso de group-title

Os players IPTV organizam tudo pelo:

* group-title

Criar grupos consistentes:

TV ao Vivo:

* Sports
* News
* Entertainment
* Kids
* Movies
* Documentary
* Regional

Movies:

* Action
* Comedy
* Horror
* Anime
* Drama

Series:

* Netflix
* HBO
* Anime
* Sitcom
* Drama

4. Remover identificação pessoal

Remover completamente:

* IgorBifano
* scared_core

Verificar:

* #EXTM3U
* #PLAYLIST
* tvg-name
* metadata
* parser
* README
* outputs

Substituir por:

* Private IPTV
  ou
* Family Media

5. Melhorar heurísticas do parser

Revisar:

* scripts/merge_lists.py
* scripts/iptv_core.py

O parser deve:

* detectar live/vod/series
* detectar categorias automaticamente
* não misturar filmes com live TV
* não misturar séries com canais lineares

6. Gerar estrutura final

Gerar:

/index.m3u
/output/index.m3u

/output/live/index.m3u
/output/movies/index.m3u
/output/series/index.m3u

/output/channels/
/output/categories/
/output/countries/

Todos os arquivos devem conter streams reais e funcionais.

7. Compatibilidade

Garantir compatibilidade com:

* IPTV Smarters
* TiviMate
* OTT Navigator
* VLC
* Kodi

8. Validar a saída

Explicar:

* por que a versão anterior não funcionava
* o que foi corrigido
* como os players IPTV interpretam group-title
* como o sistema agora separa conteúdo corretamente

9. GitHub Pages

Garantir que os arquivos gerados funcionem diretamente via:

[https://igorbifano.github.io/scared_core/](https://igorbifano.github.io/scared_core/)

e que:
[https://igorbifano.github.io/scared_core/index.m3u](https://igorbifano.github.io/scared_core/index.m3u)

seja a playlist principal utilizável diretamente nos players IPTV.
