"""Rendering of the QX PORTMAP results: text, JSON, Markdown.
"""

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

# Labels of the text and Markdown renderings in the two output languages.
# The French strings reproduce exactly the historical output of the tool,
# byte for byte; the console default is English.
TEXT_STRINGS = {
    "fr": {
        "status": STATUS_LABEL,
        "title": "QX PORTMAP - etat des symboles QNX dans la documentation %s",
        "corpus": "corpus fige : %s",
        "pages": "pages : %d (7.1 : %d, 8.0 : %d) - consulte le %s - mode hors ligne",
        "corpus_quick": "petit corpus du mode rapide : %s",
        "pages_quick": "pages : %d (7.1 : %d, 8.0 : %d) - telecharge le %s - mode rapide "
                       "(index A-Z et guide de migration seulement ; jamais \"absent\")",
        "empty": "(aucun symbole a analyser)",
        "page": "    page   : %s",
        "see": "    voir   : %s",
        "citation": "    citation (%s) :",
        "detail": "    detail :",
        "migration": "    * cite par le guide de migration officiel %s : %s",
        "note": "    note   : %s",
        "worklist": "--- Liste de travail de mise a niveau (%d symbole(s)) ---",
        "nothing": "(rien a migrer : tous les symboles analyses sont documentes en %s)",
        "migration_short": "      cite par le guide de migration : %s",
    },
    "en": {
        "status": {
            DOCUMENTED: "documented",
            ELSEWHERE: "described elsewhere",
            ABSENT: "absent",
            UNKNOWN: "unknown",
        },
        "title": "QX PORTMAP - status of QNX symbols in the %s documentation",
        "corpus": "frozen corpus: %s",
        "pages": "pages: %d (7.1: %d, 8.0: %d) - consulted on %s - offline mode",
        "corpus_quick": "quick-mode small corpus: %s",
        "pages_quick": "pages: %d (7.1: %d, 8.0: %d) - downloaded on %s - quick mode "
                       "(A-Z indexes and migration guide only; never \"absent\")",
        "empty": "(no symbol to analyze)",
        "page": "    page   : %s",
        "see": "    see    : %s",
        "citation": "    citation (%s) :",
        "detail": "    detail :",
        "migration": "    * cited by the official migration guide %s: %s",
        "note": "    note   : %s",
        "worklist": "--- Upgrade worklist (%d symbol(s)) ---",
        "nothing": "(nothing to migrate: every analyzed symbol is documented in %s)",
        "migration_short": "      cited by the migration guide: %s",
    },
}

MD_STRINGS = {
    "fr": {
        "status": STATUS_LABEL,
        "title": "## QX PORTMAP - etat des symboles dans la documentation QNX %s",
        "header": "Corpus fige : %d pages (%s), consulte le %s, lecture hors ligne.",
        "header_quick": "Mode rapide : %d pages (%s), telechargees le %s : index A-Z et "
                        "guide de migration seulement, jamais \"absent\".",
        "by_version": "%s : %d pages",
        "empty": "_Aucun symbole analyse._",
        "table_head": "| Symbole | Statut %s | En 7.1 | Page officielle | Citation exacte |",
        "yes": "oui",
        "no": "non",
        "worklist": "### Liste de travail de mise a niveau",
        "nothing": "_Aucun symbole a migrer._",
        "work_head": "| Priorite | Symbole | Statut | Page |",
    },
    "en": {
        "status": {
            DOCUMENTED: "documented",
            ELSEWHERE: "described elsewhere",
            ABSENT: "absent",
            UNKNOWN: "unknown",
        },
        "title": "## QX PORTMAP - status of symbols in the QNX %s documentation",
        "header": "Frozen corpus: %d pages (%s), consulted on %s, offline reading.",
        "header_quick": "Quick mode: %d pages (%s), downloaded on %s: A-Z indexes and "
                        "migration guide only, never \"absent\".",
        "by_version": "%s: %d pages",
        "empty": "_No symbol analyzed._",
        "table_head": "| Symbol | Status %s | In 7.1 | Official page | Exact citation |",
        "yes": "yes",
        "no": "no",
        "worklist": "### Upgrade worklist",
        "nothing": "_No symbol to migrate._",
        "work_head": "| Priority | Symbol | Status | Page |",
    },
}


