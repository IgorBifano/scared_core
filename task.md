Precisamos corrigir definitivamente a estrutura e classificação da playlist IPTV.

O app/player já lê corretamente categorias M3U usando group-title.
O problema atual é que muitas categorias são criadas vazias.

EXEMPLO DO BUG:
- "SERIES | Todos" mostra séries normalmente
- "SERIES | Animes" aparece vazio
- Categorias de TV ao Vivo aparecem misturadas com SERIES

OBJETIVO:
Corrigir parser, classificação e geração das playlists para que TODAS AS CATEGORIAS contenham os itens corretos.

--------------------------------------------------
REGRAS OBRIGATÓRIAS
--------------------------------------------------

1. PADRONIZAÇÃO DE GROUP-TITLE

TV ao vivo:
group-title="TV AO VIVO | Nome Categoria"

Séries:
group-title="SERIES | Nome Categoria"

Filmes:
group-title="FILMES | Nome Categoria"

NUNCA misturar:
- SERIES dentro de TV AO VIVO
- FILMES dentro de SERIES
- etc

--------------------------------------------------
2. GERAR PLAYLISTS FUNCIONAIS
--------------------------------------------------

Cada categoria precisa gerar:
- playlist individual válida
- contendo os itens reais

Exemplo:
output/series/animes.m3u

Esse arquivo PRECISA conter:
- todas as séries/animes
- links válidos
- EXTINF completos

Não pode gerar categoria vazia.

--------------------------------------------------
3. CLASSIFICAÇÃO AUTOMÁTICA
--------------------------------------------------

Implementar classificação inteligente baseada em:
- group-title original
- tvg-name
- nome do conteúdo
- keywords

EXEMPLOS:

Se nome contém:
- Naruto
- One Piece
- Bleach
- Attack on Titan

=> SERIES | Animes

Se contém:
- ESPN
- ESPN 2
- ESPN HD

=> TV AO VIVO | Canais ESPN

Se contém:
- SporTV
=> TV AO VIVO | Canais Sportv

Se contém:
- HBO
=> TV AO VIVO | Canais HBO

Se contém:
- Premiere
=> TV AO VIVO | Canais Premiere Clubes

Se contém:
- Netflix
=> SERIES | Netflix

Se contém:
- Prime Video
=> SERIES | Amazon Prime Video

--------------------------------------------------
4. CATEGORIAS OBRIGATÓRIAS
--------------------------------------------------

TV AO VIVO:
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

SERIES:
- Todos
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

FILMES:
- Todos
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

--------------------------------------------------
5. REMOVER DADOS PESSOAIS
--------------------------------------------------

REMOVER completamente:
- IgorBifano
- usuários/senhas embutidos
- tokens pessoais
- URLs privadas

EXEMPLO:

ANTES:
http://server.xyz/IgorBifano/token/123

DEPOIS:
substituir por stream limpa ou remover entrada.

NÃO expor credenciais em nenhuma playlist gerada.

--------------------------------------------------
6. SAÍDA FINAL
--------------------------------------------------

Gerar:

output/index.m3u
output/tv/
output/series/
output/movies/

Cada categoria deve funcionar corretamente no player.

--------------------------------------------------
7. FINALIZAÇÃO
--------------------------------------------------

Ao terminar:
- executar regeneração completa
- validar categorias
- fazer commit
- fazer push no GitHub

Formato commit:
[v1.x.x] [adjustment] IPTV category classification fix