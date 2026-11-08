"""Relatório do Instagram @useledluminarias (estratégia 1.1).

Dois modos (variável MODO ou 1º argumento):
- coletar: roda várias vezes ao dia. Guarda números dos stories no ar (eles
  somem em 24 h), dos posts/Reels recentes e da conta (dia anterior).
- resumo: toda segunda. Lê os últimos 7 dias, escreve
  instagram/relatorios/AAAA-MM-DD.md e imprime o texto (o workflow abre uma
  issue com ele, para chegar por e-mail).

Variáveis: IG_ACCESS_TOKEN (segredo), IG_USER_ID.
Dados em instagram/dados/ (repositório privado). Nada de token em arquivo.
"""
import json
import os
import sys
import urllib.error
import urllib.parse
import urllib.request
from collections import defaultdict
from datetime import datetime, timedelta
from pathlib import Path
from zoneinfo import ZoneInfo

SP = ZoneInfo("America/Sao_Paulo")
API = "https://graph.instagram.com/v23.0"
RAIZ = Path(__file__).resolve().parents[2] / "instagram"
DADOS = RAIZ / "dados"
FILA_URL = "https://raw.githubusercontent.com/Elielsonbo/useled-stories-midia/main/fila/fila.json"

M_STORY = ["reach", "views", "replies", "shares", "total_interactions", "follows", "profile_visits"]
M_MEDIA = ["reach", "views", "likes", "comments", "saved", "shares", "total_interactions"]
M_CONTA = ["reach", "views", "profile_views", "website_clicks", "accounts_engaged",
           "total_interactions", "follows_and_unfollows"]


# ---------- API ----------
def token():
    """Aceita o segredo colado com sobras: 'IG_ACCESS_TOKEN=', aspas, espaços, quebras de linha."""
    t = os.environ["IG_ACCESS_TOKEN"].strip()
    if t.upper().startswith("IG_ACCESS_TOKEN"):
        t = t.split("=", 1)[-1]
    t = t.strip().strip('"').strip("'")
    return t.split()[0] if t else t


def chamar(caminho, **params):
    params["access_token"] = token()
    url = f"{API}/{caminho}?{urllib.parse.urlencode(params)}"
    try:
        with urllib.request.urlopen(url, timeout=60) as r:
            return json.load(r)
    except urllib.error.HTTPError as e:
        corpo = e.read().decode(errors="ignore")[:300]
        raise RuntimeError(f"HTTP {e.code} em {caminho}: {corpo}") from None


def metrica(id_, nome, **extra):
    """Uma métrica por chamada: se a Meta não aceitar uma, as outras seguem."""
    try:
        d = chamar(f"{id_}/insights", metric=nome, **extra).get("data", [])
    except RuntimeError as e:
        return None, str(e)
    if not d:
        return None, "vazio"
    m = d[0]
    if "total_value" in m:
        tv = m["total_value"]
        if "breakdowns" in tv:
            return {r["dimension_values"][0]: r["value"]
                    for b in tv["breakdowns"] for r in b.get("results", [])}, None
        return tv.get("value"), None
    vals = m.get("values") or []
    return (vals[-1].get("value") if vals else None), None


def insights(id_, nomes, **extra):
    out, erros = {}, {}
    for n in nomes:
        v, err = metrica(id_, n, **extra)
        if err:
            erros[n] = err
        else:
            out[n] = v
    return out, erros


# ---------- arquivos ----------
def ler_jsonl(nome):
    p = DADOS / nome
    if not p.exists():
        return []
    return [json.loads(l) for l in p.read_text(encoding="utf-8").splitlines() if l.strip()]


def gravar_por_chave(nome, registros, chave):
    """Atualiza (upsert) mantendo a leitura mais recente de cada item."""
    atual = {r[chave]: r for r in ler_jsonl(nome)}
    for r in registros:
        atual[r[chave]] = {**atual.get(r[chave], {}), **r}
    DADOS.mkdir(parents=True, exist_ok=True)
    linhas = sorted(atual.values(), key=lambda r: r.get("timestamp") or r.get("dia") or "")
    (DADOS / nome).write_text("\n".join(json.dumps(r, ensure_ascii=False) for r in linhas) + "\n",
                              encoding="utf-8")


