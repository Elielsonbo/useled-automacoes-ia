# Planejamento — Automação dos Stories (Etapa 1)

> Repositório: `~/Downloads/Projeto Automacao e Shopee`
> Versão 1 — 22/10/2026

## 1. Objetivo

Publicar stories recorrentes no Instagram da loja mostrando modelos 3D em alta no MakerWorld, dentro de temas pré-definidos, com arte padronizada da loja e texto chamativo — com o mínimo de trabalho manual.

**Fluxo-alvo:**

```
MakerWorld ──► Coleta ──► Curadoria ──► Imagem limpa ──► Arte (template) ──► Texto ──► Aprovação ──► Publicação no Story ──► Métricas
   (temas)    (diária)   (score+licença)                   1080x1920 JPEG     (Claude)   (opcional)    (Graph API)          (insights)
```

## 2. Três fatos que moldam o desenho

1. **Story não tem legenda.** Pela API do Instagram, story é só a mídia: não existe campo de legenda, e stickers (link, enquete, menção) não são suportados. Portanto, **o texto vai dentro da arte**. A "legenda" que o Claude cria vira o título/chamada impresso na imagem.
2. **A API exige conta profissional + app Meta + imagem em URL pública.** Publicar story é oficialmente suportado (`media_type=STORIES`), mas exige conta Business/Creator, um app no Meta for Developers com permissão de publicação, e que o JPEG esteja hospedado num endereço público no momento do envio. Limite: ~50–100 publicações por API a cada 24h (sobra muito).
3. **Licença dos modelos do MakerWorld.** A licença padrão do MakerWorld **proíbe vender impressões** sem permissão do criador. Decisão (D3): a curadoria **não filtra** por licença, porque o objetivo é inspirar. Mas **registra a licença** de cada modelo publicado, para você conferir quando entrar uma encomenda. As fotos são do criador: o crédito vai sempre na arte.
4. **O MakerWorld bloqueia robôs (Cloudflare).** A coleta é feita pelo navegador integrado do app Claude no Mac, e o fluxo diário é uma tarefa agendada do Claude às 9h e às 20h (D10 e D11 em `decisoes.md`).

## 3. Arquitetura recomendada

| Componente | Escolha recomendada | Alternativa | Por quê |
|---|---|---|---|
| Coleta MakerWorld | Navegador automatizado (Playwright) lendo as páginas de tendência por tema | Claude navegando via browser integrado | Site é dinâmico; Playwright é estável e grátis |
| Curadoria / score | Script Python + regras + histórico em SQLite | — | Evita repetir modelo, garante variedade de temas |
| Imagem limpa | Melhor foto da galeria + remoção de fundo (`rembg`, local e grátis) | Canva "remove background" | Sem custo por imagem |
| Arte | Template HTML/CSS renderizado em JPEG 1080x1920 | Canva (autofill de template exige plano Enterprise) | Versionável, sem custo, 100% automatizável. O fundo/identidade pode ser desenhado no Canva e exportado como PNG |
| Texto da arte | Claude gera chamada curta + crédito ao criador | Regras fixas | Variedade e tom da marca |
| Aprovação | Fase piloto: kit diário enviado a você para aprovar | Automático total depois | Segurança na largada |
| Hospedagem da imagem | GitHub Pages ou Cloudinary (grátis) | S3 | Requisito da API |
| Publicação | Instagram Graph API (container → publish) | Meta Business Suite manual | Oficial, sem risco de bloqueio |
| Agendamento | Tarefa agendada do Claude **ou** script no Mac/GitHub Actions | — | Decidir na Fase 0 (ver §6) |

## 4. Etapas

### Fase 0 — Fundamentos e decisões (em andamento)
- [x] **Temas** definidos e configurados em `stories/temas.json`.
- [x] **Frequência**: 2 stories/dia, às 9h e às 20h.
- [x] Conta da loja é **profissional**.
- [x] **Licença**: sem filtro, com registro (D3).
- [x] **Identidade visual** incorporada (D4).
- [x] **Liberação de rede** (falta `makerworld.bblmw.com`, das fotos).
- [ ] Criar **app no Meta for Developers** (em andamento, juntos).
- **Entrega:** `docs/decisoes.md`.

### Fase 1 — Coleta no MakerWorld (em andamento)
- [x] Busca por tema com ordenação "Tendendo": `makerworld.com/en/search/models?keyword=<termo>&orderBy=hotScore`.
- [x] Extração validada (`stories/coleta/extrair_makerworld.js`): título, link, criador, licença, curtidas, downloads, data e fotos (inclusive a capa vertical).
- [ ] Baixar as fotos (depende de liberar `makerworld.bblmw.com`).
- [ ] Respeitar o site: baixa frequência (1 coleta/dia), pausas entre páginas, sem sobrecarga.
- [ ] Salvar em `stories/dados/coleta_AAAA-MM-DD.json`.
- **Critério de pronto:** coleta de 20+ modelos/tema com licença identificada corretamente.

### Fase 2 — Curadoria (1 sessão)
- [ ] **Score de tendência**: crescimento recente de downloads/curtidas, idade do modelo, qualidade das fotos.
- [ ] **Filtros eliminatórios**: licença incompatível, modelo já publicado nos últimos 30 dias, sem foto boa, conteúdo fora da marca.
- [ ] **Rodízio de temas** para não repetir o mesmo tema seguido.
- [x] Histórico com os links em `stories/dados/historico.csv` (`historico.py`).
- **Critério de pronto:** gera a fila do dia (N modelos) de forma reproduzível.

