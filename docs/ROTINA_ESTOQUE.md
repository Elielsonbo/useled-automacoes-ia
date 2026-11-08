# Rotina de montagem do estoque de stories

Executada pela tarefa agendada **"Estoque Stories USE LED"**, toda **segunda (~10h)** e **quinta (~12h)**. Substitui a antiga rotina de 1 story por vez (`ROTINA_STORY.md`, aposentada).

**Divisão de trabalho**
- **Montagem (esta rotina, no Mac):** escolhe os modelos, gera as artes e monta a fila.
- **Publicação (GitHub Actions, sem o Mac):** publica 1 story às ~9h e ~20h. Fica no repositório `Elielsonbo/useled-stories-midia`, em `scripts/publicar_fila.py` e `.github/workflows/publicar-story.yml`.

**Pastas**
- Projeto no Mac: `~/Downloads/Projeto Automacao e Shopee` (no shell do Mac: `$HOME/mnt/Projeto Automacao e Shopee`).
- Repositório de mídia: branch `stories` = imagens; branch `main` = `fila/fila.json` + publicador.

## 1. Quantos stories montar
| Dia da montagem | Horários cobertos | Agendados |
|---|---|---|
| Segunda | seg 20h, ter 9h/20h, qua 9h/20h, qui 9h | 6 |
| Quinta | qui 20h, sex 9h/20h, sáb 9h/20h, dom 9h/20h, seg 9h | 8 |

Além disso, mantenha **2 reservas** (`horario: null`) pendentes na fila. Conte as que já existem e complete só o que faltar. Reservas devem ser de temas **sem data** (decoração, luminárias, livros/filmes).

Antes de montar:
- Leia a fila atual (`main:fila/fila.json`) e **não duplique horários** que já têm item pendente.
- Rode no Mac `historico.sincronizar_com_fila()` para marcar no histórico o que já foi publicado.
- Se a montagem anterior falhou e algum horário já passou, comece pelo próximo horário futuro.

## 2. Distribuição de temas
- **Antes de tudo, leia `foco_semana` em `stories/temas.json`.** Se estiver dentro da validade, atenda primeiro os pedidos do dono da loja (quantidade mínima por tema). Só depois complete com a distribuição normal.
- Use `stories/temas.json`: só temas cuja janela inclui a data do horário (ex.: Halloween só até 31/10, Natal de 15/10 a 25/12, Ano Novo de 20/12 a 05/01).
- Nunca o mesmo tema em dois horários seguidos. Varie conforme o `peso`.
- Datas especiais perto do horário (Halloween na véspera, Natal em dezembro) podem ganhar mais espaço.

## 3. Coleta (navegador integrado do app Claude no Mac)
- Busca por termo do tema: `https://makerworld.com/en/search/models?keyword=<termo>&orderBy=hotScore`. Extraia com `stories/coleta/extrair_makerworld.js`.
- O MakerWorld bloqueia robôs na nuvem: **só pelo navegador do Mac**. Nunca contorne captcha ou bloqueio. Se bloquear, pare e avise.

## 4. Curadoria — regras do dono da loja
**Excluir sempre:**
- conotação **política**, ideológica ou partidária; símbolos de ódio; **conteúdo preconceituoso** ou ofensivo a qualquer grupo;
- conteúdo violento ou de mau gosto (ex.: adereço de "zíper no rosto", gore), armas, conteúdo adulto ou NSFW;
- objetos que não são decorativos ou úteis em casa (peças de impressora, calibração, cartões de teste);
- modelos já publicados ou agendados nos últimos 30 dias (`model_id` no histórico ou na fila);
- modelos sem nenhuma foto limpa.

**Limite de complexidade** (no perfil de impressão mais baixado; se houver um perfil "menor" no próprio modelo, ele pode ser usado):
- **até 12 h** de impressão **e até 300 g** de filamento.

