#!/usr/bin/env python3
"""Lança/atualiza pedidos na aba "Vendas por pedido" da planilha de custos da USE LED.

Uso:
    python3 lancar_vendas.py PLANILHA.xlsx pedidos.json [catalogo_consumo.json]

pedidos.json = lista de objetos:
  {"data": "2026-11-15", "canal": "Shopee" | "TikTok Shop" | "Site" | "Venda direta",
   "pedido": "2611XXXXXXXXXX", "produto": "Porta-retratos Polaroid", "variacao": "Kit 5 Pastel",
   "unidades": 5, "status": "A liberar" | "Concluído" | "Cancelado" | "Devolução",
   "pago": 54.90, "recebido": 39.42, "obs": "..."}
  Campos de consumo opcionais (se ausentes, vêm do catálogo):
   filamento_g, impressao_h, imas, lampadas, rabichos, fita_cm, cabos, placas,
   outros_comp, embalagem, outros_custos

Regras:
- Pedido que já existe na aba: atualiza só status, pago, recebido e obs (não duplica).
- Pedido novo: grava na primeira linha vazia (as colunas calculadas já têm fórmula).
- Cancelado/Devolução sem envio: consumo zerado.
- Produto sem consumo conhecido: grava com consumo 0 e "CONSUMO A CONFIRMAR" na observação.
Imprime um JSON com o que foi feito. Não recalcula fórmulas: rode o LibreOffice depois
(soffice --headless --convert-to xlsx --outdir recalc PLANILHA.xlsx) para gravar os valores.
"""
import datetime as dt
import json
import re
import sys

import openpyxl

ABA = "Vendas por pedido"
PRIMEIRA = 4
COL = {"data": "A", "canal": "C", "pedido": "D", "produto": "E", "variacao": "F", "unidades": "G",
       "status": "H", "pago": "I", "recebido": "K", "filamento_g": "L", "impressao_h": "M",
       "imas": "N", "lampadas": "O", "rabichos": "P", "fita_cm": "Q", "cabos": "R", "placas": "S",
       "outros_comp": "T", "embalagem": "U", "outros_custos": "V", "obs": "AC"}
CONSUMO = ["filamento_g", "impressao_h", "imas", "lampadas", "rabichos", "fita_cm", "cabos",
           "placas", "outros_comp", "outros_custos"]


def consumo_do_catalogo(cat, produto, variacao, unidades):
    texto = f"{produto} {variacao}".lower()
    for item in cat.get("produtos", []):
        if any(re.search(p, texto) for p in item["padroes"]):
            por_un = item.get("por_unidade", {})
            res = {k: round(v * unidades, 3) for k, v in por_un.items()}
            res["embalagem"] = item.get("embalagem_por_pedido", cat.get("embalagem_padrao", 1.0))
            return res, item["nome"]
    return None, None


def main():
    planilha, arq_pedidos = sys.argv[1], sys.argv[2]
    cat = json.load(open(sys.argv[3], encoding="utf-8")) if len(sys.argv) > 3 else {}
    pedidos = json.load(open(arq_pedidos, encoding="utf-8"))
    wb = openpyxl.load_workbook(planilha)
    ws = wb[ABA]
    existentes = {}
    ultima = PRIMEIRA - 1
    for r in range(PRIMEIRA, ws.max_row + 1):
        if ws[f"A{r}"].value is not None:
            ultima = r
            ped = ws[f"D{r}"].value
            if ped not in (None, "", "—"):
                existentes[str(ped).strip()] = r
    feitos = {"novos": [], "atualizados": [], "a_confirmar": []}
    prox = ultima + 1
    for p in pedidos:
        ped = str(p["pedido"]).strip()
        if ped in existentes:
            r = existentes[ped]
            for k in ("status", "pago", "recebido"):
                if k in p and p[k] is not None:
                    ws[f"{COL[k]}{r}"] = p[k]
            if p.get("status") in ("Cancelado", "Devolução") and p.get("sem_envio", True):
                for k in CONSUMO + ["embalagem"]:
                    ws[f"{COL[k]}{r}"] = 0
            if p.get("obs"):
                antiga = ws[f"AC{r}"].value or ""
                if p["obs"] not in antiga:
                    ws[f"AC{r}"] = (antiga + "; " if antiga else "") + p["obs"]
            feitos["atualizados"].append(ped)
            continue
        r = prox
        prox += 1
        data = dt.datetime.strptime(p["data"], "%Y-%m-%d")
        ws[f"A{r}"] = data
        ws[f"A{r}"].number_format = "DD/MM/YYYY"
        for k in ("canal", "pedido", "produto", "variacao", "unidades", "status", "pago", "recebido"):
            ws[f"{COL[k]}{r}"] = p.get(k)
        obs = p.get("obs", "")
        cancelado = p.get("status") in ("Cancelado", "Devolução")
        if cancelado:
            cons = {k: 0 for k in CONSUMO + ["embalagem"]}
        elif any(k in p for k in CONSUMO):
            cons = {k: p.get(k, 0) for k in CONSUMO}
            cons["embalagem"] = p.get("embalagem", cat.get("embalagem_padrao", 1.0))
        else:
            cons, nome = consumo_do_catalogo(cat, p.get("produto", ""), p.get("variacao", ""),
                                              p.get("unidades", 1) or 1)
            if cons is None:
                cons = {k: 0 for k in CONSUMO}
                cons["embalagem"] = cat.get("embalagem_padrao", 1.0)
                obs = (obs + "; " if obs else "") + "CONSUMO A CONFIRMAR"
                feitos["a_confirmar"].append(ped)
        for k in CONSUMO + ["embalagem"]:
            ws[f"{COL[k]}{r}"] = cons.get(k, 0)
        if obs:
            ws[f"AC{r}"] = obs
        existentes[ped] = r
        feitos["novos"].append(ped)
    wb.save(planilha)
    print(json.dumps(feitos, ensure_ascii=False))


if __name__ == "__main__":
    main()
