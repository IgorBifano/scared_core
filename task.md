Analise completamente o sistema IPTV atual antes de alterar qualquer arquivo.

O objetivo agora é reorganizar TODA a estrutura IPTV para funcionar como um catálogo IPTV profissional real, compatível com:

* IPTV Smarters
* TiviMate
* OTT Navigator
* Kodi
* VLC

IMPORTANTE:
Atualmente as categorias existem fisicamente, mas os conteúdos não aparecem corretamente dentro dos players IPTV.

O sistema precisa:

* usar corretamente group-title
* classificar streams reais
* gerar playlists funcionais
* separar TV ao vivo, séries e filmes corretamente
* garantir que os conteúdos apareçam dentro das categorias dos players

O sistema NÃO deve depender de navegação de diretórios GitHub.

==================================================
ESTRUTURA PRINCIPAL
===================

Corrigir:

* index.m3u
* output/index.m3u

Esses arquivos DEVEM conter:

* streams reais
* URLs reais
* metadata correta
* group-title correto

NÃO usar:

* playlists internas como stream
* caminhos relativos como:
  channels/espn.m3u

Formato correto:

#EXTINF:-1 tvg-id="espn.br" tvg-logo="..." group-title="TV AO VIVO | Canais ESPN",ESPN HD
https://stream.m3u8

==================================================
TV AO VIVO — CATEGORIAS OBRIGATÓRIAS
====================================

Separar os canais EXATAMENTE nessas categorias:

* Todos
* Canais Abertos
* Canais Internacionais
* Canais Documentarios
* Canais Filmes e Series
* Canais HBO
* Canais Telecine
* Canais Infantis
* Canais Noticias
* Canais Variedades
* Canais Religiosos
* Canais Premiere Clubes
* Canais Sportv
* Canais ESPN
* Canais Amazon Prime
* Canais Disney
* Canais Paramount
* Canais HBO MAX
* Canais TNT
* Canais Combate/UFC Fight
* Canais Nba League Pass
* Canais Apple TV
* Canais Cazé TV
* Canais DAZN
* Canais GE TV
* Canais GOAT
* Canais Nosso Futebol
* Canais NSPORTS
* Canais XSPORTS
* Canais 24h Animes
* Canais 24h Discovery
* Canais 24h Novelas
* Canais 24h Infantis
* Canais 24h Series de TV
* Canais Adultos

==================================================
REGRAS PARA TV AO VIVO
======================

Agrupar automaticamente:

* SD
* HD
* FHD
* 4K

Exemplo:

ESPN SD
ESPN HD
ESPN FHD
ESPN 2
ESPN 3
ESPN 4

SporTV HD
SporTV 2
SporTV 3

Globo SP
Globo RJ
Globo MG

Usar:
group-title="TV AO VIVO | Canais ESPN"

==================================================
SÉRIES — CATEGORIAS OBRIGATÓRIAS
================================

Separar EXATAMENTE nessas categorias:

* Todos
* ABC
* AMC+
* Apple TV
* BBC ONE
* Brasil Paralelo
* CW
* Discovery +
* Disney +
* GloboPlay
* HBO Max
* Hulu
* Lionsgate +
* Looke
* Netflix
* Paramount +
* PlayPlus
* Amazon Prime Video
* Starz
* Via Play
* Ação
* Animação/Infantil
* Animes
* Aventura
* Chicago Universe
* Comedia
* Crime
* Documentários
* Dorama
* Drama
* Ficção e Fantasia
* Faroeste
* Guerra
* Marvel
* Mini Séries
* Nacional
* Novelas
* Reality Shows
* Romance
* Suspense
* Terror
* Turcas
* Tv Show

==================================================
REGRAS PARA SÉRIES
==================

Detectar automaticamente:

* S01E01
* Season
* Episode
* Temporada
* Capítulo

Separar:

* plataforma
* gênero
* coleção

Exemplo:

group-title="SERIES | Netflix"
group-title="SERIES | Dorama"
group-title="SERIES | Marvel"

IMPORTANTE:
Hoje as séries existem no sistema mas não aparecem corretamente nas categorias.

Corrigir isso.

==================================================
FILMES — CATEGORIAS OBRIGATÓRIAS
================================

Separar EXATAMENTE nessas categorias:

* Todos
* Cinema
* Lançamentos
* 4K
* Ação
* Animação
* Animes Filmes
* Aventura
* Clássicos
* Coletânea 007
* Coletânea Batman
* Coletânea Bourne
* Coletânea Jornada nas Estrelas
* Coletânea Os Trapalhões
* Coletânea Resident Evil
* Coletânea Rocky
* Coletânea Star Wars
* Comédia Stand-up
* Comédia
* Comédia Romântica
* Crime
* Drama
* Documentários Filmes
* Faroeste
* Ficção
* Guerra
* Infantil
* Karaoke
* Legendados
* Musical
* Nacional
* Religiosos
* Romance
* Suspense
* Terror
* Especiais de Natal

==================================================
REGRAS PARA FILMES
==================

Detectar automaticamente:

* Movie
* BluRay
* WEB-DL
* 1080p
* 4K
* MKV
* MP4

Separar corretamente:

* filmes
* séries
* canais live

Usar:

group-title="FILMES | Ação"
group-title="FILMES | Lançamentos"
group-title="FILMES | 4K"

==================================================
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

==================================================
PARSER
======

Revisar:

* scripts/merge_lists.py
* scripts/iptv_core.py

Melhorar:

* heurísticas
* classificação
* detecção de categorias
* detecção de qualidade
* detecção de plataforma
* separação de conteúdo

==================================================
OUTPUT FINAL
============

Gerar:

/index.m3u
/output/index.m3u

/output/live/
/output/series/
/output/movies/

/output/channels/
/output/categories/
/output/countries/

Todos os arquivos devem conter streams reais funcionais.

==================================================
VALIDAÇÃO FINAL
===============

Explicar:

* por que as categorias não apareciam antes
* como os players IPTV interpretam group-title
* como o parser agora classifica conteúdos
* como live TV, séries e filmes foram separados
* como SD/HD/FHD/4K foram agrupados
* como as plataformas foram identificadas
