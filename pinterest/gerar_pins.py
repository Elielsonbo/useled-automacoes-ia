"""Gera os pins da Shopee (1000x1500, padrão USE LED) e a planilha CSV de criação em massa do Pinterest.

Uso: python gerar_pins.py AAAA-MM-DD   (data do primeiro pin; 1 pin por dia, às 12h de Brasília)
Saída: out/*.jpg e out/pins_AAAA-MM.csv
"""
import csv
import shutil
import sys
from datetime import date, timedelta
from pathlib import Path

from playwright.sync_api import sync_playwright

R = Path(__file__).parent
ASSETS = R / "assets"  # fontes e logo da marca
OUT = R / "out"
SHOP = 555488051
URL_IMG = "https://raw.githubusercontent.com/Elielsonbo/useled-stories-midia/stories/pinterest/{arq}"
UTM = "?utm_source=pinterest&utm_medium=social&utm_campaign=pins"

# id, capa, pasta (board), títulos A/B, descrição, palavras-chave
PRODUTOS = [
    ("58263428271", "58263428271.jpg", "Porta-retratos e Ímãs de Geladeira",
     ["Porta-retratos ondulados<br>para fotos Instax", "Sua geladeira<br>cheia de memórias"],
     "Porta-retrato magnético ondulado para fotos Instax Mini. Kits de 2, 5 ou 10 em 12 cores (paleta colorida ou neutra). Ímã forte no verso, impressão 3D, feito sob encomenda. Ideia de presente e decoração de geladeira.",
     "porta retrato instax, decoração de geladeira, ímã de geladeira, presente criativo, decoração colorida"),
    ("58218531411", "58218531411.jpg", "Decoração 3D para Casa",
     ["Porta-copos Monstera<br>com vasinho", "Mesa posta com<br>folhas de Monstera"],
     "Kit porta-copos em formato de folha de Costela de Adão (Monstera) com vasinho decorativo que guarda as peças. Impressão 3D, ótimo para mesa posta, café e presente para quem ama plantas.",
     "porta copos monstera, costela de adão, mesa posta, decoração com plantas, presente criativo"),
    ("22099479782", "22099479782.jpg", "Decoração 3D para Casa",
     ["Porta-copos Monstera<br>6 peças + base", "Folhas que protegem<br>a sua mesa"],
     "Kit com 6 porta-copos em formato de folha Monstera e base organizadora. Design moderno, impressão 3D, deixa a mesa de centro e a mesa posta mais bonitas.",
     "porta copos, monstera, decoração moderna, mesa de centro, casa com plantas"),
    ("58260337368", "58260337368.jpg", "Decoração 3D para Casa",
     ["Vasinhos para suculentas<br>em impressão 3D", "Um cantinho verde<br>na sua mesa"],
     "Kit de 3 vasos para suculentas com texturas modernas e bandeja. Feitos em impressão 3D, perfeitos para mesa de escritório, estante e sala.",
     "vaso suculenta, cachepot, decoração escritório, vasos modernos, plantas em casa"),
    ("58260038457", "58260038457.jpg", "Organização de Mesa e Escritório",
     ["Kit organizador<br>de mesa completo", "Mesa arrumada,<br>cabeça leve"],
     "Kit organizador de mesa com suporte de celular, porta-canetas e porta-objetos. Visual minimalista em impressão 3D para home office, escritório e setup gamer.",
     "organizador de mesa, home office, setup gamer, escritório minimalista, suporte celular"),
    ("58210157033", "58210157033.jpg", "Organização de Mesa e Escritório",
     ["Suporte de celular<br>minimalista", "Celular na altura certa,<br>mesa organizada"],
     "Suporte de celular com design moderno e ergonômico, em várias cores. Ideal para chamadas de vídeo, receitas e home office. Impressão 3D.",
     "suporte de celular, home office, mesa minimalista, acessórios escritório"),
    ("22494968293", "22494968293.jpg", "Banheiro e Penteadeira",
     ["Saboneteira que<br>deixa o sabonete seco", "Detalhe minimalista<br>para o banheiro"],
     "Saboneteira com drenagem que mantém o sabonete seco por mais tempo. Design canelado e minimalista, em impressão 3D, para banheiro e lavabo.",
     "saboneteira, decoração banheiro, lavabo, banheiro minimalista"),
    ("58210927197", "58210927197.jpg", "Organização de Mesa e Escritório",
     ["Suporte para headphone<br>de mesa", "Seu fone sempre<br>no lugar certo"],
     "Suporte para headphone e fone de ouvido em impressão 3D. Organiza a mesa gamer ou do escritório e protege o fone.",
     "suporte headphone, setup gamer, organização de mesa, escritório"),
    ("58211055597", "58211055597.jpg", "Banheiro e Penteadeira",
     ["Porta-maquiagem<br>giratório 360°", "Pincéis e batons<br>sempre à mão"],
     "Organizador de maquiagem giratório 360° para pincéis, batons e cosméticos. Multiuso, em impressão 3D, deixa a penteadeira organizada e bonita.",
     "organizador maquiagem, porta pincel, penteadeira, organização"),
    ("58260916127", "58260916127.jpg", "Presentes Criativos",
     ["Porta-joias<br>Gato Preto", "Para quem ama gatos<br>(e anéis)"],
     "Porta-joias em formato de gato preto com bandeja grande para anéis, colares e bijuterias. Decorativo, em impressão 3D. Presente perfeito para quem ama gatos.",
     "porta joias, gato preto, presente para quem ama gatos, decoração criativa"),
    ("58260902322", "58260902322.jpg", "Banheiro e Penteadeira",
     ["Porta-algodão<br>e cotonete", "Banheiro organizado<br>e elegante"],
     "Porta-algodão e cotonete canelado em impressão 3D. Multiuso: também serve para pincéis e escovas. Organiza o banheiro com elegância.",
     "porta algodão, porta cotonete, organização banheiro, decoração banheiro"),
]

