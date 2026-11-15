#!/usr/bin/env python3
"""Measure the blocks of the Devpost submission kit and fill in the lengths.

The kit (``KIT-SOUMISSION-QNX.md``) is the text to paste into the Devpost
submission form of the QNX Global Hackathon. Each block is delimited by an
HTML comment ``<!-- BLOC:id -->`` followed by a fenced code block, and each
block has a line::

    - Length (measured): __LEN_id__ characters

This script measures the length of every block (the text between the fences,
as pasted, without the final newline) and writes that number in place of the
placeholder. With ``--check`` it rewrites nothing and fails if a length in the
file is wrong, so a judge can check the kit with one command.

Usage::

    python3 tools/mesure_kit.py            # fill in the lengths
    python3 tools/mesure_kit.py --check    # verify the lengths, exit 1 if wrong

Exit code: 0 if everything is consistent, 1 otherwise.
"""

import argparse
import os
import re
import sys

KIT = "KIT-SOUMISSION-QNX.md"
MARKER = re.compile(r"<!--\s*BLOC:([A-Za-z0-9_]+)\s*-->")
FENCE = re.compile(r"^\s*```(.*)$")
PLACEHOLDER = re.compile(r"__LEN_([A-Za-z0-9_]+)__")

# Limits published by Devpost, with the source that was read on 15/11/2026.
# "chars" = maximum number of characters, "lines" = maximum number of lines.
# See KIT-SOUMISSION-QNX.md, section 1.1, for the exact quotes.
LIMITS = {
    "2_2": (140, "chars", "Devpost help, article 145: \"Submission tagline (140 characters)*\""),
    "3_2": (25, "lines", "Devpost help, article 126: \"Built with tags* ... (25 maximum)\""),
}


def parse_blocks(lines):
    """Return [(id, start_line, end_line, content)] for every marked block.

    ``start_line`` is the line of the ``` that opens the block, ``end_line``
    the line of the ``` that closes it. Nested fences (a ```bash inside a
    ```markdown block) are handled with a stack.
    """
    blocks = []
    i = 0
    while i < len(lines):
        m = MARKER.search(lines[i])
        if not m:
            i += 1
            continue
        block_id = m.group(1)
        # find the first fence after the marker
        j = i + 1
        while j < len(lines) and not FENCE.match(lines[j]):
            j += 1
        if j >= len(lines):
            raise SystemExit("no fenced block after the marker %s" % block_id)
        start = j
        # walk the fences with a stack: depth 1 = the block itself
        depth = 1
        k = j + 1
        while k < len(lines) and depth > 0:
            fm = FENCE.match(lines[k])
            if fm:
                if fm.group(1).strip():
                    depth += 1
                else:
                    depth -= 1
                if depth == 0:
                    break
            k += 1
        if depth != 0:
            raise SystemExit("unclosed fenced block after the marker %s" % block_id)
        content = "\n".join(lines[start + 1:k])
        blocks.append((block_id, start, k, content))
        i = k + 1
    return blocks


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--check", action="store_true",
                    help="do not write, fail if a length is wrong")
    ap.add_argument("--kit", default=KIT, help="path of the kit (default: %s)" % KIT)
    args = ap.parse_args()

    if not os.path.exists(args.kit):
        raise SystemExit("kit not found: %s (run from the repository root)" % args.kit)
    with open(args.kit, encoding="utf-8") as fh:
        text = fh.read()
    lines = text.split("\n")
    blocks = parse_blocks(lines)
    if not blocks:
        raise SystemExit("no block found in %s" % args.kit)

    lengths = {bid: len(content) for bid, _s, _e, content in blocks}
    contents = {bid: content for bid, _s, _e, content in blocks}
    used = set(PLACEHOLDER.findall(text))

    out_lines = list(lines)
    # rewrite the length line of every block (idempotent: the line is found
    # by its text, not by a placeholder that only exists in the first draft)
    length_line = {}
    for bid, _s, end, _c in blocks:
        for idx in range(end + 1, min(end + 12, len(out_lines))):
            if "Length (measured)" in out_lines[idx]:
                length_line[bid] = idx
                break
        else:
            raise SystemExit("no 'Length (measured)' line after the block %s" % bid)
        line = out_lines[length_line[bid]]
        m = re.search(r"Length \(measured\):\s*(\d+|__LEN_[A-Za-z0-9_]+__)\s*characters",
                      line)
        if not m:
            raise SystemExit("unreadable length line for the block %s: %s" % (bid, line))
        out_lines[length_line[bid]] = line[:m.start(1)] + str(lengths[bid]) + line[m.end(1):]

    new_text = "\n".join(out_lines)
    if args.check:
        bad = []
        # compare each measured line with the value of the block it describes
        for bid, _s, _e, _c in blocks:
            idx = length_line[bid]
            m = re.search(r"Length \(measured\):\s*(\d+)\s*characters", lines[idx])
            if not m:
                bad.append("%s: no length line found" % bid)
                continue
            if int(m.group(1)) != lengths[bid]:
                bad.append("%s: file says %s, measured %d"
                           % (bid, m.group(1), lengths[bid]))
        left = PLACEHOLDER.findall(new_text)
        if left:
            bad.append("placeholders left in the file: %s" % ", ".join(sorted(set(left))))
        for bid, (limit, kind, source) in sorted(LIMITS.items()):
            if bid not in lengths:
                bad.append("%s: published limit %d %s (%s) but the block is missing"
                           % (bid, limit, kind, source))
                continue
            value = lengths[bid] if kind == "chars" else len(
                [ln for ln in contents[bid].split("\n") if ln.strip()])
            if value > limit:
                bad.append("%s: %d %s over the published limit of %d (%s)"
                           % (bid, value, kind, limit, source))
        for bid, value in sorted(lengths.items()):
            print("%-6s %6d characters" % (bid, value))
        for bid, (limit, kind, source) in sorted(LIMITS.items()):
            if kind == "chars":
                value = lengths.get(bid, 0)
            else:
                value = len([ln for ln in contents.get(bid, "").split("\n") if ln.strip()])
            print("%-6s %6d %s (published limit: %d)" % (bid, value, kind, limit))
        if bad:
            print("\nKO :")
            for b in bad:
                print("  - %s" % b)
            return 1
        print("\nOK : every measured length of %s matches the text." % args.kit)
        return 0

    with open(args.kit, "w", encoding="utf-8") as fh:
        fh.write(new_text)
    for bid, value in sorted(lengths.items()):
        print("%-6s %6d characters" % (bid, value))
    print("\nwritten: %s (%d blocks)" % (args.kit, len(blocks)))
    return 0


if __name__ == "__main__":
    sys.exit(main())
