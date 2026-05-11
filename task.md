Precisamos RESETAR COMPLETAMENTE a arquitetura da playlist IPTV.

O projeto ficou poluído com:
- categorias antigas
- playlists antigas
- outputs antigos
- pastas legadas
- arquivos duplicados
- estruturas conflitantes
- group-title conflitando

Isso está causando:
- categorias vazias
- SERIES aparecendo em TV AO VIVO
- categorias quebradas
- comportamento inconsistente no player

--------------------------------------------------
OBJETIVO
--------------------------------------------------

FAZER UMA RECONSTRUÇÃO LIMPA.

NÃO reaproveitar outputs antigos.

--------------------------------------------------
PASSO 1 — LIMPEZA TOTAL
--------------------------------------------------

REMOVER COMPLETAMENTE:

categories/
channels/
countries/
kids/
live/
movies/
news/
series/
sports/
vod/
output/

REMOVER também:
- playlists antigas inutilizadas
- arquivos .m3u duplicados
- outputs legados
- cache gerado
- categorias antigas
- qualquer playlist órfã

MANTER SOMENTE:
- scripts/
- playlists/source/
- config/
- README
- workflow necessário

--------------------------------------------------
PASSO 2 — NOVA ARQUITETURA
--------------------------------------------------

Gerar SOMENTE:

output/index.m3u

Opcional:
output/report.json

NÃO criar:
- centenas de subpastas
- categorias separadas
- estrutura duplicada

O PLAYER IPTV usa apenas:
group-title

--------------------------------------------------
PASSO 3 — RECONSTRUIR PLAYLIST
--------------------------------------------------

Gerar UMA ÚNICA playlist limpa:

output/index.m3u

com:
- #EXTM3U no topo
- UTF-8 válido
- EXTINF padronizado
- group-title correto

--------------------------------------------------
FORMATO OBRIGATÓRIO
--------------------------------------------------

TV AO VIVO:
group-title="TV AO VIVO | Categoria"

SERIES:
group-title="SERIES | Categoria"

FILMES:
group-title="FILMES | Categoria"

--------------------------------------------------
REGRA ABSOLUTA
--------------------------------------------------

NUNCA permitir:

- SERIES dentro de TV AO VIVO
- FILMES dentro de SERIES
- categorias órfãs
- categorias vazias
- conteúdos sem group-title
- group-title duplicado errado

--------------------------------------------------
PASSO 4 — CLASSIFICAÇÃO LIMPA
--------------------------------------------------

Classificar item por item.

EXEMPLOS:

Naruto
=> SERIES | Animes

Breaking Bad
=> SERIES | Drama

ESPN HD
=> TV AO VIVO | Canais ESPN

Premiere 2
=> TV AO VIVO | Canais Premiere Clubes

Batman Begins
=> FILMES | Ação

--------------------------------------------------
PASSO 5 — SANITIZAÇÃO
--------------------------------------------------

REMOVER:
- IgorBifano
- tokens
- usuários
- senhas
- URLs privadas

NÃO deixar credenciais visíveis.

--------------------------------------------------
PASSO 6 — VALIDAÇÃO REAL
--------------------------------------------------

Após gerar:
output/index.m3u

FAZER:

1. Contagem de categorias
2. Contagem de itens por categoria
3. Detectar categorias vazias
4. Detectar conteúdos classificados errado

Exibir relatório no terminal.

--------------------------------------------------
PASSO 7 — TESTE REAL
--------------------------------------------------

Validar no próprio player:

- SERIES | Animes deve abrir conteúdo
- SERIES | Netflix deve abrir conteúdo
- TV AO VIVO | ESPN deve abrir canais
- FILMES | Ação deve abrir filmes

--------------------------------------------------
PASSO 8 — FINALIZAÇÃO
--------------------------------------------------

Commit + push.

Commit:
[v1.x.x] [adjustment] Full IPTV architecture rebuild