def fila_por_media():
    try:
        with urllib.request.urlopen(FILA_URL, timeout=30) as r:
            itens = json.load(r)["itens"]
        return {i["media_id"]: i for i in itens if i.get("media_id")}
    except Exception as e:  # o relatório segue sem o tema
        print(f"aviso: não li a fila ({e})")
        return {}


# ---------- coletar ----------
def coletar():
    uid = os.environ["IG_USER_ID"]
    agora = datetime.now(SP)
    erros = {}
    t = token()
    # diagnóstico sem expor o token: só tamanho e se tem o formato esperado
    print(f"token: {len(t)} caracteres, começa com 'IG': {t.startswith('IG')}, "
          f"só letras/números: {t.isalnum()}")

    # 1) stories no ar
    fila = fila_por_media()
    stories = []
    for s in chamar(f"{uid}/stories", fields="id,timestamp,media_type,permalink").get("data", []):
        num, err = insights(s["id"], M_STORY)
        nav, err2 = metrica(s["id"], "navigation", breakdown="story_navigation_action_type")
        if isinstance(nav, dict):
            num["navegacao"] = nav
        erros.update({f"story.{k}": v for k, v in err.items()})
        f = fila.get(s["id"], {})
        stories.append({"id": s["id"], "timestamp": s.get("timestamp"), "tipo": s.get("media_type"),
                        "tema": f.get("tema", "manual"), "titulo": f.get("titulo"),
                        "coletado_em": agora.isoformat(timespec="minutes"), **num})
    gravar_por_chave("stories.jsonl", stories, "id")

    # 2) posts e Reels dos últimos 30 dias
    posts = []
    lim = agora - timedelta(days=30)
    campos = "id,timestamp,media_type,media_product_type,permalink,caption,like_count,comments_count"
    for m in chamar(f"{uid}/media", fields=campos, limit=30).get("data", []):
        ts = datetime.fromisoformat(m["timestamp"].replace("+0000", "+00:00"))
        if ts < lim:
            continue
        num, err = insights(m["id"], M_MEDIA)
        erros.update({f"post.{k}": v for k, v in err.items()})
        posts.append({"id": m["id"], "timestamp": m["timestamp"], "tipo": m.get("media_product_type") or m.get("media_type"),
                      "permalink": m.get("permalink"), "legenda": (m.get("caption") or "")[:80],
                      "coletado_em": agora.isoformat(timespec="minutes"), **num})
    gravar_por_chave("posts.jsonl", posts, "id")

    # 3) conta: seguidores agora + números de ontem
    perfil = chamar(uid, fields="followers_count,follows_count,media_count")
    ontem = (agora - timedelta(days=1)).date()
    ini = int(datetime(ontem.year, ontem.month, ontem.day, tzinfo=SP).timestamp())
    num, err = insights(uid, M_CONTA, period="day", metric_type="total_value",
                        since=ini, until=ini + 86400)
    erros.update({f"conta.{k}": v for k, v in err.items()})
    gravar_por_chave("conta.jsonl", [{"dia": ontem.isoformat(), "seguidores": perfil.get("followers_count"),
                                      "seguindo": perfil.get("follows_count"), **num}], "dia")

    print(json.dumps({"stories": len(stories), "posts": len(posts),
                      "seguidores": perfil.get("followers_count")}, ensure_ascii=False))
    if erros:
        # Uma métrica recusada não derruba a coleta; fica registrado no log.
        print("métricas recusadas pela Meta:")
        for k, v in sorted(erros.items()):
            print(f"  {k}: {v[:160]}")
    if not stories and not posts and "conta.reach" in erros and "permission" in erros["conta.reach"].lower():
        sys.exit("Sem permissão de insights no token. Ver instagram/README_RELATORIO.md.")


# ---------- resumo ----------
def n(v):
    return v if isinstance(v, (int, float)) else 0


def fmt(v):
    return f"{v:,.0f}".replace(",", ".")