CSS = """
@font-face{font-family:Sora;font-weight:600;src:url(ASSETS/fonts/sora-latin-600-normal.woff2)}
@font-face{font-family:DM;font-weight:500;src:url(ASSETS/fonts/dm-sans-latin-500-normal.woff2)}
@font-face{font-family:Mono;font-weight:500;src:url(ASSETS/fonts/jetbrains-mono-latin-500-normal.woff2)}
*{box-sizing:border-box;margin:0;padding:0}
html,body{width:1000px;height:1500px;background:#F7F3EA;color:#1F1F1C;overflow:hidden}
.k{position:absolute;left:70px;top:70px;font:500 22px Mono;letter-spacing:.16em;text-transform:uppercase;color:#C96A3A}
h1{position:absolute;left:70px;right:70px;top:112px;font:600 64px/1.08 Sora;letter-spacing:-.02em}
.foto{position:absolute;left:70px;right:70px;top:300px;height:960px;border-radius:36px;overflow:hidden;background:#fff;box-shadow:0 18px 40px rgba(31,31,28,.10)}
.foto img{width:100%;height:100%;object-fit:cover}
.pe{position:absolute;left:70px;right:70px;bottom:64px;display:flex;align-items:center;justify-content:space-between}
.cta{font:500 30px DM;color:#fff;background:#C96A3A;border-radius:999px;padding:20px 36px}
.sub{position:absolute;left:70px;bottom:150px;font:500 28px DM;color:#6E675D}
.logo{height:46px}
"""


def html(titulo, foto):
    return (f'<!doctype html><html><head><meta charset="utf-8"><style>{CSS.replace("ASSETS", ASSETS.as_uri())}</style></head><body>'
            f'<div class="k">USE LED · impressão 3D</div><h1>{titulo}</h1>'
            f'<div class="foto"><img src="{foto.as_uri()}"></div>'
            f'<div class="sub">Feito sob encomenda · várias cores</div>'
            f'<div class="pe"><div class="cta">Compre na Shopee</div><img class="logo" src="{(ASSETS / "logo-horizontal.png").as_uri()}"></div>'
            f'</body></html>')


def main(inicio: date):
    OUT.mkdir(exist_ok=True)
    pins = []
    # 1ª rodada: título A de todos; 2ª rodada: título B. O Polaroid entra só na 2ª metade (reposição de ímãs).
    for rodada in (0, 1):
        for pid, capa, board, titulos, desc, kw in PRODUTOS:
            pins.append((pid, capa, board, titulos[rodada], desc, kw, rodada))
    polaroid = [p for p in pins if p[0] == "58263428271"]
    outros = [p for p in pins if p[0] != "58263428271"]
    ordem = outros[:10] + polaroid[:1] + outros[10:] + polaroid[1:]

    linhas = []
    with sync_playwright() as pw:
        b = pw.chromium.launch()
        pg = b.new_page(viewport={"width": 1000, "height": 1500})
        for i, (pid, capa, board, titulo, desc, kw, rodada) in enumerate(ordem):
            arq = f"{inicio:%Y-%m}_{pid}_{'ab'[rodada]}.jpg"
            tmp = R / "_pin.html"
            tmp.write_text(html(titulo, R / "capas" / capa), encoding="utf-8")
            pg.goto(tmp.as_uri()); pg.wait_for_timeout(300)
            pg.screenshot(path=str(OUT / arq), type="jpeg", quality=88)
            dia = inicio + timedelta(days=i)
            linhas.append({
                "Title": titulo.replace("<br>", " ")[:100],
                "Media URL": URL_IMG.format(arq=arq),
                "Pinterest board": board,
                "Thumbnail": "",
                "Description": desc[:500],
                "Link": f"https://shopee.com.br/product/{SHOP}/{pid}{UTM}",
                "Publish date": f"{dia:%Y-%m-%d}T15:00:00",  # 12h de Brasília
                "Keywords": kw,
            })
        b.close()
    (R / "_pin.html").unlink(missing_ok=True)
    csv_path = OUT / f"pins_{inicio:%Y-%m}.csv"
    with open(csv_path, "w", newline="", encoding="utf-8") as f:
        w = csv.DictWriter(f, fieldnames=list(linhas[0].keys()))
        w.writeheader(); w.writerows(linhas)
    print(csv_path, len(linhas), "pins de", linhas[0]["Publish date"], "a", linhas[-1]["Publish date"])


if __name__ == "__main__":
    main(date.fromisoformat(sys.argv[1]) if len(sys.argv) > 1 else date.today() + timedelta(days=1))
