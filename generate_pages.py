#!/usr/bin/env python3
"""
Generator halaman STIKES Medika Seramoe Barat.

Membaca pages.json (daftar path halaman), lalu untuk setiap path membuat
file HTML dari template halaman.html dengan mengganti <!--HEAD--> dan <title>.

Pemakaian:
    python generate_pages.py                 # generate semua halaman
    python generate_pages.py --sync          # perbarui pages.json dari data/content.json, lalu generate
    python generate_pages.py --check         # hanya cek, tidak menulis file (exit 1 bila ada masalah)

Aturan path -> halaman:
    berita/index.html          -> p=berita,  s=""
    prodi/index.html           -> p=prodi,   s=""
    prodi/<slug>/index.html    -> p=prodi,   s=<slug>   (slug = slugify(nama prodi))
    galeri/index.html          -> p=galeri,  s=""
    berita/<slug>/index.html   -> p=artikel, s=<slug>
"""
import argparse
import html
import json
import re
import sys
import unicodedata
from pathlib import Path

SITE = "STIKES Medika Seramoe Barat"

DESC = {
    "berita": "Kabar terbaru dan agenda kampus STIKES Medika Seramoe Barat.",
    "prodi": "Program studi di STIKES Medika Seramoe Barat.",
    "galeri": "Suasana dan kegiatan kampus STIKES Medika Seramoe Barat.",
    "artikel": "Berita STIKES Medika Seramoe Barat.",
}
TITLE = {"berita": "Berita", "prodi": "Program Studi", "galeri": "Galeri", "artikel": "Berita"}


def slugify(t):
    """Harus identik dengan slugify() di JavaScript pada template."""
    t = unicodedata.normalize("NFD", str(t or "").lower())
    t = re.sub(r"[\u0300-\u036f]", "", t)
    t = re.sub(r"[^a-z0-9]+", "-", t)
    t = re.sub(r"^-+|-+$", "", t)[:50]
    return t or "item"


def short(text, n=160):
    text = re.sub(r"\s+", " ", str(text or "")).strip()
    return text if len(text) <= n else text[: n - 1].rstrip() + "…"


def classify(path):
    """Kembalikan (p, s) dari path relatif, atau None bila tidak dikenali."""
    parts = Path(path).as_posix().split("/")
    if parts[-1] != "index.html":
        return None
    dirs = parts[:-1]
    if len(dirs) == 1 and dirs[0] in ("berita", "prodi", "galeri"):
        return dirs[0], ""
    if len(dirs) == 2 and dirs[0] == "prodi":
        return "prodi", dirs[1]
    if len(dirs) == 2 and dirs[0] == "berita":
        return "artikel", dirs[1]
    return None


def build_meta(p, s, content, warnings):
    """Tentukan judul + deskripsi halaman."""
    title, desc = TITLE[p], DESC[p]
    if p == "prodi" and s:
        cur = next((x for x in content.get("programs", []) if slugify(x.get("nama")) == s), None)
        if cur:
            title, desc = cur["nama"], cur.get("deskripsi") or desc
        else:
            warnings.append(f"prodi '{s}' tidak ada di content.json")
    elif p == "artikel":
        cur = next((x for x in content.get("berita", []) if x.get("slug") == s), None)
        if cur:
            title, desc = cur.get("judul") or title, short(cur.get("isi")) or desc
        else:
            warnings.append(f"berita '{s}' tidak ada di content.json")
    return title, desc


def build_head(base, p, s, title, desc):
    full = f"{title} — {SITE}"
    e = lambda v: html.escape(v, quote=True)
    page_js = json.dumps({"p": p, "s": s}).replace("</", "<\\/")
    return "\n".join([
        f'<base href="{base}">',
        f'<meta name="description" content="{e(desc)}">',
        '<meta property="og:type" content="website">',
        f'<meta property="og:title" content="{e(full)}">',
        f'<meta property="og:description" content="{e(desc)}">',
        f"<script>window.PAGE={page_js};</script>",
    ]), full


def pages_from_content(content):
    out = ["berita/index.html", "prodi/index.html"]
    out += [f"prodi/{slugify(x.get('nama'))}/index.html" for x in content.get("programs", [])]
    out.append("galeri/index.html")
    out += [f"berita/{x['slug']}/index.html" for x in content.get("berita", []) if x.get("slug")]
    return out


def main():
    ap = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    ap.add_argument("--root", default=".", help="folder situs (default: folder saat ini)")
    ap.add_argument("--template", default="halaman.html")
    ap.add_argument("--pages", default="pages.json")
    ap.add_argument("--content", default="data/content.json")
    ap.add_argument("--sync", action="store_true", help="tulis ulang pages.json dari content.json")
    ap.add_argument("--check", action="store_true", help="dry-run: tidak menulis file")
    a = ap.parse_args()

    root = Path(a.root)
    tpl_path, pages_path, content_path = root / a.template, root / a.pages, root / a.content

    if not tpl_path.exists():
        sys.exit(f"Template tidak ditemukan: {tpl_path}")
    template = tpl_path.read_text(encoding="utf-8")
    if "<!--HEAD-->" not in template:
        sys.exit("Template tidak memiliki penanda <!--HEAD-->")

    content = {}
    if content_path.exists():
        content = json.loads(content_path.read_text(encoding="utf-8"))
    else:
        print(f"! {content_path} tidak ada; judul/deskripsi memakai bawaan", file=sys.stderr)

    if a.sync:
        if not content:
            sys.exit("--sync membutuhkan data/content.json")
        paths = pages_from_content(content)
        if not a.check:
            pages_path.write_text(json.dumps(paths, indent=2, ensure_ascii=False) + "\n", encoding="utf-8")
        print(f"pages.json diperbarui: {len(paths)} halaman")
    else:
        paths = json.loads(pages_path.read_text(encoding="utf-8"))

    problems = 0
    for path in paths:
        info = classify(path)
        if not info:
            print(f"✗ {path}: path tidak dikenali, dilewati", file=sys.stderr)
            problems += 1
            continue
        p, s = info
        warnings = []
        title, desc = build_meta(p, s, content, warnings)
        depth = len(Path(path).parts) - 1
        head, full_title = build_head("../" * depth, p, s, title, desc)

        out = template.replace("<!--HEAD-->", head)
        out = re.sub(r"<title>.*?</title>", lambda _: f"<title>{html.escape(full_title)}</title>", out, count=1, flags=re.S)

        for w in warnings:
            print(f"! {path}: {w}", file=sys.stderr)
            problems += 1
        if not a.check:
            dest = root / path
            dest.parent.mkdir(parents=True, exist_ok=True)
            dest.write_text(out, encoding="utf-8")
        print(f"✓ {path}")

    print(f"\nSelesai: {len(paths)} halaman, {problems} peringatan.")
    if a.check and problems:
        sys.exit(1)


if __name__ == "__main__":
    main()