def resumo():
    hoje = datetime.now(SP).date()
    ini = hoje - timedelta(days=7)
    no_periodo = lambda ts: ts and ini <= datetime.fromisoformat(ts.replace("+0000", "+00:00")).astimezone(SP).date() < hoje

    st = [s for s in ler_jsonl("stories.jsonl") if no_periodo(s.get("timestamp"))]
    ps = [p for p in ler_jsonl("posts.jsonl") if no_periodo(p.get("timestamp"))]
    ct = [c for c in ler_jsonl("conta.jsonl") if ini.isoformat() <= c["dia"] < hoje.isoformat()]
    ct_ant = [c for c in ler_jsonl("conta.jsonl")
              if (ini - timedelta(days=7)).isoformat() <= c["dia"] < ini.isoformat()]

    L = [f"# Instagram @useledluminarias: semana de {ini:%d/%m} a {hoje - timedelta(days=1):%d/%m}", ""]

    # conta
    if ct:
        seg_fim = ct[-1].get("seguidores")
        seg_ini = (ct_ant[-1] if ct_ant else ct[0]).get("seguidores")
        alc = sum(n(c.get("reach")) for c in ct)
        alc_ant = sum(n(c.get("reach")) for c in ct_ant)
        vis = sum(n(c.get("profile_views")) for c in ct)
        cli = sum(n(c.get("website_clicks")) for c in ct)
        L += ["## Conta",
              f"- Seguidores: **{fmt(seg_fim or 0)}** ({'+' if n(seg_fim) - n(seg_ini) >= 0 else ''}{n(seg_fim) - n(seg_ini)} na semana)",
              f"- Alcance somado dos dias: {fmt(alc)}" + (f" (semana anterior: {fmt(alc_ant)})" if ct_ant else ""),
              f"- Visitas ao perfil: {fmt(vis)} · cliques no link da bio: {fmt(cli)}", ""]

    # stories
    if st:
        L += ["## Stories", f"{len(st)} stories na semana. Alcance médio: **{fmt(sum(n(s.get('reach')) for s in st) / len(st))}**.", ""]
        por_tema = defaultdict(list)
        for s in st:
            por_tema[s.get("tema") or "manual"].append(s)
        L += ["| Tema | Stories | Alcance médio | Saídas por story | Respostas |", "|---|---|---|---|---|"]
        for tema, xs in sorted(por_tema.items(), key=lambda kv: -sum(n(s.get("reach")) for s in kv[1]) / len(kv[1])):
            saidas = sum(n((s.get("navegacao") or {}).get("tap_exit")) for s in xs)
            L.append(f"| {tema} | {len(xs)} | {fmt(sum(n(s.get('reach')) for s in xs) / len(xs))} | "
                     f"{saidas / len(xs):.1f} | {sum(n(s.get('replies')) for s in xs)} |")
        manha = [s for s in st if datetime.fromisoformat(s["timestamp"].replace("+0000", "+00:00")).astimezone(SP).hour < 16]
        noite = [s for s in st if s not in manha]
        if manha and noite:
            am = sum(n(s.get("reach")) for s in manha) / len(manha)
            pm = sum(n(s.get("reach")) for s in noite) / len(noite)
            L += ["", f"Horário: manhã {fmt(am)} de alcance médio × noite {fmt(pm)}."]
        top = max(st, key=lambda s: n(s.get("reach")))
        L += [f"Melhor story: **{top.get('titulo') or top['id']}** ({top.get('tema')}), alcance {fmt(n(top.get('reach')))}.", ""]

    # posts
    if ps:
        L += ["## Posts e Reels", "| Data | Tipo | Alcance | Curtidas | Salvos | Compart. | Legenda |", "|---|---|---|---|---|---|---|"]
        for p in sorted(ps, key=lambda p: -n(p.get("reach"))):
            d = datetime.fromisoformat(p["timestamp"].replace("+0000", "+00:00")).astimezone(SP)
            L.append(f"| {d:%d/%m} | {p.get('tipo')} | {fmt(n(p.get('reach')))} | {n(p.get('likes'))} | "
                     f"{n(p.get('saved'))} | {n(p.get('shares'))} | {p.get('legenda', '').replace('|', '/')[:50]} |")
        L.append("")

    if not (ct or st or ps):
        L += ["Ainda não há dados coletados neste período."]

    L += ["---", "Gerado automaticamente pelo workflow *Relatório do Instagram* (useled-design)."]
    texto = "\n".join(L)
    (RAIZ / "relatorios").mkdir(parents=True, exist_ok=True)
    (RAIZ / "relatorios" / f"{hoje.isoformat()}.md").write_text(texto + "\n", encoding="utf-8")
    print(texto)


if __name__ == "__main__":
    modo = (sys.argv[1] if len(sys.argv) > 1 else os.environ.get("MODO", "coletar")).strip()
    {"coletar": coletar, "resumo": resumo}[modo]()
