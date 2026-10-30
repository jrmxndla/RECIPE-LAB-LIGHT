#!/usr/bin/env python3
"""
Recipe Lab — construction du fichier autonome index.html

    python3 build.py

Rassemble src/, fonts/ et assets/ en un seul fichier HTML sans aucune
dépendance locale : polices et illustrations y sont encodées en base64.
Seules les bibliothèques d'export (jsPDF, html2canvas, SheetJS) sont
appelées à la demande depuis un CDN, au moment où l'on exporte.
"""

import base64
import pathlib

ROOT = pathlib.Path(__file__).parent
SRC = ROOT / "src"
FONTS = ROOT / "fonts"
ASSETS = ROOT / "assets"
OUT = ROOT / "index.html"
OUT_LIGHT = ROOT / "light.html"

# graisses de Lineal embarquées, dans l'ordre des poids CSS
WEIGHTS = [(400, "Regular"), (500, "Medium"), (700, "Bold"), (900, "Black")]

# illustrations : le nom du fichier devient la clé utilisée dans le code
ART_NAMES = [
    "taste", "pizza", "waiter", "baker", "barista", "pasta", "whisk",
    "cake", "chop", "coffee", "brioche", "steak", "sushi", "carrot", "logo",
]
# clé JS -> nom de fichier, pour les noms qui ne sont pas des identifiants
ART_EXTRA = {"logoLight": "logo-light"}

# M PLUS 1, embarquée uniquement dans la version allégée
MPLUS = FONTS / "mplus1"
MPLUS_WEIGHTS = [100, 200, 300, 400, 500, 600, 700, 800, 900]


def data_uri(path, mime):
    return "data:%s;base64,%s" % (mime, base64.b64encode(path.read_bytes()).decode())


def font_css():
    rules = []
    for weight, style in WEIGHTS:
        uri = data_uri(FONTS / ("Lineal-%s.woff2" % style), "font/woff2")
        rules.append(
            "@font-face{font-family:'Lineal';src:url(%s) format('woff2');"
            "font-weight:%d;font-style:normal;font-display:swap}" % (uri, weight)
        )
    return "\n".join(rules)


def art_js():
    import json
    art = {n: data_uri(ASSETS / ("%s.webp" % n), "image/webp") for n in ART_NAMES}
    for key, fname in ART_EXTRA.items():
        art[key] = data_uri(ASSETS / ("%s.webp" % fname), "image/webp")
    return "const ART=" + json.dumps(art) + ";"


def mplus_css():
    rules = []
    for weight in MPLUS_WEIGHTS:
        path = MPLUS / ("m-plus-1-latin-%d-normal.woff2" % weight)
        rules.append(
            "@font-face{font-family:'M PLUS 1';src:url(%s) format('woff2');"
            "font-weight:%d;font-style:normal;font-display:swap}"
            % (data_uri(path, "font/woff2"), weight)
        )
    return "\n".join(rules)


def main():
    head = (SRC / "01-head.html").read_text(encoding="utf-8")
    if "/*__LINEAL__*/" not in head:
        raise SystemExit("01-head.html : marqueur /*__LINEAL__*/ introuvable")
    head = head.replace("/*__LINEAL__*/", font_css())

    parts = [
        head,
        (SRC / "02-body.html").read_text(encoding="utf-8"),
        "<script>\n",
        art_js(),
        "\n</script>\n",
        (SRC / "03-state.js").read_text(encoding="utf-8"),
        (SRC / "04-i18n.js").read_text(encoding="utf-8"),
        (SRC / "05-sheet.js").read_text(encoding="utf-8"),
        (SRC / "06-editor.js").read_text(encoding="utf-8"),
        (SRC / "07-app.js").read_text(encoding="utf-8"),
    ]
    page = "".join(parts)
    OUT.write_text(page.replace("/*__GEIST__*/", ""), encoding="utf-8")
    print("index.html écrit — %d Ko" % (OUT.stat().st_size // 1024))

    # version allégée : même code, un interrupteur et un titre différents
    light = page.replace("const LIGHT = false; /*__LIGHT__*/",
                         "const LIGHT = true; /*__LIGHT__*/")
    if light == page:
        raise SystemExit("03-state.js : interrupteur /*__LIGHT__*/ introuvable")
    light = light.replace("<title>Recipe Lab — Fiches techniques</title>",
                          "<title>Recipe Lab Light — Fiches techniques</title>")
    light = light.replace("/*__GEIST__*/", mplus_css())
    light = light.replace('<body data-screen="menu">', '<body class="light" data-screen="menu">')
    OUT_LIGHT.write_text(light, encoding="utf-8")
    print("light.html écrit — %d Ko" % (OUT_LIGHT.stat().st_size // 1024))


if __name__ == "__main__":
    main()
