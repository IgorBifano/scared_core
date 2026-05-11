PARE de gerar categorias separadas como solução principal.

O player IPTV NÃO usa os arquivos separados para navegação.
Ele usa SOMENTE os group-title da playlist principal.

O problema atual NÃO é existência dos arquivos.
O problema é que os itens dentro da playlist principal continuam classificados errado.

OBJETIVO:
Gerar UMA playlist principal totalmente organizada via group-title.

ARQUITETURA CORRETA:

output/index.m3u

TODOS os conteúdos devem existir nessa playlist única.

O player automaticamente cria:
- TV AO VIVO
- SERIES
- FILMES

baseado no group-title.

--------------------------------------------------
FORMATO OBRIGATÓRIO
--------------------------------------------------

EXEMPLO CORRETO:

#EXTINF:-1 tvg-id="naruto" tvg-name="Naruto" group-title="SERIES | Animes",Naruto
http://stream.com/video.m3u8

#EXTINF:-1 tvg-id="espn.br" tvg-name="ESPN HD" group-title="TV AO VIVO | Canais ESPN",ESPN HD
http://stream.com/live.m3u8

#EXTINF:-1 tvg-id="batman" tvg-name="Batman Begins" group-title="FILMES | Ação",Batman Begins
http://stream.com/movie.m3u8

--------------------------------------------------
PROBLEMA ATUAL
--------------------------------------------------

O menu de categorias aparece.
Mas quando clico:
- SERIES | Animes
- SERIES | Netflix
- etc

fica vazio.

Isso significa:
os itens NÃO estão com group-title correto dentro da playlist principal.

--------------------------------------------------
CORRIGIR DEFINITIVAMENTE
--------------------------------------------------

1. NÃO gerar apenas arquivos separados
2. Atualizar TODOS os EXTINF da playlist principal
3. Garantir group-title correto item por item
4. Garantir que:
   - animes => SERIES | Animes
   - Netflix => SERIES | Netflix
   - ESPN => TV AO VIVO | Canais ESPN
   - HBO => TV AO VIVO | Canais HBO
   - filmes ação => FILMES | Ação

--------------------------------------------------
VALIDAÇÃO OBRIGATÓRIA
--------------------------------------------------

Após gerar output/index.m3u:

FAZER TESTE REAL:

- contar quantos itens possuem:
group-title="SERIES | Animes"

- contar quantos itens possuem:
group-title="SERIES | Netflix"

- contar quantos itens possuem:
group-title="TV AO VIVO | Canais ESPN"

Exibir os totais no terminal.

Se estiver 0:
a classificação FALHOU.

--------------------------------------------------
REMOVER BUGS
--------------------------------------------------

NUNCA permitir:
- SERIES dentro de TV AO VIVO
- FILMES dentro de SERIES
- categorias vazias
- categorias órfãs
- títulos sem group-title

--------------------------------------------------
IMPORTANTE
--------------------------------------------------

O app IPTV lê:
- group-title
- tvg-name
- tvg-logo
- tvg-id

Ele NÃO usa a estrutura de pastas do GitHub para categorizar.

A categorização inteira precisa existir DENTRO do output/index.m3u.

--------------------------------------------------
FINALIZAÇÃO
--------------------------------------------------

Após corrigir:
- regenerar playlist
- commit
- push

Commit:
[v1.x.x] [adjustment] Fix IPTV group-title architecture