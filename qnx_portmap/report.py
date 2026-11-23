"""Rendering of the QX PORTMAP results: text, JSON, Markdown, SARIF.
"""

import json

from . import __version__
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
                       "(index A-Z et guide de migration seulement ; \"absent\" seulement si le guide annonce le retrait)",
        "empty": "(aucun symbole a analyser)",
        "page": "    page   : %s",
        "see": "    voir   : %s",
        "citation": "    citation (%s) :",
        "detail": "    detail :",
        "migration": "    * cite par le guide de migration officiel %s : %s",
        "note": "    note   : %s",
        "locations": "    appele : %s",
        "locations_short": "      appele dans : %s",
        "suggestions": "    symbole proche : %s",
        "worklist": "--- Liste de travail de mise a niveau (%d symbole(s)) ---",
        "nothing": "(rien a migrer : tous les symboles analyses sont documentes en %s)",
        "nothing_decided": "(rien a migrer parmi les symboles tranches)",
        "unknown_tail": "(+ %d symbole(s) inconnu(s), hors de cette liste : %s - verifier "
                        "l'orthographe, ou un symbole ajoute apres la date du corpus)",
        "unknown_tail_quick": "(+ %d symbole(s) inconnu(s), non tranche(s) par le mode rapide : "
                              "%s - le corpus complet les tranche)",
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
                       "(A-Z indexes and migration guide only; \"absent\" only when the guide announces the removal)",
        "empty": "(no symbol to analyze)",
        "page": "    page   : %s",
        "see": "    see    : %s",
        "citation": "    citation (%s) :",
        "detail": "    detail :",
        "migration": "    * cited by the official migration guide %s: %s",
        "note": "    note   : %s",
        "locations": "    called : %s",
        "locations_short": "      called at: %s",
        "suggestions": "    similar symbol: %s",
        "worklist": "--- Upgrade worklist (%d symbol(s)) ---",
        "nothing": "(nothing to migrate: every analyzed symbol is documented in %s)",
        "nothing_decided": "(nothing to migrate among the decided symbols)",
        "unknown_tail": "(+ %d unknown symbol(s), not in this list: %s - check the spelling, "
                        "or a symbol added after the corpus date)",
        "unknown_tail_quick": "(+ %d unknown symbol(s), not decided by the quick mode: %s - "
                              "the full corpus decides them)",
        "migration_short": "      cited by the migration guide: %s",
    },
}

MD_STRINGS = {
    "fr": {
        "status": STATUS_LABEL,
        "title": "## QX PORTMAP - etat des symboles dans la documentation QNX %s",
        "header": "Corpus fige : %d pages (%s), consulte le %s, lecture hors ligne.",
        "header_quick": "Mode rapide : %d pages (%s), telechargees le %s : index A-Z et "
                        "guide de migration seulement ; \"absent\" seulement si le guide annonce le retrait.",
        "by_version": "%s : %d pages",
        "empty": "_Aucun symbole analyse._",
        "table_head": "| Symbole | Statut %s | En 7.1 | Page officielle | Citation exacte |",
        "table_head_loc": "| Symbole | Statut %s | En 7.1 | Page officielle | Citation exacte | Fichier:ligne |",
        "yes": "oui",
        "no": "non",
        "worklist": "### Liste de travail de mise a niveau",
        "nothing": "_Aucun symbole a migrer._",
        "nothing_decided": "_Aucun symbole a migrer parmi les symboles tranches._",
        "unknown_tail": "_Hors de cette liste, symboles inconnus : %s._",
        "work_head": "| Priorite | Symbole | Statut | Page |",
        "work_head_loc": "| Priorite | Symbole | Statut | Page | Fichier:ligne |",
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
                        "migration guide only; \"absent\" only when the guide announces the removal.",
        "by_version": "%s: %d pages",
        "empty": "_No symbol analyzed._",
        "table_head": "| Symbol | Status %s | In 7.1 | Official page | Exact citation |",
        "table_head_loc": "| Symbol | Status %s | In 7.1 | Official page | Exact citation | File:line |",
        "yes": "yes",
        "no": "no",
        "worklist": "### Upgrade worklist",
        "nothing": "_No symbol to migrate._",
        "nothing_decided": "_No symbol to migrate among the decided ones._",
        "unknown_tail": "_Unknown, not in this list: %s._",
        "work_head": "| Priority | Symbol | Status | Page |",
        "work_head_loc": "| Priority | Symbol | Status | Page | File:line |",
    },
}


