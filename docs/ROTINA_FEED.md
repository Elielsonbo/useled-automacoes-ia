# Rotina: compartilhar posts do feed nos stories

Roda **sozinha no GitHub Actions**, sem depender do Mac. Fica no repositório `Elielsonbo/useled-stories-midia`:
- workflow: `.github/workflows/compartilhar-feed.yml`
- script: `scripts/compartilhar_feed.py`
- modelo da arte: `arte/story_feed.html`

## Quando
- **A cada 2 dias**, a partir de 26/10/2026 (dias pares contados dessa data).
- Período: **entre 11h e 18h** (Brasília), no máximo 1 por dia. Fica no meio dos stories das 9h e das 20h.
- O GitHub atrasa os agendamentos, então há 4 disparos (10h17 a 13h17). Se já houve compartilhamento no dia, os disparos seguintes não fazem nada.

## O que faz
1. Lê os posts do feed da @useledluminarias pela API (fotos, carrosséis e vídeos/reels) dos **últimos 365 dias**.
2. Escolhe o **mais recente ainda não compartilhado**. Se todos já foram, repete o que foi compartilhado há mais tempo (no mínimo 30 dias atrás).
3. Gera a arte 1080×1920 no padrão USE LED:
   - selo "No nosso feed";
   - título "Tem post novo por aqui" (post de até 14 dias) ou "Já viu este post?";
   - a imagem do post (a capa, no caso de vídeo);
   - um trecho da legenda, sem hashtags;
   - "Veja o post completo no perfil" ou "Assista no nosso perfil".
4. Envia a imagem para a branch `stories` (`feed/AAAA-MM-DD_<id>.jpg`) e publica como story.
5. Grava o histórico em `main:fila/compartilhados.json`.

## Limitação
A API do Instagram **não permite** o compartilhamento nativo de post no story (com o adesivo clicável do post). Por isso a arte convida a ver no perfil.

## Comandos úteis
- Testar sem publicar: Actions › "Compartilhar post do feed" › Run workflow › modo `teste` e `forcar` marcado. A arte vai para `stories:feed/teste_*.jpg`.
- Publicar agora, fora do dia: modo `publicar` com `forcar` marcado.
