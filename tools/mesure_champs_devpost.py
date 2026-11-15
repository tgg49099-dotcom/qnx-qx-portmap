#!/usr/bin/env python3
"""Measures, on PUBLIC Devpost project pages, the lengths of the fields
the Devpost submission form contains (tagline, description, "Built with"
list, "try it out" URL).

Method: a LOWER bound. What is observed is what the platform accepted and
published for real submissions. The rule of the form itself is not read (the
form is behind a session: HTTP 302 measured on 15/11/2026).

Output: JSON + a summary on stdout.
"""
import concurrent.futures as cf
import html
import json
import re
import sys
import subprocess

UA = ("Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36 (KHTML, like Gecko) "
      "Chrome/120.0.0.0 Safari/537.36")


def fetch(url):
    """curl with a browser UA (Cloudflare answers 403 to bare urllib)."""
    p = subprocess.run(
        ["curl", "-s", "-L", "--max-time", "40", "-A", UA,
         "-w", "\n%{http_code}",
         url],
        capture_output=True, text=True, errors="replace")
    body = p.stdout
    if "\n" not in body:
        return None, "ERR:empty"
    page, _, code = body.rpartition("\n")
    code = code.strip()
    if code != "200":
        return None, "HTTP %s" % code
    return 200, page


def strip_tags(s):
    s = re.sub(r"(?is)<(script|style|noscript)\b.*?</\1>", " ", s)
    s = re.sub(r"(?is)<br\s*/?>", "\n", s)
    s = re.sub(r"(?is)</(p|div|li|h[1-6]|tr)>", "\n", s)
    s = re.sub(r"(?is)<[^>]+>", " ", s)
    s = html.unescape(s)
    s = re.sub(r"[ \t\xa0]+", " ", s)
    return s.strip()


def measure(slug):
    url = "https://devpost.com/software/" + slug
    status, page = fetch(url)
    if status != 200:
        return {"slug": slug, "status": status, "error": page[:120]}
    out = {"slug": slug, "status": 200, "url": url}
    # tagline: <h1> / title element of the project
    m = re.search(r'(?is)<h1[^>]*>(.*?)</h1>', page)
    if m:
        out["titre"] = strip_tags(m.group(1))
        out["longueur_titre"] = len(out["titre"])
    # description: content of app-details-left, between the end of the gallery
    # and the "built-with" block / the right column.
    i = page.find('id="app-details-left"')
    if i != -1:
        body = page[i:]
        for stop in ('id="built-with"', 'id="app-details-right"', "<aside"):
            k = body.find(stop)
            if k != -1:
                body = body[:k]
        body = re.sub(r"(?is)<ul[^>]*data-slick.*?</ul>", " ", body)
        desc = strip_tags(body)
        out["longueur_description"] = len(desc)
        out["extrait_description"] = desc[:200]
        out["fin_description"] = desc[-120:]
    # built with: list of tags
    tags = sorted(set(re.findall(r'devpost\.com/software/built-with/([a-z0-9%._+-]+)', page)))
    if tags:
        out["nb_built_with"] = len(tags)
        out["built_with"] = tags[:60]
    # try it out / download links
    m = re.search(r'(?is)try it out.{0,4000}?href="(http[^"]+)"', page)
    if m:
        out["url_try_it_out"] = m.group(1)
        out["longueur_url_try_it_out"] = len(m.group(1))
    return out


def main():
    slugs = [l.strip() for l in open(sys.argv[1], encoding="utf-8") if l.strip()]
    limit = int(sys.argv[2]) if len(sys.argv) > 2 else len(slugs)
    slugs = slugs[:limit]
    rows = []
    with cf.ThreadPoolExecutor(max_workers=8) as ex:
        for r in ex.map(measure, slugs):
            rows.append(r)
    ok = [r for r in rows if r.get("status") == 200]
    out = {"echantillon": len(rows), "mesurees": len(ok), "mesure_le": "2026-11-15",
           "source": "https://devpost.com/software/<slug> (pages de projets publiees)",
           "rows": rows}
    with open("mesure_champs_devpost.json", "w", encoding="utf-8") as f:
        json.dump(out, f, ensure_ascii=False, indent=1)

    def stat(key):
        vals = [r[key] for r in ok if key in r]
        if not vals:
            return "n/a"
        vals.sort()
        return "n=%d min=%d max=%d median=%d p90=%d" % (
            len(vals), vals[0], vals[-1], vals[len(vals) // 2], vals[int(len(vals) * 0.9)])

    print("echantillon mesure :", len(ok), "/", len(rows))
    print("longueur titre      :", stat("longueur_titre"))
    print("longueur description:", stat("longueur_description"))
    print("nb built with       :", stat("nb_built_with"))
    print("longueur url try_out:", stat("longueur_url_try_it_out"))
    top = sorted([r for r in ok if "longueur_description" in r],
                 key=lambda r: -r["longueur_description"])[:8]
    for r in top:
        print("  desc %6d  %-40s | fin: %s" % (r["longueur_description"], r["slug"],
                                              r.get("fin_description", "")[-70:].replace("\n", " ")))
    hist = {}
    for r in ok:
        d = r.get("longueur_description")
        if d:
            hist[d // 100 * 100] = hist.get(d // 100 * 100, 0) + 1
    print("histogramme (paliers de 100) :",
          " ".join("%d:%d" % (k, v) for k, v in sorted(hist.items())))


if __name__ == "__main__":
    main()
