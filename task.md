Analise completamente a estrutura deste projeto IPTV.

Objetivos:
- entender como as playlists .m3u estão sendo processadas
- identificar onde os arquivos finais são gerados
- localizar scripts de merge, parser e geração de playlists
- identificar como categorias estão sendo criadas

Depois disso:

1. Refatore o sistema para:
   - gerar playlists separadas por categoria
   - gerar playlists separadas por canal/rede
   - remover duplicatas
   - normalizar nomes de canais
   - criar um index.m3u principal

2. A nova estrutura deve gerar:
   /categories/
   /channels/
   /countries/
   /output/

3. Criar playlists individuais automaticamente como:
   - espn.m3u
   - sportv.m3u
   - disney_channel.m3u
   - hbo.m3u
   - premiere.m3u

4. A playlist principal index.m3u deve incluir os grupos organizados.

5. Integrar também a playlist personalizada colocada na raiz do projeto.

6. Garantir compatibilidade com GitHub Pages para acesso direto via:
https://igorbifano.github.io/scared_core/

7. Criar pipeline automatizado para regenerar playlists.

Antes de alterar qualquer coisa:
- faça uma análise completa do projeto
- explique a arquitetura atual
- explique o fluxo de geração das playlists
- mostre os pontos críticos e gargalos