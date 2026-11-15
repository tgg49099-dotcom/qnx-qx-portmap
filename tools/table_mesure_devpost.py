#!/usr/bin/env python3
"""Transforme la mesure brute des pages Devpost en une table de preuves ASCII.

Le script de mesure (`tools/mesure_champs_devpost.py`) ecrit un JSON qui
contient des extraits de pages publiques. Ce JSON n'est pas publie tel quel :
ce script en tire la table courte qui justifie les chiffres cites dans
`KIT-SOUMISSION-QNX.md` (longueurs observees sur 120 pages publiees).

Usage :
    python3 tools/table_mesure_devpost.py <mesure_champs_devpost.json> \
        --out docs/preuves/j-mesure-champs-devpost.txt

Code de sortie : 0 si tout va bien, 1 sinon.
"""

import argparse
import json
import sys

DEFAULT_OUT = "docs/preuves/j-mesure-champs-devpost.txt"


def ascii_safe(text):
    """Remplace tout caractere non ASCII par son equivalent lisible."""
    if text is None:
        return ""
    out = []
    for ch in str(text):
        if ord(ch) < 128:
            out.append(ch)
        else:
            out.append("?")
    return "".join(out)


def stat(values):
    vals = sorted(v for v in values if isinstance(v, int))
    if not vals:
        return None
    return {
        "n": len(vals),
        "min": vals[0],
        "max": vals[-1],
        "median": vals[len(vals) // 2],
    }


def main():
    ap = argparse.ArgumentParser(description=__doc__)
    ap.add_argument("json_path", nargs="?", default=None,
                    help="fichier JSON ecrit par tools/mesure_champs_devpost.py")
    ap.add_argument("--out", default=DEFAULT_OUT, help="fichier de preuve a ecrire")
    args = ap.parse_args()

    if not args.json_path:
        print("usage : python3 tools/table_mesure_devpost.py <fichier.json>")
        return 1

    with open(args.json_path, encoding="utf-8") as fh:
        data = json.load(fh)

    rows = [r for r in data.get("rows", []) if r.get("status") == 200]
    if not rows:
        print("aucune page mesuree dans %s" % args.json_path)
        return 1

    fields = [
        ("longueur_titre", "longueur du nom du projet"),
        ("longueur_description", "longueur de la description publiee"),
        ("nb_built_with", "nombre de tags Built with"),
        ("longueur_url_try_it_out", "longueur de l'URL try it out"),
    ]

    lines = []
    lines.append("MESURE DES CHAMPS DEVPOST PUBLIES - QX PORTMAP")
    lines.append("")
    lines.append("But : borner par l'observation ce que la plateforme accepte,")
    lines.append("quand la limite exacte du formulaire QNX n'est pas lisible")
    lines.append("(le formulaire est derriere une session : HTTP 302 / 401).")
    lines.append("")
    lines.append("Source des donnees : %s" % ascii_safe(data.get("source", "")))
    lines.append("Echantillon       : %d pages publiees mesurees" % len(rows))
    lines.append("Mesure le        : %s" % ascii_safe(data.get("mesure_le", "")))
    lines.append("Commande de mesure :")
    lines.append("    python3 tools/mesure_champs_devpost.py <liste_de_slugs>")
    lines.append("Table generee par :")
    lines.append("    python3 tools/table_mesure_devpost.py <mesure.json>")
    lines.append("")
    lines.append("Resume des longueurs observees :")
    lines.append("")
    lines.append("| element | n | min | median | max |")
    lines.append("|---|---|---|---|---|")
    for key, label in fields:
        s = stat([r.get(key) for r in rows])
        if s is None:
            continue
        lines.append("| %s | %d | %d | %d | %d |"
                     % (label, s["n"], s["min"], s["median"], s["max"]))
    lines.append("")
    lines.append("Detail (une ligne par page publiee mesuree) :")
    lines.append("")
    lines.append("| # | slug | nom | description | tags | url try it out |")
    lines.append("|---|---|---|---|---|---|")
    for i, r in enumerate(sorted(rows, key=lambda r: r.get("slug", "")), 1):
        lines.append("| %d | %s | %s | %s | %s | %s |" % (
            i,
            ascii_safe(r.get("slug", "")),
            r.get("longueur_titre", ""),
            r.get("longueur_description", ""),
            r.get("nb_built_with", ""),
            r.get("longueur_url_try_it_out", ""),
        ))
    lines.append("")

    text = "\n".join(lines)
    if any(ord(ch) >= 128 for ch in text):
        print("ERREUR : le fichier produit contient des caracteres non ASCII.")
        return 1

    with open(args.out, "w", encoding="ascii") as fh:
        fh.write(text)
    print("table de preuves ecrite : %s (%d lignes, %d pages)"
          % (args.out, len(lines), len(rows)))
    return 0


if __name__ == "__main__":
    sys.exit(main())
