import html
import pathlib
import re

L = chr(60)
S = chr(47)
raw = pathlib.Path("posna.html").read_text(encoding="utf-8", errors="ignore")
raw = re.sub(L + r"script[\s\S]*?" + L + S + "script>", " ", raw, flags=re.I)
raw = re.sub(L + r"style[\s\S]*?" + L + S + "style>", " ", raw, flags=re.I)

link_re = re.compile(
    L + r"a[^>]+href=[\"']([^\"']+)[\"'][^>]*>(.*?)" + L + S + "a>",
    re.I | re.S,
)
links = link_re.findall(raw)
title_m = re.search(L + r"title[^>]*>(.*?)" + L + S + "title>", raw, re.I | re.S)
desc_m = re.search(
    r'name=["\']description["\'][^>]*content=["\'](.*?)["\']', raw, re.I | re.S
)
if not desc_m:
    desc_m = re.search(
        r'content=["\'](.*?)["\'][^>]*name=["\']description["\']', raw, re.I | re.S
    )

text = html.unescape(re.sub(L + r"[^>]+>", "\n", raw))
lines = []
prev = ""
for line in text.splitlines():
    line = re.sub(r"\s+", " ", line).strip()
    if len(line) > 1 and line != prev:
        lines.append(line)
        prev = line

out = []
out.append(
    "TITLE: "
    + (
        html.unescape(re.sub(r"\s+", " ", title_m.group(1)).strip())
        if title_m
        else ""
    )
)
out.append("DESC: " + (html.unescape(desc_m.group(1).strip()) if desc_m else ""))
out.append("")
out.append("LINKS:")
seen = set()
for href, label in links:
    lab = re.sub(r"\s+", " ", re.sub(L + r"[^>]+>", " ", label))
    lab = html.unescape(lab).strip()
    key = (href, lab)
    if key in seen or not lab:
        continue
    seen.add(key)
    out.append(lab + " | " + href)
out.append("")
out.append("TEXT:")
out.extend(lines)
pathlib.Path("posna-text.txt").write_text("\n".join(out), encoding="utf-8")
print(len(out), "lines", pathlib.Path("posna-text.txt").stat().st_size, "bytes")