def _format_locations(locations):
    return ", ".join("%s:%d" % (loc["file"], loc["line"]) for loc in locations)


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
                lang="fr", worklist_only=False):
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

    if not worklist_only:
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
            if getattr(res, "suggestions", None):
                out.append(L["suggestions"] % ", ".join(res.suggestions))
            if getattr(res, "locations", None):
                out.append(L["locations"] % _format_locations(res.locations))
            out.append("")

    out.append(L["worklist"] % len(worklist))
    unknown = [r.symbol for r in results if r.status == UNKNOWN]
    if not worklist and not unknown:
        out.append(L["nothing"] % version)
    elif not worklist:
        out.append(L["nothing_decided"])
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
            if getattr(res, "locations", None):
                out.append(L["locations_short"] % _format_locations(res.locations))
    if unknown:
        # an unknown symbol is never silently left out of the worklist
        out.append(L["unknown_tail_quick" if quick else "unknown_tail"]
                   % (len(unknown), ", ".join(unknown)))
    out.append("")
    return "\n".join(out) + "\n"


def render_json(results, worklist, corpus, version="8.0", previous="7.1",
                worklist_only=False, scan=None):
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
    }
    if scan is not None:
        payload["scan"] = scan.to_dict()
    if worklist_only:
        payload["worklist_only"] = True
        payload["worklist"] = [r.to_dict() for r in worklist]
        payload["unknown"] = [r.to_dict() for r in results if r.status == UNKNOWN]
    else:
        payload["symbols"] = [r.to_dict() for r in results]
        payload["worklist"] = [r.to_dict() for r in worklist]
    payload["counts"] = {
        "symbols": len(results),
        "documented": len([r for r in results if r.status == DOCUMENTED]),
        "described_elsewhere": len([r for r in results if r.status == ELSEWHERE]),
        "absent": len([r for r in results if r.status == ABSENT]),
        "unknown": len([r for r in results if r.status == UNKNOWN]),
    }
    return json.dumps(payload, ensure_ascii=False, indent=1) + "\n"


def render_markdown(results, worklist, corpus, version="8.0", previous="7.1",
                    lang="fr", worklist_only=False):
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

    has_locs = any(getattr(r, "locations", None) for r in results)

    if not worklist_only:
        if has_locs:
            out.append(L["table_head_loc"] % version)
            out.append("|---|---|---|---|---|---|")
        else:
            out.append(L["table_head"] % version)
            out.append("|---|---|---|---|---|")
        for res in results:
            cite = (res.citation.replace("\n", " ").replace("|", "\\|")[:300]
                    if res.citation else "-")
            if has_locs:
                locs = (_format_locations(res.locations).replace("|", "\\|")
                        if getattr(res, "locations", None) else "-")
                out.append("| `%s` | %s | %s | %s | %s | %s |"
                           % (res.symbol,
                              L["status"][res.status],
                              L["yes"] if res.in_71 else L["no"],
                              res.url or "-",
                              cite,
                              locs))
            else:
                out.append("| `%s` | %s | %s | %s | %s |"
                           % (res.symbol,
                              L["status"][res.status],
                              L["yes"] if res.in_71 else L["no"],
                              res.url or "-",
                              cite))
        out.append("")

    out.append(L["worklist"])
    out.append("")
    unknown = [r.symbol for r in results if r.status == UNKNOWN]
    if not worklist:
        out.append(L["nothing_decided"] if unknown else L["nothing"])
    else:
        if has_locs:
            out.append(L["work_head_loc"])
            out.append("|---|---|---|---|---|")
            for res in worklist:
                locs = (_format_locations(res.locations).replace("|", "\\|")
                        if getattr(res, "locations", None) else "-")
                out.append("| P%d | `%s` | %s | %s | %s |"
                           % (res.priority, res.symbol, L["status"][res.status],
                              res.url or "-", locs))
        else:
            out.append(L["work_head"])
            out.append("|---|---|---|---|")
            for res in worklist:
                out.append("| P%d | `%s` | %s | %s |"
                           % (res.priority, res.symbol, L["status"][res.status],
                              res.url or "-"))
    if unknown:
        out.append("")
        out.append(L["unknown_tail"] % ", ".join("`%s`" % u for u in unknown))
    out.append("")
    return "\n".join(out) + "\n"


