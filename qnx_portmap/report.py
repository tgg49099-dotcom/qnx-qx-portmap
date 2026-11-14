"""Rendu des resultats de QX PORTMAP : texte, JSON, Markdown."""

import json

from .classify import ABSENT, DOCUMENTED, ELSEWHERE, UNKNOWN

STATUS_LABEL = {
    DOCUMENTED: "documente",
    ELSEWHERE: "decrit ailleurs",
    ABSENT: "absent de la 8.0",
    UNKNOWN: "inconnu du corpus",
}

STATUS_LABEL_EN = {
    DOCUMENTED: "documented",
    ELSEWHERE: "described_elsewhere",
    ABSENT: "absent",
    UNKNOWN: "unknown",
}


def _wrap(text, width, indent):
    if not text:
        return []
    words = text.split()
    lines = []
    current = ""
    for word in words:
        too_long = current and len(current) + 1 + len(word) > width
        # une URL ne doit jamais etre coupee en deux
        if too_long and ("://" in current or "://" in word):
            lines.append(current)
            current = word
            continue
        if too_long:
            lines.append(current)
            current = word
        else:
            current = (current + " " + word).strip()
    if current:
        lines.append(current)
    return [indent + line for line in lines]


def render_text(results, worklist, corpus, version="8.0", previous="7.1", width=100):
    """Rendu texte, lisible dans un terminal."""
    out = []
    out.append("QX PORTMAP - etat des symboles QNX dans la documentation %s" % version)
    man = corpus.manifest
    out.append("corpus fige : %s" % corpus.root)
    out.append("pages : %d (7.1 : %d, 8.0 : %d) - consulte le %s - mode hors ligne"
               % (man.get("pages_total", 0),
                  man.get("pages_by_version", {}).get(previous, 0),
                  man.get("pages_by_version", {}).get(version, 0),
                  man.get("consulted", "?")))
    out.append("")
    if not results:
        out.append("(aucun symbole a analyser)")
        return "\n".join(out) + "\n"

    for res in results:
        head = "  %-28s %s" % (res.symbol, STATUS_LABEL[res.status])
        out.append(head)
        if res.url:
            out.append("    page   : %s" % res.url)
        for extra in res.see_urls[1:]:
            out.append("    voir   : %s" % extra)
        if res.citation:
            source = res.citation_source
            if res.citation_kind:
                source = "%s, %s" % (source, res.citation_kind)
            out.append("    citation (%s) :" % source)
            out.extend(_wrap(res.citation, width - 6, "      "))
        if res.detail:
            out.append("    detail :")
            out.extend(_wrap(res.detail, width - 6, "      "))
        if res.mentioned_in_migration_guide:
            out.append("    * cite par le guide de migration officiel %s : %s"
                       % (version, res.migration_urls[0] if res.migration_urls else ""))
        if res.note:
            out.append("    note   : %s" % res.note)
        out.append("")

    out.append("--- Liste de travail de mise a niveau (%d symbole(s)) ---" % len(worklist))
    if not worklist:
        out.append("(rien a migrer : tous les symboles analyses sont documentes en %s)" % version)
    else:
        for res in worklist:
            tag = "P%d" % res.priority
            out.append("%s  %-26s %s" % (tag, res.symbol, STATUS_LABEL[res.status]))
            if res.url:
                out.append("      %s" % res.url)
            if res.citation:
                out.extend(_wrap(res.citation, width - 8, "      "))
            if res.mentioned_in_migration_guide:
                out.append("      cite par le guide de migration : %s"
                           % (res.migration_urls[0] if res.migration_urls else ""))
    out.append("")
    return "\n".join(out) + "\n"


def render_json(results, worklist, corpus, version="8.0", previous="7.1"):
    """Rendu JSON (une seule fois, machine lisible)."""
    man = corpus.manifest
    payload = {
        "tool": "QX PORTMAP",
        "version": version,
        "previous_version": previous,
        "corpus": {
            "path": corpus.root,
            "pages_total": man.get("pages_total"),
            "pages_by_version": man.get("pages_by_version"),
            "consulted": man.get("consulted"),
            "offline": True,
        },
        "symbols": [r.to_dict() for r in results],
        "worklist": [r.to_dict() for r in worklist],
        "counts": {
            "symbols": len(results),
            "documented": len([r for r in results if r.status == DOCUMENTED]),
            "described_elsewhere": len([r for r in results if r.status == ELSEWHERE]),
            "absent": len([r for r in results if r.status == ABSENT]),
            "unknown": len([r for r in results if r.status == UNKNOWN]),
        },
    }
    return json.dumps(payload, ensure_ascii=False, indent=1) + "\n"


def render_markdown(results, worklist, corpus, version="8.0", previous="7.1"):
    """Rendu Markdown, prete a coller dans un rapport."""
    man = corpus.manifest
    out = []
    out.append("## QX PORTMAP - etat des symboles dans la documentation QNX %s" % version)
    out.append("")
    out.append("Corpus fige : %d pages (%s), consulte le %s, lecture hors ligne."
               % (man.get("pages_total", 0),
                  ", ".join("%s : %d pages" % (v, n)
                            for v, n in sorted(man.get("pages_by_version", {}).items())),
                  man.get("consulted", "?")))
    out.append("")
    if not results:
        out.append("_Aucun symbole analyse._")
        return "\n".join(out) + "\n"
    out.append("| Symbole | Statut %s | En 7.1 | Page officielle | Citation exacte |" % version)
    out.append("|---|---|---|---|---|")
    for res in results:
        out.append("| `%s` | %s | %s | %s | %s |"
                   % (res.symbol,
                      STATUS_LABEL[res.status],
                      "oui" if res.in_71 else "non",
                      res.url or "-",
                      (res.citation.replace("|", "\\|")[:300] if res.citation else "-")))
    out.append("")
    out.append("### Liste de travail de mise a niveau")
    out.append("")
    if not worklist:
        out.append("_Aucun symbole a migrer._")
    else:
        out.append("| Priorite | Symbole | Statut | Page |")
        out.append("|---|---|---|---|")
        for res in worklist:
            out.append("| P%d | `%s` | %s | %s |"
                       % (res.priority, res.symbol, STATUS_LABEL[res.status], res.url or "-"))
    out.append("")
    return "\n".join(out) + "\n"
