# Rotina do story (executada pela tarefa agendada às ~9h e ~20h)

Fonte de verdade da automação. Modo: **publicação automática com aviso** (decidido em 22/10/2026). Nada aqui pede aprovação, exceto quando algo der errado.

Pasta do projeto no Mac: `~/Downloads/Projeto Automacao e Shopee` (no shell do Mac: `$HOME/mnt/Projeto Automacao e Shopee`).

## 0. Preparação
1. Confirme acesso à pasta do projeto (device_list_dir). Se o Mac não responder, **pare** e avise o dono da loja: "Story das Xh não saiu: Mac/app Claude offline".
2. Leia `docs/decisoes.md` (regras) e `stories/temas.json`.
3. Renove o token se necessário, no shell do Mac: `cd stories/publicacao && python3 publicar.py --renovar`.

## 1. Tema
No shell do Mac: `cd stories/curadoria && python3 escolher_tema.py` → `{id, chip, busca}`.

## 2. Coleta (navegador integrado do app Claude no Mac — NUNCA pela nuvem; o MakerWorld bloqueia robôs)
1. Para 1–2 termos de `busca`, abra `https://makerworld.com/en/search/models?keyword=<termo>&orderBy=hotScore`.
2. Execute o conteúdo de `stories/coleta/extrair_makerworld.js` na página (javascript_tool) → lista de modelos.
3. Não tente contornar captchas/bloqueios. Se o site bloquear, avise e pare.

## 3. Curadoria (julgamento do Claude)
Descarte: modelo já publicado nos últimos 30 dias (`model_id` no `stories/dados/historico.csv`), nsfw, modelos que não são objetos físicos decorativos/úteis (ex.: cartões, ferramentas de impressora), modelos cuja foto boa não exista.
Prefira: maior `hot_score`, criação recente, visual bonito e coerente com a marca (luz, decoração, casa, presentes). Escolha **1** modelo.

## 4. Página do modelo
Abra o link do modelo no navegador do app e leia `__NEXT_DATA__` → `props.pageProps.design`:
- fotos: `designExtension.design_pictures[].url` (+ `instances[].pictures`)
- impressão: perfil padrão (`defaultInstanceId`, ou o com mais downloads) → `weight` (g), `prediction` (segundos → horas), `title` (perfil)
- licença: `license`; criador: `designCreator.handle`

## 5. Foto limpa
Baixe as fotos (nuvem: `curl` em makerworld.bblmw.com funciona) e **olhe cada uma**. Use a mais limpa: produto em destaque, **sem texto sobreposto**, sem colagens. A capa costuma ter texto; a 2ª/3ª foto geralmente é a mesma, limpa. Se nenhuma servir, volte ao passo 3 e escolha outro modelo.

## 6. Texto (português do Brasil, tom da marca: acolhedor, simples, sem exagero)
- `titulo` + `titulo_destaque`: nome curto do objeto, ex. "Presépio" + "minimalista" (juntos ≤ 30 caracteres)
- `corpo`: 1–2 frases, ≤ 110 caracteres, terminando em convite à encomenda ("Escolha as cores e encomende o seu.", "Chama no direct e encomende.")
- `chip`: o `chip` do tema; `credito`: "Modelo: @<criador> · MakerWorld"
- Nunca prometa prazo, preço ou que o modelo é da loja.

## 7. Arte (na nuvem)
1. Traga para a nuvem (device_stage_files) `stories/arte/gerar_arte.py`, `stories/arte/templates/story_produto.html` e todos os arquivos de `stories/arte/templates/assets/` (inclusive `fonts/`), mantendo a estrutura em uma pasta de trabalho.
2. `pip install playwright pillow` se faltar (Chromium já está em /opt/pw-browsers).
3. Crie `story.json` com os campos do passo 6 + `"imagem": "<foto>"` e rode `python3 gerar_arte.py story.json <saida>.jpg`. Se acusar texto longo, encurte e rode de novo.
4. **Olhe a arte gerada** antes de seguir (modelo inteiro e nítido, texto sem erro).

## 8. Hospedagem (GitHub)
1. Anexe o repositório `Elielsonbo/useled-stories-midia` com acesso de envio (add_repo, access "push") e clone a branch `stories` (`git clone --depth 1 -b stories ...`).
2. Salve como `AAAA/MM/AAAA-MM-DD_HHh_<tema>_<model_id>.jpg`, commit e push na branch `stories`.
3. URL: `https://raw.githubusercontent.com/Elielsonbo/useled-stories-midia/stories/<caminho>` — confirme HTTP 200 com `curl -I`.

## 9. Publicação (shell do Mac)
`cd stories/publicacao && python3 publicar.py "<URL>"` → JSON com `media_id` e `permalink`.
Se falhar: tente de novo 1 vez após 1 minuto; se falhar de novo, avise o dono da loja com o erro e pare (não registre como publicado).

## 10. Registro (shell do Mac)
Em `stories/`, com `sys.path` incluindo `dados`: `historico.registrar({...})` com tema, titulo_story, modelo, criador, licenca, link_makerworld, filamento_g, tempo_impressao_h, perfil_impressao, arte (URL), status="publicado", id_instagram, model_id. O custo é calculado automaticamente.

## 11. Aviso ao dono da loja
Envie a arte (SendUserFile) e uma mensagem curta (SendUserMessage):
"Story das Xh publicado ✅ — <titulo> (<tema>). Link do modelo: <link>. Licença: <licença>."
Se a licença for a padrão do MakerWorld, acrescente: "Para vender a impressão, precisa de permissão do criador."
