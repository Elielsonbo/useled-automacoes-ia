# Rotina semanal: lançamento de vendas na planilha

Executada por uma **tarefa agendada do Claude** toda **segunda de manhã**, no computador da loja. É uma automação independente da montagem de stories: roda antes dela, para as duas não disputarem o computador e o navegador.

**O que faz:** lança na planilha de custos os pedidos da semana anterior das três lojas (Shopee, TikTok Shop e site Nuvemshop), atualiza o status de pedidos que ainda estavam "A liberar", recalcula a planilha e envia ao dono o resumo da semana (faturamento, taxas, custo, lucro e margem).

## Arquivos
- `vendas/lancar_vendas.py`: grava os pedidos na aba "Vendas por pedido" e não duplica (chave = nº do pedido). As colunas de custo e lucro já têm fórmulas na planilha.
- `vendas/catalogo_consumo.exemplo.json`: formato do catálogo de consumo por peça (filamento, horas de impressão, componentes). O catálogo real fica só no computador da loja.
- `vendas/pedidos.exemplo.json`: formato da entrada do script.
- A planilha e os lançamentos reais **não** ficam neste repositório.

## 1. Período
- Semana da planilha = segunda a domingo (aba "Resumo semanal", que soma tudo por fórmulas).
- O agente lança **todos os pedidos depois do último já lançado**. Se uma execução falhar, a seguinte recupera o atraso sozinha.
- Linhas "A liberar" são revisadas: podem ter virado Concluído, Cancelado ou Devolução.

## 2. Coleta
- Pelo navegador do app Claude no computador da loja, com as sessões já abertas pelo dono.
- Se alguma plataforma pedir login, captcha ou verificação, o agente **pula essa plataforma e avisa**. Não digita senha nem contorna bloqueio.
- Valor recebido: o líquido informado pela plataforma. Se ainda não estiver disponível, o agente estima pela tabela pública de comissões e marca "recebido estimado".

## 3. Lançamento
- Produto com **nome curto** do catálogo (não o título longo do anúncio).
- `unidades` = número de peças (Kit 10 = 10).
- Cancelado/Devolução sem envio: consumo zerado.
- Produto sem consumo conhecido: entra com consumo 0 e a observação "CONSUMO A CONFIRMAR", para o dono completar.

```
python3 vendas/lancar_vendas.py planilha.xlsx lancamento.json catalogo_consumo.json
soffice --headless --convert-to xlsx --outdir recalc planilha.xlsx   # grava os valores das fórmulas
```
O agente confere a cópia recalculada (sem `#REF!`/`#VALUE!`, totais coerentes) antes de devolver a planilha.

## 4. Aviso ao dono
Mensagem curta com: pedidos, pago, taxas, recebido, custo, lucro e margem da semana; comparação com a anterior; divisão por canal; produto campeão; pendências.

## Limites
- Não muda preços, não responde clientes, não emite nota fiscal e não envia nada em nome do dono.
- Não grava nome, CPF ou endereço de cliente na planilha.
