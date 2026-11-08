# Estratégias de crescimento — Instagram @useledluminarias (proposta de 29/10/2026)

**Objetivo do dono da loja:** mais seguidores, conteúdo de mais qualidade e, por consequência, mais vendas no site (Nuvemshop, luminárias) e na Shopee.
**Status:** aprovado para começar a partir de 30/10. O dono da loja vai escolher por qual tópico começar.

**Diagnóstico:** hoje quase tudo são stories automáticos com modelos de outros criadores do MakerWorld (2 por dia), mais o compartilhamento do feed e o story semanal de produto aos domingos. Stories mantêm o perfil ativo, mas quase não alcançam quem ainda não segue e mostram pouco o produto da loja.

## Ordem sugerida para começar
1. Relatório automático do Instagram (1.1)
2. Página de links rastreável (1.2)
3. Resposta automática "comente LUZ" (3.1)
4. Depois disso: Reels, com os vídeos que o dono da loja gravar (2.1)

---

## 1. Medir antes de mexer (análise de dados)
- [ ] **1.1 Relatório semanal automático** (GitHub Actions, como o publicador).
  - **Story:** coleta diária, porque os números só ficam disponíveis por 24 horas: alcance, saídas, avanços, respostas.
  - **Conta:** seguidores, alcance e visitas ao perfil.
  - **Posts e Reels:** curtidas, salvamentos, compartilhamentos e alcance.
  - Toda segunda, um resumo para o dono da loja: o que funcionou por tema, horário e formato.
  - **Depende do dono da loja:** acesso ao painel de desenvolvedor da Meta (developers.facebook.com), onde está o app da automação (ver `meta_app.md`), para liberar a permissão `instagram_manage_insights`. Pode ser preciso gerar o token de novo; quem coloca o token é o dono da loja (segredo do GitHub).
- [ ] **1.2 Página de links na bio, com UTM.**
  - Links para Nuvemshop, Shopee, Polaroid, luminárias e WhatsApp/direct, para medir quantas vendas vêm do Instagram.
  - Pode ser um artefato ou uma página da Nuvemshop. Os links da Shopee já usam UTM nos pins do Pinterest (`utm_source=pinterest`); aqui seria `utm_source=instagram`.

## 2. Conteúdo próprio (é o que faz crescer)
- [ ] **2.1 Reels, 2 a 3 por semana.** É o formato que chega a quem não segue a conta. Os que mais funcionam:
  - timelapse da impressão;
  - a luminária acendendo;
  - montar o kit do Polaroid na geladeira;
  - "transformei isso nisso".

  Fluxo: o dono da loja grava e o Claude edita (cortes, textos e capa). A publicação pode ser automatizada, porque a API aceita Reels. Os roteiros estão em `shopee/videos/ROTEIROS_SHOPEE_VIDEO.md` e servem para Shopee Vídeo e Reels.
- [ ] **2.2 Carrosséis de feed para salvar**, ex.: "5 luminárias para presentear no Natal", "como escolher sua paleta". Salvamentos ajudam o alcance.
- [ ] **2.3 Mudar a mistura dos stories automáticos:** 1 por dia com produto da loja e 1 do MakerWorld (hoje são 2 do MakerWorld). Exige uma fila de artes de produto (fotos em `stories:produtos/`).

## 3. Transformar interesse em venda
- [ ] **3.1 Resposta automática por palavra-chave**, ex.: "Comente LUZ que eu te mando o link". Ferramenta nativa da Meta ou ManyChat (plano gratuito). Definir as palavras e os links de cada produto.
- [ ] **3.2 Instagram Shopping:** levar o catálogo da Nuvemshop para a Meta e marcar os produtos nos posts (preço e botão de compra). Conferir se a conta é elegível no Commerce Manager.
- [ ] **3.3 Stories manuais com figurinha de link e enquetes**, 1 a 2 vezes por semana: lançamento, promoção, "últimas unidades", "qual cor você escolheria?". A API não coloca figurinhas, por isso é manual. O Claude pode preparar a arte e o texto.
- [ ] **3.4 Destaques do perfil:** Luminárias, Porta-retratos, Como comprar, Avaliações. Fazer as capas no padrão da marca e revisar a bio.

## 4. Prova social e parcerias
- [ ] **4.1 Fotos de clientes:** ajustar o cartão de avaliação (`visibilidade/cartao_avaliacao_A4.pdf`) para pedir "poste e marque @useledluminarias". Republicar nos stories e nos Destaques.
- [ ] **4.2 Microinfluenciadores** (5 a 30 mil seguidores) de decoração, livros/fantasia e cultura geek: troca de produto por post em colaboração. Fazer uma lista de perfis e um texto de abordagem. Referência: 7 das ~8 vendas recentes do Polaroid vieram de afiliados da Shopee.

## 5. Calendário e anúncio pago
- [ ] **5.1 Calendário editorial por data:** Black Friday (27/11), Natal, amigo secreto, Ano Novo, Dia dos Namorados (12/06). Ligar o calendário à fila de stories (`temas.json`, `foco_semana`).
- [ ] **5.2 Impulsionar o Reel de melhor resultado** com R$ 10 a R$ 15 por dia, só depois de existirem Reels e o relatório (1.1) mostrar qual foi melhor. Separado do anúncio da Shopee (Polaroid, R$ 5/dia, depois da reposição dos ímãs).

---

**Restrições que continuam valendo:**
- Tokens e logins são sempre do dono da loja.
- Nada de custos ou credenciais no repositório público.
- Publicar conteúdo público novo, como um Reel ou um carrossel, só com o "ok" do dono da loja, até ele definir que pode ser automático.
