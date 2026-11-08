# Rotina: Pinterest (USE LED)

## Duas fontes de pins
1. **Luminárias (Nuvemshop)**: app oficial do Pinterest na Nuvemshop. Ele verifica o site useled.lojavirtualnuvem.com.br e sincroniza o catálogo. Os pins de produto são criados e atualizados sozinhos.
2. **Produtos da Shopee**: planilha CSV mensal de criação em massa. O Claude gera as artes (1000×1500) e a planilha. O dono da loja sobe em Pinterest › Criar › "Criar Pins em massa". Os pins saem 1 por dia, às 12h de Brasília.

Por que não RSS nem API: a publicação automática por RSS exige que o link do pin seja do site verificado, então não aceita link da Shopee. A API em modo teste cria pins visíveis só para o dono.

## Mensal (até o dia 25)
- Gerar o lote do mês seguinte com `python gerar_pins.py AAAA-MM-DD` (pasta pinterest/). A cada rodada, trocar os títulos e incluir os produtos novos.
- As imagens ficam em `Elielsonbo/useled-stories-midia`, branch `stories`, pasta `pinterest/`.
- O dono da loja sobe o CSV (até 200 pins por arquivo).

## Pastas (boards)
Decoração 3D para Casa · Organização de Mesa e Escritório · Banheiro e Penteadeira · Presentes Criativos · Porta-retratos e Ímãs de Geladeira. O Pinterest cria a pasta automaticamente se ela não existir.

## Lote 1 (out–nov/2026)
22 pins de 30/10 a 20/11, com 2 títulos por produto e 11 produtos ativos. O Polaroid só entra em 09/11 e 20/11, por causa da reposição de ímãs.
Links com `utm_source=pinterest`, para medir o tráfego.
