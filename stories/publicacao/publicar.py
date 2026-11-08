"""Publica um story no Instagram da loja via API oficial (Instagram Login).

Uso:
    python publicar.py <URL_PUBLICA_DO_JPEG>
    python publicar.py --verificar        # só valida o token
    python publicar.py --renovar          # renova o token (60 dias) se faltar < 15 dias

Lê as credenciais de `credenciais.txt` (mesma pasta). Imprime JSON com o resultado.
"""
import json
import sys
import time
import urllib.error
import urllib.parse
import urllib.request
from datetime import datetime, timedelta
from pathlib import Path

AQUI = Path(__file__).resolve().parent
CRED = AQUI / "credenciais.txt"
API = "https://graph.instagram.com/v21.0"


def ler_cred() -> dict:
    cfg = {}
    for linha in CRED.read_text(encoding="utf-8").splitlines():
        linha = linha.strip()
        if linha and not linha.startswith("#") and "=" in linha:
            k, v = linha.split("=", 1)
            cfg[k.strip()] = v.strip().strip('"').strip("'")
    if not cfg.get("IG_ACCESS_TOKEN"):
        raise SystemExit("IG_ACCESS_TOKEN vazio em credenciais.txt")
    return cfg


def salvar_cred(cfg: dict) -> None:
    linhas = CRED.read_text(encoding="utf-8").splitlines()
    novas, vistos = [], set()
    for l in linhas:
        k = l.split("=", 1)[0].strip() if "=" in l and not l.lstrip().startswith("#") else None
        if k in cfg:
            novas.append(f"{k}={cfg[k]}"); vistos.add(k)
        else:
            novas.append(l)
    novas += [f"{k}={v}" for k, v in cfg.items() if k not in vistos]
    CRED.write_text("\n".join(novas) + "\n", encoding="utf-8")


def chamar(metodo: str, caminho: str, token: str, **params) -> dict:
    params["access_token"] = token
    dados = urllib.parse.urlencode(params).encode()
    if metodo == "GET":
        req = urllib.request.Request(f"{caminho}?{dados.decode()}")
    else:
        req = urllib.request.Request(caminho, data=dados, method="POST")
    try:
        with urllib.request.urlopen(req, timeout=60) as r:
            return json.load(r)
    except urllib.error.HTTPError as e:
        try:
            corpo = json.load(e)
        except Exception:
            corpo = {"raw": e.read().decode(errors="ignore")[:500]}
        raise RuntimeError(f"HTTP {e.code}: {json.dumps(corpo, ensure_ascii=False)}")


def publicar_story(url_imagem: str) -> dict:
    cfg = ler_cred()
    tok, uid = cfg["IG_ACCESS_TOKEN"], cfg["IG_USER_ID"]

    # 1) cria o container do story
    cont = chamar("POST", f"{API}/{uid}/media", tok, image_url=url_imagem, media_type="STORIES")
    cid = cont["id"]

    # 2) aguarda o Instagram processar a imagem
    status = None
    for _ in range(30):
        status = chamar("GET", f"{API}/{cid}", tok, fields="status_code,status").get("status_code")
        if status == "FINISHED":
            break
        if status in ("ERROR", "EXPIRED"):
            raise RuntimeError(f"Container {cid} falhou: {status}")
        time.sleep(4)
    if status != "FINISHED":
        raise RuntimeError(f"Container {cid} não ficou pronto (status={status})")

    # 3) publica
    pub = chamar("POST", f"{API}/{uid}/media_publish", tok, creation_id=cid)
    mid = pub["id"]
    info = {}
    try:
        info = chamar("GET", f"{API}/{mid}", tok, fields="id,media_type,timestamp,permalink")
    except RuntimeError:
        pass
    return {"ok": True, "container_id": cid, "media_id": mid, **info}


def verificar() -> dict:
    cfg = ler_cred()
    me = chamar("GET", f"{API}/me", cfg["IG_ACCESS_TOKEN"], fields="user_id,username,account_type")
    lim = chamar("GET", f"{API}/{cfg['IG_USER_ID']}/content_publishing_limit",
                 cfg["IG_ACCESS_TOKEN"], fields="quota_usage,config")
    return {"ok": True, "conta": me.get("username"), "uso_24h": lim["data"][0]["quota_usage"],
            "token_expira_em": cfg.get("IG_TOKEN_EXPIRA_EM", "desconhecido")}


def renovar(forcar: bool = False) -> dict:
    cfg = ler_cred()
    expira = cfg.get("IG_TOKEN_EXPIRA_EM")
    if expira and not forcar:
        faltam = datetime.fromisoformat(expira) - datetime.now()
        if faltam > timedelta(days=15):
            return {"ok": True, "renovado": False, "faltam_dias": faltam.days}
    r = chamar("GET", "https://graph.instagram.com/refresh_access_token",
               cfg["IG_ACCESS_TOKEN"], grant_type="ig_refresh_token")
    nova_exp = (datetime.now() + timedelta(seconds=int(r.get("expires_in", 0)))).isoformat(timespec="seconds")
    salvar_cred({"IG_ACCESS_TOKEN": r["access_token"], "IG_TOKEN_EXPIRA_EM": nova_exp})
    return {"ok": True, "renovado": True, "expira_em": nova_exp}


if __name__ == "__main__":
    arg = sys.argv[1] if len(sys.argv) > 1 else ""
    try:
        if arg == "--verificar":
            out = verificar()
        elif arg == "--renovar":
            out = renovar(forcar="--forcar" in sys.argv)
        elif arg.startswith("https://"):
            out = publicar_story(arg)
        else:
            raise SystemExit(__doc__)
        print(json.dumps(out, ensure_ascii=False))
    except RuntimeError as e:
        print(json.dumps({"ok": False, "erro": str(e)}, ensure_ascii=False))
        sys.exit(1)
