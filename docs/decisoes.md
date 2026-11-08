# Decisões — Etapa 1 (Stories)

Registro do que foi decidido e por quê. Atualizado em 22/10/2026.

## Fechadas

| # | Decisão | Detalhe |
|---|---|---|
| D1 | **Temas** | Halloween, Natal, Ano Novo, Casa & Decoração, Luminárias Divertidas, Filmes/Séries/Livros. Em `stories/temas.json`. |
| D2 | **Conta** | @use_led_luminarias já é profissional. |
| D3 | **Objetivo** | Inspirar e gerar encomendas. Sem filtro de licença; a licença de cada modelo fica registrada no histórico (O1). |
| D4 | **Identidade** | Kit USE LED: Carvão #1F1F1C, Marfim #F7F3EA, Greige #B8AFA2, Terracota #C96A3A, Kraft #A9784B. Fontes Sora e DM Sans. |
| D5 | **Arte** | Template próprio (`story_produto.html`) com o título fixo **"Ideias de impressão 3D"**, nome do modelo como subtítulo, selo do tema e crédito ao criador. JPEG 1080x1920. |
| D6 | **Onde roda** | No Mac. GitHub Actions fica como plano B. |
| D7 | **Frequência** | **2 stories por dia: 9h e 20h** (horário de Brasília). |
| D8 | **Histórico de links** | Cada story publicado gera uma linha em `stories/dados/historico.csv` (abre no Numbers/Excel) com data, tema, modelo, criador, licença e **link do MakerWorld**. Também evita repetir modelo por 30 dias. |
| D9 | **Rede** | Domínios liberados: `makerworld.com`, `makerworld.bblmw.com`, `graph.facebook.com`, `graph.instagram.com`. |
| D10 | **Coleta pelo navegador do Mac** | O MakerWorld tem proteção anti-robô (Cloudflare) que bloqueia acessos de servidores. A coleta funciona pelo **navegador integrado do app Claude no seu Mac**, que acessa como um usuário comum. Não vamos tentar burlar a proteção. |
| D12 | **App Meta** | App "USE LED Stories" criado no portfólio Use Led, com @useledluminarias como testadora. Token validado em 22/10. Detalhes em `docs/meta_app.md`. |
| D13 | **Foto do modelo** | O modelo aparece **inteiro** no card (sem corte), com a própria foto desfocada preenchendo as sobras. A curadoria escolhe a foto **mais limpa** entre todas as do modelo: capa com texto sobreposto é descartada (geralmente a 2ª ou 3ª foto é a mesma, limpa). |
| D14 | **Custo estimado (uso interno)** | Para cada modelo, o histórico guarda filamento (g), tempo de impressão (h) e perfil, lidos da página do MakerWorld, e calcula um custo estimado de produção. Os valores da base de custos ficam fora do repositório público. Nunca aparece no story. |
| D15 | **Publicação validada** | 1º story publicado em 22/10/2026, às 12:06 (Presépio minimalista). Imagens no repositório público `Elielsonbo/useled-stories-midia` (branch `stories`); publicação por `stories/publicacao/publicar.py`. |
| D16 | **Tarefa agendada ativa** | "Stories USE LED" roda às **8:44 e 19:44** (horário de Brasília), para o story sair por volta das 9h e das 20h. Modo **automático com aviso**: publica sozinho e avisa o dono da loja com a arte, o link e o custo. Segue `docs/ROTINA_STORY.md`. Requisito: Mac ligado e app Claude aberto. |
| D11 | **Orquestração** | **Tarefa agendada do Claude** às 9h e 20h: abre o MakerWorld no navegador do Mac, faz a curadoria, escreve o texto, gera a arte, publica e registra no histórico. Requisito: **Mac ligado e app Claude aberto** nesses horários. |

## Em aberto

| # | Pergunta | Por que importa |
|---|---|---|

## Observações

**O1. Licença.** Na amostra de Natal coletada hoje, 15 de 20 modelos usam a licença padrão do MakerWorld, que proíbe vender a impressão sem permissão do criador. Quando entrar uma encomenda, confira a licença no histórico.

**O2. Sazonalidade.** Hoje é 22/10. O Halloween só entra se a automação ficar pronta antes do dia 31. O Natal tem o maior peso daqui até 25/12.

**O3. "Em alta".** O MakerWorld oferece a ordenação "Tendendo" (`hotScore`). A curadoria usa essa ordem, prioriza modelos recentes e descarta os sem foto vertical boa e os já publicados.

## D20 — Horários de reserva no agendamento (22/10/2026)
O primeiro agendamento das 19h50 não foi disparado pelo GitHub, e o story das 20h foi publicado manualmente às 20h36. Foram adicionados disparos de reserva às 9h20/9h50 e 20h20/20h50. Eles não duplicam posts, porque o script pula se já publicou nas últimas 3h.

## D21 — Agendamento mais cedo e repetido (26/10/2026)
De 22 a 26/10, o GitHub atrasou os disparos de 1h30 a 4h, e o story de domingo de manhã não saiu. Agora há 6 disparos por período (6h07–9h52 e 17h07–20h52). O script publica a partir de 1h antes do horário e dentro das janelas 8–12h e 19–23h. Foi mantido só o GitHub, sem tarefa agendada do Claude (decisão do dono da loja).

## D22 — Compartilhar posts do feed nos stories (26/10/2026)
Pedido do dono da loja: a cada 2 dias, a partir de 26/10, compartilhar nos stories um post do próprio feed (só do último ano). A rotina roda sozinha no GitHub Actions, entre 11h e 18h. Como a API não tem o compartilhamento nativo de post, a automação gera uma arte da marca com a imagem do post e o convite "veja no perfil". Detalhes em docs/ROTINA_FEED.md.

## D23 (29/10/2026): story semanal de produto
Um story por semana (domingo, 14h–19h) com um produto da Shopee em rodízio, pelo workflow `produto-semanal.yml` e o script `scripts/produto_semanal.py`. Usa a mesma arte do compartilhamento do feed (kicker "Na nossa loja", CTA "Procure useled3d na Shopee"). A lista e a ordem ficam em `fila/produtos.json` (foto em stories:produtos/<id>.jpg). O Polaroid ficou para a 3ª semana por causa da reposição de ímãs.

## D24 (03/11/2026): janela da noite mais larga
Em 02/11 os disparos do GitHub caíram às 18h57 e 23h14, fora da janela de 19h a 23h, e o story das 20h perdeu o horário (virou reserva). Pedido do dono da loja: a janela da noite passou para 18h–23h59. A antecedência subiu de 1h para 2h, para que um disparo às 18h publique o item das 20h em vez de uma reserva.
