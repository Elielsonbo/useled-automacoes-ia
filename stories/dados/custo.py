"""Custo estimado de produção de um modelo 3D (uso interno).

A base de custos real fica em `custos.json` (fora do Git, ver .gitignore).
Copie `custos.exemplo.json` para `custos.json` e preencha os valores.
"""
import json
from pathlib import Path

_ARQ = Path(__file__).with_name("custos.json")
_BASE = json.loads(_ARQ.read_text(encoding="utf-8")) if _ARQ.exists() else {
    "por_grama": 0.0, "por_hora": 0.0, "mao_de_obra": 0.0}


def custo_estimado(filamento_g: float, tempo_h: float) -> float:
    return round(filamento_g * _BASE["por_grama"] + tempo_h * _BASE["por_hora"] + _BASE["mao_de_obra"], 2)


def formatar_brl(valor: float) -> str:
    return f"R$ {valor:,.2f}".replace(",", "X").replace(".", ",").replace("X", ".")
