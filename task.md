Corrigir completamente a arquitetura e classificação das playlists M3U do projeto IPTV.

PROBLEMAS ATUAIS:

1. As categorias aparecem no app IPTV, mas os conteúdos não aparecem dentro delas.
2. Séries estão sendo exibidas como TV ao vivo.
3. Filmes e séries não estão sendo classificados corretamente como VOD.
4. O group-title está inconsistente.
5. Algumas categorias aparecem vazias mesmo havendo conteúdo.
6. O cabeçalho das categorias está incorreto (ex.: SERIES aparecendo em TV AO VIVO).
7. O sistema atual cria pastas corretamente, mas o player IPTV não interpreta os conteúdos.

OBJETIVO:

Reestruturar TODA a geração dos arquivos M3U para funcionar corretamente em IPTV Smarters, TiviMate, OTT Navigator e apps similares.

REQUISITOS OBRIGATÓRIOS:

==================================================
TV AO VIVO
==================================================

Todos os canais ao vivo DEVEM:

- permanecer como streams LIVE
- usar:
  group-title="TV AO VIVO | Nome da Categoria"

Exemplo:

group-title="TV AO VIVO | Canais ESPN"

As categorias obrigatórias:

- Todos
- Canais Abertos
- Canais Internacionais
- Canais Documentarios
- Canais Filmes e Series
- Canais HBO
- Canais Telecine
- Canais Infantis
- Canais Noticias
- Canais Variedades
- Canais Religiosos
- Canais Premiere Clubes
- Canais Sportv
- Canais ESPN
- Canais Amazon Prime
- Canais Disney
- Canais Paramount
- Canais HBO MAX
- Canais TNT
- Canais Combate/UFC Fight
- Canais Nba League Pass
- Canais Apple TV
- Canais Cazé TV
- Canais DAZN
- Canais GE TV
- Canais GOAT
- Canais Nosso Futebol
- Canais NSPORTS
- Canais XSPORTS
- Canais 24h Animes
- Canais 24h Discovery
- Canais 24h Novelas
- Canais 24h Infantis
- Canais 24h Series de TV
- Canais Adultos

Também separar canais SD/HD/FHD/4K quando possível.

==================================================
SÉRIES
==================================================

Séries DEVEM ser exportadas como VOD/SERIES.

NÃO podem aparecer em TV AO VIVO.

Cada série deve conter atributos compatíveis com players IPTV:

- tvg-name
- tvg-logo
- group-title
- título correto
- URL final

group-title deve seguir:

group-title="SERIES | Netflix"

ou

group-title="SERIES | Ação"

Categorias obrigatórias:

- ABC
- AMC+
- Apple TV
- BBC ONE
- Brasil Paralelo
- CW
- Discovery +
- Disney +
- GloboPlay
- HBO Max
- Hulu
- Lionsgate +
- Looke
- Netflix
- Paramount +
- PlayPlus
- Amazon Prime Video
- Starz
- Via Play
- Ação
- Animação/Infantil
- Animes
- Aventura
- Chicago Universe
- Comedia
- Crime
- Documentários
- Dorama
- Drama
- Ficção e Fantasia
- Faroeste
- Guerra
- Marvel
- Mini Séries
- Nacional
- Novelas
- Reality Shows
- Romance
- Suspense
- Terror
- Turcas
- Tv Show

Corrigir problema atual onde as categorias aparecem vazias.

O conteúdo realmente precisa ser atribuído aos grupos.

==================================================
FILMES
==================================================

Filmes DEVEM ser exportados como VOD.

group-title:

group-title="FILMES | Ação"

Categorias obrigatórias:

- Cinema
- Lançamentos
- 4K
- Ação
- Animação
- Animes Filmes
- Aventura
- Clássicos
- Coletânea 007
- Coletânea Batman
- Coletânea Bourne
- Coletânea Jornada nas Estrelas
- Coletânea Os Trapalhões
- Coletânea Resident Evil
- Coletânea Rocky
- Coletânea Star Wars
- Comédia Stand-up
- Comédia
- Comédia Romântica
- Crime
- Drama
- Documentários Filmes
- Faroeste
- Ficção
- Guerra
- Infantil
- Karaoke
- Legendados
- Musical
- Nacional
- Religiosos
- Romance
- Suspense
- Terror
- Especiais de Natal

==================================================
ESTRUTURA
==================================================

Gerar:

/output/index.m3u
/output/live/
/output/series/
/output/movies/
/output/categories/
/output/channels/

==================================================
INDEX PRINCIPAL
==================================================

index.m3u deve funcionar corretamente em players IPTV.

As categorias precisam abrir com conteúdo real.

==================================================
CORREÇÃO CRÍTICA
==================================================

Atualmente os grupos aparecem mas não exibem itens.

Corrigir a lógica que associa entries aos arquivos M3U finais.

==================================================
REMOVER IDENTIDADE PESSOAL
==================================================

Não exibir:
- IgorBifano
- tokens pessoais
- usernames
- senhas
- credenciais

nos nomes dos canais ou metadados.

NÃO alterar URLs de stream automaticamente ainda.

Apenas limpar metadados e nomes visíveis.

==================================================
RESULTADO ESPERADO
==================================================

Ao abrir no IPTV Smarters:

- TV AO VIVO mostra canais reais
- SERIES mostra séries reais
- FILMES mostra filmes reais
- categorias funcionam
- itens aparecem dentro das categorias
- nada vazio
- sem credenciais visíveis