**Preferir:** em alta (`hotScore` alto, criação recente, muitas curtidas), visual bonito e coerente com a marca (luz, aconchego, casa, presente), boa foto.

## 5. Dados de cada modelo
Na página do modelo, use `__NEXT_DATA__` → `props.pageProps.design`:
- fotos em `designExtension.design_pictures[].url`;
- perfis em `instances[]`: `weight` (g), `prediction` (s → h), `title`, `downloadCount`;
- `license`, `designCreator.handle`.

## 6. Foto limpa
Baixe todas as fotos na nuvem (`curl` em makerworld.bblmw.com funciona) e **olhe cada uma**. Use a mais limpa: sem texto sobreposto, sem logotipo de jogo/marca, sem colagem, produto nítido. A capa costuma ter texto; a 2ª ou 3ª foto geralmente é limpa.

## 7. Texto (pt-BR, tom acolhedor e simples)
- `titulo` + `titulo_destaque`: até 30 caracteres somados (ex.: "Rena" + "de tricô").
- `corpo`: até 110 caracteres, terminando em convite ("Encomende o seu.", "Chama no direct e encomende.").
- `chip`: o do tema. `credito`: "Modelo: @criador · MakerWorld".
- Sem preço, sem prazo, sem marcas registradas no texto da loja (ex.: "caneta gigante", e não "Bic").

## 8. Artes (na nuvem)
1. Traga do Mac (device_stage_files): `stories/arte/gerar_arte.py`, `stories/arte/templates/story_produto.html` e `stories/arte/templates/assets/**`.
2. Para cada story, monte o JSON e rode `python3 gerar_arte.py <json> <saida>.jpg`.
3. **Olhe todas as artes** numa folha de contato antes de subir.

## 9. Subir para o GitHub
1. Anexe `Elielsonbo/useled-stories-midia` com acesso de envio (add_repo, access "push").
2. **Imagens**, na branch `stories`: `AAAA/MM/AAAA-MM-DD_HHh_<tema>_<model_id>.jpg`, ou `reserva_<tema>_<model_id>.jpg`. Confira HTTP 200 nas URLs raw.
3. **Fila**, na branch `main`, `fila/fila.json`: acrescente itens com id, horario (ISO com -03:00 ou null), url, tema, titulo, model_id, link, criador e `"status": "pendente"`.
   - Itens já publicados ficam no arquivo como registro.
   - Faça `git pull --rebase` antes do push, porque o publicador também grava nesse arquivo.

## 10. Histórico (Mac)
Salve um JSON do estoque em `stories/dados/estoques/estoque_AAAA-MM-DD.json`, com as colunas do histórico: data, horario, tema, titulo_story, modelo, criador, licenca, link_makerworld, filamento_g, tempo_impressao_h, perfil_impressao, arte (URL), status "agendado" ou "reserva", model_id. Depois rode `historico.registrar_estoque(<json>)`. O custo é calculado automaticamente.

## 11. Aviso ao dono da loja
Envie (SendUserFile) a folha de contato do estoque e uma mensagem curta (SendUserMessage) com a lista: horário · título · tema · custo estimado · link. Ele não precisa aprovar. Se ele pedir para tirar algum item, mude o status para "removido" na fila.

## Saúde do publicador (verifique a cada montagem)
- Execuções do workflow "Publicar story" desde a última montagem (`gh api repos/Elielsonbo/useled-stories-midia/actions/runs`).
  - Se houver falha, investigue: token, fila vazia, URL.
  - Avise o dono da loja só se precisar de ação dele.
- Se `renovar-token` falhar por falta do `GH_PAT`, avise o dono da loja.
- Confira também o workflow **"Compartilhar post do feed"** (a cada 2 dias, à tarde; veja `docs/ROTINA_FEED.md`): se falhou ou se `fila/compartilhados.json` não ganhou item novo num dia de compartilhar, investigue e corrija. Avise o dono da loja só se precisar de ação dele.
