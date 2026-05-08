Analise completamente o projeto IPTV atual antes de modificar qualquer coisa.

Objetivo:
Transformar o sistema atual em uma estrutura IPTV organizada e compatível com players modernos, utilizando apenas playlists M3U funcionais via GitHub Pages.

IMPORTANTE:
Hoje o sistema separa arquivos fisicamente, mas os players IPTV não navegam diretórios GitHub como pastas. Eles dependem da metadata M3U (#EXTINF, group-title, tvg-id, tvg-logo, etc).

O sistema precisa deixar de pensar como filesystem e passar a funcionar como catálogo IPTV real.

========================
ESTRUTURA PRINCIPAL
===================

Corrigir:

* index.m3u
* output/index.m3u

Eles DEVEM conter:

* streams reais
* URLs reais
* metadata correta
* categorias funcionais

NÃO usar:

* links relativos
* subplaylists como stream
* channels/espn.m3u dentro do index

Formato correto:

#EXTM3U

#EXTINF:-1 tvg-id="espn.br" tvg-logo="..." group-title="Sports | ESPN",ESPN HD
https://stream.m3u8

========================
ORGANIZAÇÃO DE TV AO VIVO
=========================

Separar canais por:

* categoria
* emissora
* qualidade

Exemplos obrigatórios:

Canais Abertos:

* Globo
* SBT
* Record
* Band
* RedeTV

Esportes:

* ESPN
* SporTV
* Premiere
* Combate
* Bandsports

Filmes e séries:

* HBO
* Telecine
* Warner
* Paramount

Infantil:

* Cartoon Network
* Disney Channel
* Nickelodeon
* Discovery Kids

Documentários:

* Discovery
* History
* National Geographic

Notícias:

* CNN
* GloboNews
* Record News
* Band News

========================
SEPARAÇÃO POR EMISSORA
======================

Criar playlists específicas:

/output/channels/espn.m3u
/output/channels/sportv.m3u
/output/channels/globo.m3u
/output/channels/hbo.m3u
/output/channels/disney.m3u

Essas playlists DEVEM agrupar:

* SD
* HD
* FHD
* 4K
* canais alternativos

Exemplo:

ESPN SD
ESPN HD
ESPN FHD
ESPN 2
ESPN 3
ESPN 4

SporTV SD
SporTV HD
SporTV 2
SporTV 3

Globo SP
Globo RJ
Globo MG
Globo Nordeste

========================
SEPARAÇÃO DE FILMES
===================

Filmes NÃO podem aparecer em Live TV.

Separar automaticamente por gênero:

* Action
* Comedy
* Horror
* Drama
* Documentary
* Anime
* Thriller
* Sci-Fi
* Family
* Kids
* Romance
* Launches

Criar playlists:

/output/movies/action.m3u
/output/movies/comedy.m3u
/output/movies/launches.m3u

Detectar automaticamente:

* BluRay
* WEB-DL
* 1080p
* 4K
* Movie
* MKV
* MP4

========================
SEPARAÇÃO DE SÉRIES
===================

Separar séries corretamente.

Detectar:

* S01E01
* Season
* Episode
* Temporada
* Capítulo

Separar por plataforma:

* Netflix
* Prime Video
* HBO Max
* Apple TV+
* Disney+
* Paramount+
* Crunchyroll

Criar playlists:

/output/series/netflix.m3u
/output/series/prime_video.m3u
/output/series/hbo.m3u
/output/series/anime.m3u

========================
GROUP-TITLE
===========

Os players IPTV organizam tudo via:

* group-title

Padronizar group-title.

Exemplos:

group-title="Sports | ESPN"
group-title="Sports | SporTV"
group-title="Open TV | Globo"
group-title="Movies | Action"
group-title="Series | Netflix"

========================
METADATA
========

Adicionar quando possível:

* tvg-id
* tvg-logo
* tvg-name
* group-title

Remover completamente:

* IgorBifano
* scared_core

Substituir por:

* Private IPTV
  ou
* Family Media

========================
PARSER
======

Revisar:

* scripts/merge_lists.py
* scripts/iptv_core.py

Melhorar heurísticas para:

* live TV
* movies
* series
* categories
* quality detection
* platform detection
* duplicate removal

========================
OUTPUT FINAL
============

Gerar:

/index.m3u
/output/index.m3u

/output/live/index.m3u
/output/movies/index.m3u
/output/series/index.m3u

/output/channels/
/output/categories/
/output/countries/

Todos os arquivos DEVEM conter streams reais.

========================
COMPATIBILIDADE
===============

Garantir compatibilidade com:

* IPTV Smarters
* TiviMate
* OTT Navigator
* VLC
* Kodi

========================
VALIDAÇÃO FINAL
===============

Explicar:

* por que a versão anterior não funcionava
* como players IPTV interpretam group-title
* como o parser agora classifica conteúdos
* como live TV, movies e series foram separados
* como emissoras específicas agora agrupam SD/HD/FHD corretamente