def render_sarif(results, worklist, corpus, version="8.0", previous="7.1",
                 worklist_only=False):
    """SARIF 2.1.0 rendering for CI/CD, GitHub Code Scanning, and IDE diagnostics."""
    rules = [
        {
            "id": "QXPM-P1",
            "name": "QnxSymbolRemovedInMigrationGuide",
            "shortDescription": {
                "text": "Symbol removed in QNX %s according to the official migration guide" % version,
            },
            "defaultConfiguration": {"level": "error"},
        },
        {
            "id": "QXPM-P2",
            "name": "QnxSymbolAbsentFromTargetDocs",
            "shortDescription": {
                "text": "Symbol present in QNX %s but absent from the %s documentation corpus"
                        % (previous, version),
            },
            "defaultConfiguration": {"level": "error"},
        },
        {
            "id": "QXPM-P3",
            "name": "QnxSymbolDescribedElsewhere",
            "shortDescription": {
                "text": "Symbol described elsewhere in QNX %s (no dedicated C Library Reference page)"
                        % version,
            },
            "defaultConfiguration": {"level": "warning"},
        },
        {
            "id": "QXPM-UNK",
            "name": "QnxSymbolUnknownToCorpus",
            "shortDescription": {
                "text": "Symbol not found in the frozen QNX %s documentation corpus" % version,
            },
            "defaultConfiguration": {"level": "note"},
        },
    ]

    findings = list(worklist)
    if not worklist_only:
        findings.extend(r for r in results if r.status == UNKNOWN)

    sarif_results = []
    for res in findings:
        if res.status == ABSENT and res.priority == 1:
            rule_id, level = "QXPM-P1", "error"
        elif res.status == ABSENT:
            rule_id, level = "QXPM-P2", "error"
        elif res.status == ELSEWHERE:
            rule_id, level = "QXPM-P3", "warning"
        else:
            rule_id, level = "QXPM-UNK", "note"

        msg_parts = ["%s (%s)" % (res.symbol, STATUS_LABEL_EN.get(res.status, res.status))]
        if res.note:
            msg_parts.append(res.note)
        if res.citation:
            msg_parts.append("Citation: %s" % res.citation)
        if res.url:
            msg_parts.append("Doc: %s" % res.url)
        message_text = " - ".join(msg_parts)

        props = {
            "symbol": res.symbol,
            "status": res.status,
            "priority": res.priority,
            "url": res.url,
            "in_71": res.in_71,
            "in_80": res.in_80,
            "removed_by_migration_guide": res.removed_by_migration_guide,
        }
        if getattr(res, "suggestions", None):
            props["suggestions"] = list(res.suggestions)

        locs = getattr(res, "locations", None) or []
        if locs:
            for loc in locs:
                sarif_results.append({
                    "ruleId": rule_id,
                    "level": level,
                    "message": {"text": message_text},
                    "locations": [{
                        "physicalLocation": {
                            "artifactLocation": {"uri": loc["file"]},
                            "region": {"startLine": loc["line"]},
                        }
                    }],
                    "properties": props,
                })
        else:
            sarif_results.append({
                "ruleId": rule_id,
                "level": level,
                "message": {"text": message_text},
                "locations": [{
                    "logicalLocations": [{"name": res.symbol, "kind": "function"}]
                }],
                "properties": props,
            })

    sarif = {
        "$schema": "https://json.schemastore.org/sarif-2.1.0.json",
        "version": "2.1.0",
        "runs": [{
            "tool": {
                "driver": {
                    "name": "QX PORTMAP",
                    "version": __version__,
                    "informationUri": "https://github.com/tgg49099-dotcom/qnx-qx-portmap",
                    "rules": rules,
                }
            },
            "results": sarif_results,
        }],
    }
    return json.dumps(sarif, ensure_ascii=False, indent=1) + "\n"
