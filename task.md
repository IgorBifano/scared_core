Você é um engenheiro especialista em IPTV, playlists M3U, automação Python, parsing de streams, organização de projetos e clean architecture.

Sua tarefa é analisar TODO o projeto atual profundamente antes de modificar qualquer coisa.

━━━━━━━━━━━━━━━━━━━
FASE 1 — ANÁLISE COMPLETA
━━━━━━━━━━━━━━━━━━━

Primeiro:

1. Analise toda a estrutura do projeto.
2. Identifique:

* arquivos importantes
* arquivos inúteis
* arquivos duplicados
* scripts antigos
* dependências desnecessárias
* listas quebradas
* estruturas redundantes
* categorias bagunçadas
* logos inutilizados
* arquivos temporários

3. Descubra:

* como o projeto funciona atualmente
* onde ficam playlists
* onde ficam scripts
* como as listas são organizadas
* quais arquivos realmente importam

4. Após analisar:
   MOSTRE UM RELATÓRIO COMPLETO contendo:

* árvore do projeto
* o que vale manter
* o que deve ser removido
* o que deve ser reorganizado
* melhorias recomendadas
* possíveis problemas de performance

NÃO faça mudanças antes da análise inicial.

━━━━━━━━━━━━━━━━━━━
FASE 2 — LIMPEZA E REORGANIZAÇÃO
━━━━━━━━━━━━━━━━━━━

Depois da análise:

1. Fazer clean code em todo o projeto.
2. Remover:

* arquivos inúteis
* assets não utilizados
* listas mortas
* código redundante
* scripts desnecessários
* configurações quebradas
* duplicações

3. Criar backup automático antes de apagar qualquer coisa:
   backup/

4. Manter apenas o que for útil para um projeto IPTV pessoal, organizado e escalável.

━━━━━━━━━━━━━━━━━━━
FASE 3 — INTEGRAÇÃO DA MINHA LISTA
━━━━━━━━━━━━━━━━━━━

Existe um arquivo na raiz do projeto chamado:

plus.m3u

Essa é minha lista pessoal.

O sistema deve:

* detectar automaticamente esse arquivo
* integrar essa lista ao restante do projeto
* unir ela com as outras playlists existentes
* remover canais duplicados
* manter categorias organizadas
* preservar entradas únicas da plus.m3u

━━━━━━━━━━━━━━━━━━━
FASE 4 — NOVA ESTRUTURA PROFISSIONAL
━━━━━━━━━━━━━━━━━━━

Criar estrutura organizada:

* playlists/
* countries/
* categories/
* channels/
* sports/
* movies/
* series/
* kids/
* news/
* live/
* vod/
* logos/
* config/
* scripts/
* output/
* backup/

━━━━━━━━━━━━━━━━━━━
FASE 5 — ORGANIZAÇÃO POR PAÍS
━━━━━━━━━━━━━━━━━━━

Separar automaticamente canais por país:

countries/

* br/
* us/
* uk/
* es/
* pt/
* jp/
* kr/
* fr/
* de/
* latam/
* others/

Detectar país usando:

* nome do canal
* group-title
* tvg-id
* padrões conhecidos

Exemplos:

* SporTV → Brasil
* ESPN BR → Brasil
* BBC → Reino Unido
* FOX USA → Estados Unidos
* NHK → Japão

Se não conseguir identificar:
Enviar para:
countries/others/

━━━━━━━━━━━━━━━━━━━
FASE 6 — ORGANIZAÇÃO POR CANAIS ESPECÍFICOS
━━━━━━━━━━━━━━━━━━━

Criar separação específica para canais conhecidos.

Exemplos:

channels/

* espn/
* sportv/
* disney/
* telecine/
* hbo/
* premiere/
* discovery/
* cartoon/
* fox/
* cnn/
* globo/
* nick/
* warner/

Separar automaticamente canais relacionados.

Exemplos:

* ESPN HD
* ESPN 2
* ESPN 4

Todos devem ir para:
channels/espn/

Outro exemplo:

* Disney Channel
* Disney Junior
* Disney XD

Todos devem ir para:
channels/disney/

━━━━━━━━━━━━━━━━━━━
FASE 7 — AUTOMAÇÃO IPTV
━━━━━━━━━━━━━━━━━━━

Criar script:
scripts/merge_lists.py

Esse script deve:

1. Ler:

* playlists locais
* plus.m3u
* URLs em config/sources.txt

2. Unificar tudo.

3. Remover:

* canais duplicados
* streams offline
* links inválidos
* entradas vazias

4. Padronizar:

* tvg-id
* tvg-name
* tvg-logo
* group-title
* nomes dos canais

5. Organizar automaticamente:

* país
* categoria
* canal específico

6. Gerar:

output/all_channels.m3u

output/countries/br.m3u
output/countries/us.m3u

output/categories/sports.m3u
output/categories/movies.m3u

output/channels/espn.m3u
output/channels/disney.m3u
output/channels/sportv.m3u

━━━━━━━━━━━━━━━━━━━
FASE 8 — QUALIDADE DO CÓDIGO
━━━━━━━━━━━━━━━━━━━

* Código modular
* Funções separadas
* Python tipado
* Logs claros
* Tratamento de erros
* Estrutura escalável
* Comentários úteis
* Clean Architecture

━━━━━━━━━━━━━━━━━━━
FASE 9 — ARQUIVOS IMPORTANTES
━━━━━━━━━━━━━━━━━━━

Criar:

* README.md
* requirements.txt
* .gitignore

README deve explicar:

* estrutura
* como adicionar listas
* como rodar scripts
* como atualizar playlists
* como gerar arquivos finais

━━━━━━━━━━━━━━━━━━━
FINALIZAÇÃO
━━━━━━━━━━━━━━━━━━━

Ao terminar:

1. Mostrar resumo completo das alterações.
2. Mostrar árvore final do projeto.
3. Explicar o que foi removido.
4. Explicar o que foi otimizado.
5. Explicar como executar tudo.
6. Explicar como adicionar novas listas futuramente.

Você pode modificar, reorganizar, mover e limpar qualquer parte do projeto para transformá-lo em uma estrutura IPTV pessoal profissional, limpa e escalável.
