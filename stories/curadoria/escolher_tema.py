"""Escolhe o tema do próximo story.

Regras:
- só entram temas cuja janela sazonal inclui hoje (ou sem janela);
- o tema do story anterior não se repete;
- entre os elegíveis, sorteio ponderado pelo `peso` de temas.json,
  descontando temas muito usados nos últimos 7 dias.

Uso: python escolher_tema.py   -> imprime JSON {id, chip, busca}
"""
import csv
import json
import random
from datetime import date, timedelta
from pathlib import Path

RAIZ = Path(__file__).resolve().parents[1]
TEMAS = json.loads((RAIZ / "temas.json").read_text(encoding="utf-8"))["temas"]
HIST = RAIZ / "dados" / "historico.csv"


def na_janela(janela, hoje: date) -> bool:
    if not janela:
        return True
    ini, fim = (tuple(map(int, x.split("-"))) for x in janela)
    d = (hoje.month, hoje.day)
    return ini <= d <= fim if ini <= fim else (d >= ini or d <= fim)  # janela que vira o ano


def historico() -> list[dict]:
    if not HIST.exists():
        return []
    with HIST.open(newline="", encoding="utf-8-sig") as f:
        return [l for l in csv.DictReader(f, delimiter=";") if l.get("status") == "publicado"]


def escolher(hoje: date | None = None) -> dict:
    hoje = hoje or date.today()
    hist = historico()
    ultimo = hist[-1]["tema"] if hist else None
    semana = (hoje - timedelta(days=7)).isoformat()
    usos = {}
    for l in hist:
        if l["data"] >= semana:
            usos[l["tema"]] = usos.get(l["tema"], 0) + 1

    elegiveis = [t for t in TEMAS if na_janela(t.get("janela"), hoje) and t["id"] != ultimo]
    if not elegiveis:
        elegiveis = [t for t in TEMAS if na_janela(t.get("janela"), hoje)]
    pesos = [t["peso"] / (1 + usos.get(t["id"], 0)) for t in elegiveis]
    t = random.choices(elegiveis, weights=pesos, k=1)[0]
    return {"id": t["id"], "chip": t["chip"], "busca": t["busca"]}


if __name__ == "__main__":
    print(json.dumps(escolher(), ensure_ascii=False))
