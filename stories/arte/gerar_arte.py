"""Gera a arte do story (1080x1920, JPEG) a partir de um template HTML.

Uso:
    python gerar_arte.py exemplos/natal.json saida/natal.jpg
    python gerar_arte.py exemplos/natal.json saida/natal.jpg --zonas   # mostra zonas seguras

O JSON tem os campos do template: imagem, chip, credito, eyebrow, titulo,
titulo_destaque, corpo e (opcional) handle e template.
"""
import argparse
import asyncio
import html
import io
import json
import re
from pathlib import Path

from PIL import Image, ImageDraw
from playwright.async_api import async_playwright

AQUI = Path(__file__).resolve().parent
TEMPLATES = AQUI / "templates"
LARGURA, ALTURA = 1080, 1920
ZONA_TOPO, ZONA_BASE = 200, 180  # áreas cobertas pela interface do Instagram

PADROES = {
    "handle": "@useledluminarias",
    "eyebrow": "Vem descobrir o que dá para imprimir",
    "template": "story_produto.html",
    "posicao": "center center",  # enquadramento da foto no card (CSS object-position)
}


def preencher(template: str, dados: dict) -> str:
    def troca(m):
        chave = m.group(1)
        valor = dados.get(chave, "")
        if chave == "imagem":
            return Path(valor).resolve().as_uri() if valor and "://" not in valor else valor
        return html.escape(str(valor))

    return re.sub(r"\{\{(\w+)\}\}", troca, template)


async def renderizar(html_pronto: str) -> bytes:
    tmp = TEMPLATES / "_render.html"
    tmp.write_text(html_pronto, encoding="utf-8")
    try:
        async with async_playwright() as p:
            navegador = await p.chromium.launch(args=["--allow-file-access-from-files"])
            pagina = await navegador.new_page(viewport={"width": LARGURA, "height": ALTURA})
            await pagina.goto(tmp.as_uri())
            await pagina.evaluate("document.fonts.ready")
            await pagina.wait_for_load_state("networkidle")
            folga = await pagina.evaluate(
                "document.querySelector('.rodape').getBoundingClientRect().top"
                " - document.querySelector('.texto').getBoundingClientRect().bottom"
            )
            if folga < 16:
                raise ValueError(f"Texto longo demais: invade o rodapé ({folga:.0f}px). Encurte titulo/corpo.")
            png = await pagina.screenshot(type="png")
            await navegador.close()
            return png
    finally:
        tmp.unlink(missing_ok=True)


def desenhar_zonas(img: Image.Image) -> Image.Image:
    img = img.convert("RGBA")
    camada = Image.new("RGBA", img.size, (0, 0, 0, 0))
    d = ImageDraw.Draw(camada)
    d.rectangle([0, 0, LARGURA, ZONA_TOPO], fill=(255, 0, 0, 60))
    d.rectangle([0, ALTURA - ZONA_BASE, LARGURA, ALTURA], fill=(255, 0, 0, 60))
    return Image.alpha_composite(img, camada)


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("entrada", help="JSON com os textos e a imagem")
    ap.add_argument("saida", help="arquivo .jpg de saída")
    ap.add_argument("--zonas", action="store_true", help="sobrepõe as zonas seguras")
    a = ap.parse_args()

    entrada = Path(a.entrada).resolve()
    dados = {**PADROES, **json.loads(entrada.read_text(encoding="utf-8"))}
    if dados.get("imagem") and "://" not in dados["imagem"]:
        dados["imagem"] = str((entrada.parent / dados["imagem"]).resolve())

    template = (TEMPLATES / dados["template"]).read_text(encoding="utf-8")
    png = asyncio.run(renderizar(preencher(template, dados)))

    img = Image.open(io.BytesIO(png))
    if a.zonas:
        img = desenhar_zonas(img)
    saida = Path(a.saida)
    saida.parent.mkdir(parents=True, exist_ok=True)
    img.convert("RGB").save(saida, "JPEG", quality=92, optimize=True)  # API do IG aceita só JPEG
    print(f"ok -> {saida}")


if __name__ == "__main__":
    main()
