"""Add South Asia and Southeast Asia choices to the country filters on /countries-of-origin/ (Pranoto, 21 Nov 2026).

Usage: python3 build/merge-incoming/south_asia_filter.py SITE
There is no South Asia page: the South Asian states are origin states and live on Countries of Origin. This adds
"South Asia" (BD, IN, LK, NP, PK) and "Southeast Asia" (ID, PH, VN, MM, KH, LA, TL) to the country menus of the
instruments list (section VI) and the laws list (section VII), shows the right label for secondary and UN-hosted
copies in the laws list, and replaces "All eight" (the page now has twelve states). Idempotent.
"""
import sys
from pathlib import Path

p = Path(sys.argv[1]) / "countries-of-origin/oc.js"
s = p.read_text(encoding="utf-8")
if "var REG = " not in s:
    REG = ('  var REG = {"@SA": [["South Asia", "Asia Selatan"], ["BD", "IN", "LK", "NP", "PK"]], '
           '"@SEA": [["Southeast Asia", "Asia Tenggara"], ["ID", "PH", "VN", "MM", "KH", "LA", "TL"]]};\n'
           '  var inSel = function (v, k) { return !v || (REG[v] ? REG[v][1].indexOf(k) >= 0 : v === k); };\n'
           '  var regOpts = function (v) { return Object.keys(REG).map(function (r) { return \'<option value="\' + r + \'"\' + (v === r ? " selected" : "") + ">" + esc(t(REG[r][0][0], REG[r][0][1])) + "</option>"; }).join(""); };\n')
    anchor = "  function atools() {"
    assert anchor in s
    s = s.replace(anchor, REG + anchor, 1)
    # menus: "All" + regions + states
    s = s.replace("""var so = '<option value="">' + t("All eight", "Kedelapannya") + "</option>" + S.map(function (s) { return '<option value="' + s.k + '"' + (AF.s === s.k""",
                  """var so = '<option value="">' + t("All countries", "Semua negara") + "</option>" + regOpts(AF.s) + S.map(function (s) { return '<option value="' + s.k + '"' + (AF.s === s.k""")
    s = s.replace("""var so = '<option value="">' + t("All eight", "Kedelapannya") + "</option>" + S.map(function (s) { return '<option value="' + s.k + '"' + (LF.s === s.k""",
                  """var so = '<option value="">' + t("All countries", "Semua negara") + "</option>" + regOpts(LF.s) + S.map(function (s) { return '<option value="' + s.k + '"' + (LF.s === s.k""")
    # filters
    s = s.replace("return (!AF.s || covers(a, AF.s)) &&",
                  "return (!AF.s || (REG[AF.s] ? REG[AF.s][1].some(function (k) { return covers(a, k); }) : covers(a, AF.s))) &&")
    s = s.replace("return (!LF.s || x.s === LF.s) &&", "return inSel(LF.s, x.s) &&")
    # link labels
    s = s.replace("""(x.link === "text" ? t("Read the text", "Baca teks") : t("Official database", "Basis data resmi"))""",
                  """(x.link === "text" ? t("Read the text", "Baca teks") : x.link === "secondary" ? t("Secondary copy", "Salinan sekunder") : x.link === "un" ? t("UN-hosted copy", "Salinan di situs PBB") : x.link === "guidance" ? t("Official guidance", "Panduan resmi") : t("Official database", "Basis data resmi"))""")
    for must in ("regOpts(AF.s)", "regOpts(LF.s)", "REG[AF.s][1].some", "inSel(LF.s, x.s)", "UN-hosted copy"):
        assert must in s, must
    p.write_text(s, encoding="utf-8")
    print("South Asia and Southeast Asia filters added to", p)
else:
    print("already there")