def _wrap(text, width, indent):
    if not text:
        return []
    words = text.split()
    lines = []
    current = ""
    for word in words:
        too_long = current and len(current) + 1 + len(word) > width
        # a URL must never be cut in two
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


def render_text(results, worklist, corpus, version="8.0", previous="7.1", width=100,
                lang="fr"):
    """Text rendering, readable in a terminal."""
    L = TEXT_STRINGS[lang if lang in TEXT_STRINGS else "fr"]
    out = []
    out.append(L["title"] % version)
    man = corpus.manifest
    quick = man.get("mode") == "quick"
    out.append(L["corpus_quick" if quick else "corpus"] % corpus.root)
    out.append(L["pages_quick" if quick else "pages"] % (man.get("pages_total", 0),
                             man.get("pages_by_version", {}).get(previous, 0),
                             man.get("pages_by_version", {}).get(version, 0),
                             man.get("consulted", "?")))
    out.append("")
    if not results:
        out.append(L["empty"])
        return "\n".join(out) + "\n"

    for res in results:
        head = "  %-28s %s" % (res.symbol, L["status"][res.status])
        out.append(head)
        if res.url:
            out.append(L["page"] % res.url)
        for extra in res.see_urls[1:]:
            out.append(L["see"] % extra)
        if res.citation:
            source = res.citation_source
            if res.citation_kind:
                source = "%s, %s" % (source, res.citation_kind)
            out.append(L["citation"] % source)
            out.extend(_wrap(res.citation, width - 6, "      "))
        if res.detail:
            out.append(L["detail"])
            out.extend(_wrap(res.detail, width - 6, "      "))
        if res.mentioned_in_migration_guide:
            out.append(L["migration"]
                       % (version, res.migration_urls[0] if res.migration_urls else ""))
        if res.note:
            out.append(L["note"] % res.note)
        out.append("")

    out.append(L["worklist"] % len(worklist))
    if not worklist:
        out.append(L["nothing"] % version)
    else:
        for res in worklist:
            tag = "P%d" % res.priority
            out.append("%s  %-26s %s" % (tag, res.symbol, L["status"][res.status]))
            if res.url:
                out.append("      %s" % res.url)
            if res.citation:
                out.extend(_wrap(res.citation, width - 8, "      "))
            if res.mentioned_in_migration_guide:
                out.append(L["migration_short"]
                           % (res.migration_urls[0] if res.migration_urls else ""))
    out.append("")
    return "\n".join(out) + "\n"


def render_json(results, worklist, corpus, version="8.0", previous="7.1"):
    """JSON rendering (one single object, machine readable)."""
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
            "offline": man.get("mode") != "quick",
            "mode": man.get("mode", "full"),
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


def render_markdown(results, worklist, corpus, version="8.0", previous="7.1",
                    lang="fr"):
    """Markdown rendering, ready to paste in a report."""
    L = MD_STRINGS[lang if lang in MD_STRINGS else "fr"]
    man = corpus.manifest
    out = []
    out.append(L["title"] % version)
    out.append("")
    out.append(L["header_quick" if man.get("mode") == "quick" else "header"]
               % (man.get("pages_total", 0),
                  ", ".join(L["by_version"] % (v, n)
                            for v, n in sorted(man.get("pages_by_version", {}).items())),
                  man.get("consulted", "?")))
    out.append("")
    if not results:
        out.append(L["empty"])
        return "\n".join(out) + "\n"
    out.append(L["table_head"] % version)
    out.append("|---|---|---|---|---|")
    for res in results:
        out.append("| `%s` | %s | %s | %s | %s |"
                   % (res.symbol,
                      L["status"][res.status],
                      L["yes"] if res.in_71 else L["no"],
                      res.url or "-",
                      (res.citation.replace("|", "\\|")[:300] if res.citation else "-")))
    out.append("")
    out.append(L["worklist"])
    out.append("")
    if not worklist:
        out.append(L["nothing"])
    else:
        out.append(L["work_head"])
        out.append("|---|---|---|---|")
        for res in worklist:
            out.append("| P%d | `%s` | %s | %s |"
                       % (res.priority, res.symbol, L["status"][res.status], res.url or "-"))
    out.append("")
    return "\n".join(out) + "\n"
