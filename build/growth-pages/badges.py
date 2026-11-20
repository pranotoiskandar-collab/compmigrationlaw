"""Draw the "Data from IMR" partner badges (SVG) in four versions: English/Indonesian x light/dark.
PNG copies are made by render_png.js (Playwright) for sites that cannot use SVG."""
from common import SITE

VERSIONS = {
    "data-from-imr": ("DATA FROM", "light"),
    "data-from-imr-dark": ("DATA FROM", "dark"),
    "data-dari-imr": ("DATA DARI", "light"),
    "data-dari-imr-dark": ("DATA DARI", "dark"),
}


def svg(top, look):
    bg, stroke, sq, sqtext, small, big = (
        ("#FFFFFF", "#1E6B4A", "#1E6B4A", "#FFFFFF", "#1E6B4A", "#172D24") if look == "light"
        else ("#172D24", "#7F9A8C", "#FFFFFF", "#172D24", "#BCCFC5", "#FFFFFF"))
    label = "Data from IMR, Institute for Migrant Rights" if top == "DATA FROM" else "Data dari IMR, Institute for Migrant Rights"
    return f"""<svg xmlns="http://www.w3.org/2000/svg" width="264" height="56" viewBox="0 0 264 56" role="img" aria-label="{label}">
<title>{label}</title>
<rect x="0.75" y="0.75" width="262.5" height="54.5" rx="8" fill="{bg}" stroke="{stroke}" stroke-width="1.5"/>
<rect x="8" y="8" width="40" height="40" rx="4" fill="{sq}"/>
<text x="28" y="33" text-anchor="middle" font-family="Figtree, 'Helvetica Neue', Arial, sans-serif" font-size="15" font-weight="700" font-style="italic" fill="{sqtext}">IMR</text>
<text x="58" y="24" font-family="Figtree, 'Helvetica Neue', Arial, sans-serif" font-size="10.5" font-weight="700" letter-spacing="1.6" fill="{small}">{top}</text>
<text x="58" y="42" font-family="Figtree, 'Helvetica Neue', Arial, sans-serif" font-size="14.5" font-weight="700" fill="{big}">Institute for Migrant Rights</text>
</svg>
"""


def build():
    for name, (top, look) in VERSIONS.items():
        (SITE / "partners" / "badge" / f"{name}.svg").write_text(svg(top, look), encoding="utf-8")
    print("wrote", len(VERSIONS), "badges")


if __name__ == "__main__":
    build()
