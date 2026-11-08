"""Histórico de stories publicados — fonte única para os links dos projetos.

O arquivo `historico.csv` (nesta pasta) abre no Numbers/Excel e tem uma linha
por story, com o link do modelo no MakerWorld, criador e licença.

Uso no código:
    from historico import registrar, ja_publicado
    if not ja_publicado(model_id, dias=30): ...
    registrar({...})
"""
import csv
from datetime import date, datetime, timedelta
from pathlib import Path

ARQUIVO = Path(__file__).resolve().parent / "historico.csv"
COLUNAS = [
    "data", "horario", "tema", "titulo_story", "modelo", "criador",
    "licenca", "link_makerworld", "filamento_g", "tempo_impressao_h",
    "custo_estimado", "perfil_impressao", "arte", "status", "id_instagram", "model_id",
]


def _garantir_arquivo():
    if not ARQUIVO.exists():
        with ARQUIVO.open("w", newline="", encoding="utf-8-sig") as f:
            csv.writer(f, delimiter=";").writerow(COLUNAS)


def registrar(linha: dict) -> None:
    """Acrescenta uma linha. Campos ausentes ficam vazios.

    Se vierem filamento_g e tempo_impressao_h, calcula o custo estimado.
    """
    if linha.get("filamento_g") and linha.get("tempo_impressao_h") and not linha.get("custo_estimado"):
        from custo import custo_estimado, formatar_brl
        linha["custo_estimado"] = formatar_brl(
            custo_estimado(float(linha["filamento_g"]), float(linha["tempo_impressao_h"])))
    _garantir_arquivo()
    linha = {"data": date.today().isoformat(),
             "horario": datetime.now().strftime("%H:%M"), **linha}
    with ARQUIVO.open("a", newline="", encoding="utf-8-sig") as f:
        csv.writer(f, delimiter=";").writerow([linha.get(c, "") for c in COLUNAS])


def ler() -> list[dict]:
    _garantir_arquivo()
    with ARQUIVO.open(newline="", encoding="utf-8-sig") as f:
        return list(csv.DictReader(f, delimiter=";"))


def ja_publicado(model_id, dias: int = 30) -> bool:
    """True se o modelo saiu nos últimos `dias` (evita repetição)."""
    limite = (date.today() - timedelta(days=dias)).isoformat()
    return any(l["model_id"] == str(model_id) and l["data"] >= limite
               and l["status"] in ("publicado", "aprovado") for l in ler())


if __name__ == "__main__":
    _garantir_arquivo()
    print(f"{len(ler())} registros em {ARQUIVO}")


FILA_URL = "https://raw.githubusercontent.com/Elielsonbo/useled-stories-midia/main/fila/fila.json"


def sincronizar_com_fila(fila: dict | None = None) -> int:
    """Marca como 'publicado' as linhas cuja arte já saiu pelo GitHub Actions.

    Lê a fila pública (ou a passada como argumento) e atualiza status, data,
    horário real e id do Instagram. Devolve quantas linhas mudaram.
    """
    if fila is None:
        import json
        import urllib.request
        with urllib.request.urlopen(FILA_URL, timeout=30) as r:
            fila = json.load(r)
    publicados = {i["url"]: i for i in fila.get("itens", []) if i.get("status") == "publicado"}
    linhas = ler()
    mudou = 0
    for l in linhas:
        p = publicados.get(l.get("arte"))
        if p and l.get("status") != "publicado":
            quando = p.get("publicado_em", "")
            l.update(status="publicado", id_instagram=p.get("media_id", ""),
                     data=quando[:10] or l["data"], horario=quando[11:16] or l["horario"])
            mudou += 1
    if mudou:
        with ARQUIVO.open("w", newline="", encoding="utf-8-sig") as f:
            w = csv.writer(f, delimiter=";")
            w.writerow(COLUNAS)
            for l in linhas:
                w.writerow([l.get(c, "") for c in COLUNAS])
    return mudou


def registrar_estoque(caminho_json) -> int:
    """Acrescenta ao histórico as linhas de um estoque (status agendado/reserva)."""
    import json
    from pathlib import Path
    linhas = json.loads(Path(caminho_json).read_text(encoding="utf-8"))
    ja = {l.get("arte") for l in ler()}
    n = 0
    for l in linhas:
        if l.get("arte") not in ja:
            registrar(l)
            n += 1
    return n
