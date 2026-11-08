# Relatório automático do Instagram (estratégia 1.1)

- Workflow: `.github/workflows/relatorio-instagram.yml` (repositório privado de design; cópia em `relatorio-instagram.yml.exemplo`).
- Script: `ferramentas/instagram/relatorio.py`.
- Coleta 4x por dia: stories no ar (somem em 24 h), posts e Reels dos últimos 30 dias, seguidores e números da conta do dia anterior. Os dados ficam em `instagram/dados/`.
- Toda segunda, por volta das 10h: resumo da semana em `instagram/relatorios/AAAA-MM-DD.md`, com issue aberta (chega por e-mail):
  - alcance por tema;
  - manhã × noite;
  - melhor story;
  - posts e Reels;
  - seguidores e cliques no link da bio.
- O tema de cada story vem da fila pública (`useled-stories-midia/fila/fila.json`, pelo `media_id`).

## Para ligar (dono da loja)
1. Neste repositório: Settings → Secrets and variables → Actions → **New repository secret**.
   - Nome: `IG_ACCESS_TOKEN`.
   - Valor: o mesmo token do publicador de stories (`stories/publicacao/credenciais.txt`).
2. Actions → "Relatório do Instagram" → Run workflow → `coletar`.
   - O log mostra se alguma métrica foi recusada.
   - Se aparecer erro de permissão: o app da Meta precisa ter `instagram_business_manage_insights` marcado, e o token tem que ser gerado de novo pelo Chrome/Safari.
3. Token renovado: o workflow `renovar-token` do repositório público atualiza só o segredo de lá.
   - Se o Instagram trocar o token, cole o novo aqui também.
   - Alternativa: dar ao `GH_PAT` permissão de Secrets neste repositório.