### Fase 3 — Imagem limpa (1 sessão)
- [ ] Escolher a melhor foto (maior resolução, produto centralizado, sem texto sobreposto).
- [ ] Remover fundo quando der bom resultado; senão, usar a foto inteira com moldura.
- [ ] Checagem automática de qualidade (resolução mínima, recorte aceitável).

### Fase 4 — Arte padrão (adiantada)
- [x] Template 1 (`story_produto.html`) fiel ao layout atual, com selo do tema, crédito ao criador e símbolo em marca d'água.
- [x] **Zonas seguras** respeitadas (200 px no topo, 180 px na base).
- [x] Gerador `stories/arte/gerar_arte.py` → **JPEG** 1080x1920. Exemplos em `stories/arte/exemplos/`.
- [ ] Você aprovar o visual.
- [ ] Variações 2 e 3 (ex.: fundo escuro Carvão; versão com 2 fotos) para rodízio.

### Fase 5 — Texto da arte (junto com a Fase 4)
- [ ] Prompt do Claude com tom da marca, limite de caracteres (chamada ≤ 40, apoio ≤ 80), sem prometer o que não vendemos.
- [ ] Biblioteca de CTAs para variar.

### Fase 6 — Publicação (1–2 sessões, depende da Meta)
- [ ] Criar app no Meta for Developers, permissões `instagram_business_basic` + `instagram_business_content_publish`.
- [ ] Gerar **token de longa duração** (60 dias) + rotina de renovação automática.
- [ ] Hospedar o JPEG em URL pública.
- [ ] Publicar: criar container `STORIES` → aguardar status → `media_publish`.
- [ ] Tratar erros (token expirado, imagem recusada, limite) com aviso pra você.
- **Atenção:** revisão de app da Meta pode levar dias — começar cedo, em paralelo com as Fases 1–5.

### Fase 7 — Orquestração e agendamento (1 sessão)
- [ ] Um comando único `rodar_dia` que executa Fases 1→6.
- [ ] Agendar nos horários definidos.
- [ ] Piloto com aprovação: você recebe o kit (imagens + textos) e responde OK; só então publica.

### Fase 8 — Métricas e ajuste (contínuo)
- [ ] Coletar insights de cada story (alcance, respostas, toques para avançar/voltar, saídas) — disponíveis por 24h, então a coleta precisa ser diária.
- [ ] Relatório semanal: quais temas/templates performam melhor → ajusta pesos da curadoria.
- [ ] Ligação com a Etapa 2: modelos com bom engajamento viram candidatos a anúncio na Shopee.

### Fase 9 — Piloto e virada para automático
- [ ] 2 semanas em modo aprovação.
- [ ] Critério para liberar automático total: ≥ 90% dos kits aprovados sem ajuste.

## 5. Estrutura do repositório

```
Projeto Automacao e Shopee/
├── docs/                 planejamento, decisões, guia de operação
├── stories/
│   ├── coleta/           scripts MakerWorld
│   ├── curadoria/        score, filtros, rodízio
│   ├── arte/templates/   templates HTML/CSS + assets (logo, fontes)
│   ├── publicacao/       Instagram Graph API, hospedagem, token
│   └── dados/            coletas, histórico, saídas geradas
└── shopee/               Etapa 2
```

## 6. Decisão em aberto: onde roda no dia a dia

| Opção | Prós | Contras |
|---|---|---|
| **A. Script no seu Mac (agendado)** | Grátis, controle total | Mac precisa estar ligado nos horários |
| **B. GitHub Actions (nuvem)** | Grátis, roda sem o Mac, já hospeda a imagem via GitHub Pages | Precisa de conta GitHub; configuração inicial um pouco maior |
| **C. Tarefa agendada do Claude** | Claude faz curadoria e texto "pensando" a cada execução | Consome uso do seu plano; algumas etapas (API da Meta) dependem de rede liberada |

**Decidido (D6 e D11):** roda no Mac, como **tarefa agendada do Claude** às 9h e às 20h, usando o navegador integrado do app para o MakerWorld. Requisito: Mac ligado e app Claude aberto nesses horários. Se isso virar problema, migramos (GitHub Actions + outra fonte de imagens).

## 7. Riscos e mitigação

| Risco | Mitigação |
|---|---|
| Licença proíbe venda do modelo | Filtro obrigatório de licença + crédito ao criador |
| MakerWorld muda o layout do site | Coleta isolada num módulo; alerta quando falhar |
| Bloqueio por excesso de acesso ao MakerWorld | 1 coleta/dia, pausas, sem paralelismo |
| Token da Meta expira (60 dias) | Renovação automática + alerta 7 dias antes |
| Revisão do app Meta demora | Iniciar na Fase 0, em paralelo |
| Arte repetitiva cansa o público | 2–3 templates em rodízio + métricas |

## 8. Cronograma estimado

| Semana | Fases |
|---|---|
| 1 | Fase 0 + início do app Meta + Fase 1 |
| 2 | Fases 2, 3, 4, 5 |
| 3 | Fases 6, 7 + início do piloto |
| 4–5 | Piloto com aprovação + Fase 8 |
