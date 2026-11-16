# Video tooling only: needs pyte, Pillow and ffmpeg (NOT needed by qnx_portmap, which uses the standard library only).
"""Render the real terminal recording (script -T) of QX PORTMAP into an MP4.

Every terminal frame is the replay of the recorded bytes (pyte terminal
emulator); only idle waits are shortened (said on screen) and the final
screen of each command is held so it can be read. Captions are burned in.
No audio track.
"""
import subprocess, sys
import pyte
from PIL import Image, ImageDraw, ImageFont

W, H, FPS = 1920, 1080, 25
COLS, ROWS = 140, 38
MONO = ImageFont.truetype("/usr/share/fonts/truetype/dejavu/DejaVuSansMono.ttf", 22)
MONOB = ImageFont.truetype("/usr/share/fonts/truetype/dejavu/DejaVuSansMono-Bold.ttf", 22)
SANS = ImageFont.truetype("/usr/share/fonts/truetype/dejavu/DejaVuSans.ttf", 30)
SANSB = ImageFont.truetype("/usr/share/fonts/truetype/dejavu/DejaVuSans-Bold.ttf", 64)
SANSM = ImageFont.truetype("/usr/share/fonts/truetype/dejavu/DejaVuSans.ttf", 40)
BG, FG, PROMPT = (16, 20, 24), (225, 228, 232), (120, 200, 255)
CAPBG, CAPFG = (32, 38, 46), (255, 255, 255)
LH, CW, X0, Y0 = 25, 13, 50, 18
STATUS = {"documented": (110, 210, 120), "unknown": (240, 190, 80),
          "described elsewhere": (100, 200, 220), "absent": (240, 110, 100)}

CAPTIONS = {
    "cd": "A fresh clone of the public repository. QX PORTMAP: for each QNX symbol your code calls, is it still documented in QNX 8.0? A host tool: Python 3, standard library only. No QNX SDK, no board, no account.",
    "quick": "Quick mode: it downloads only the A-Z indexes of the official QNX 7.1 and 8.0 C Library Reference and the 8.0 migration guide (76 pages, about 1.5 min at 1 request/s; the wait is shortened here).",
    "endquick": "abort: documented in 8.0, quoted from the official page. bzero: in the 7.1 index, not in the 8.0 one, so 'unknown' in quick mode: the tool never guesses 'absent'. A typo is unknown too. Exit code 1.",
    "qnx": "Second run: the small corpus is cached, the answer is immediate.",
    "endqnx": "accept has no page of its own in the 8.0 C Library Reference but is described elsewhere: the tool gives that page, the migration-guide reference, and puts it in the upgrade worklist.",
    "json": "The same answer in JSON, for a continuous-integration pipeline.",
    "endjson": "The same answer in JSON, for a continuous-integration pipeline.",
    "tests": "The test suite: no network, no dependency. 33 tests need the full corpus and are skipped on a fresh clone.",
    "endtests": "The test suite: no network, no dependency. 33 tests need the full corpus and are skipped on a fresh clone.",
}
HOLD = {"endcd": 2.5, "endquick": 17, "endqnx": 15, "endjson": 7, "endtests": 6}
MAXGAP, SHORTGAP = 1.2, 0.5


def wrap(text, font, width, draw):
    words, lines, cur = text.split(), [], ""
    for w in words:
        t = (cur + " " + w).strip()
        if draw.textlength(t, font=font) <= width:
            cur = t
        else:
            lines.append(cur); cur = w
    if cur:
        lines.append(cur)
    return lines


def caption(draw, text, fast=False):
    if not text:
        return
    lines = wrap(text, SANS, W - 120, draw)
    h = 24 + 40 * len(lines)
    draw.rectangle([0, H - h - 10, W, H], fill=CAPBG)
    for i, l in enumerate(lines):
        draw.text((60, H - h + 4 + 40 * i), l, font=SANS, fill=CAPFG)
    if fast:
        draw.text((W - 330, 20), ">> wait shortened", font=SANS, fill=(240, 190, 80))


def term_frame(screen, cap, fast=False):
    img = Image.new("RGB", (W, H), BG)
    d = ImageDraw.Draw(img)
    for y, line in enumerate(screen.display):
        line = line.rstrip()
        if not line:
            continue
        yy = Y0 + y * LH
        if line.startswith("$ "):
            d.text((X0, yy), line, font=MONOB, fill=PROMPT)
            continue
        d.text((X0, yy), line, font=MONO, fill=FG)
        # colour the status word of a result line (same text, colour only)
        s = line.strip()
        for word, col in STATUS.items():
            if line.startswith("  ") and not line.startswith("   ") and s.endswith(word):
                prefix = line[:len(line) - len(word)]
                d.rectangle([X0 + d.textlength(prefix, font=MONO), yy, W, yy + LH - 1], fill=BG)
                d.text((X0 + d.textlength(prefix, font=MONO), yy), word, font=MONOB, fill=col)
                break
    caption(d, cap, fast)
    return img


def card(lines, sub=None):
    img = Image.new("RGB", (W, H), (10, 12, 16))
    d = ImageDraw.Draw(img)
    y = 260 if sub else 380
    for i, (t, f) in enumerate(lines):
        tw = d.textlength(t, font=f)
        d.text(((W - tw) / 2, y), t, font=f, fill=(255, 255, 255))
        y += 90 if f is SANSB else 60
    if sub:
        y += 30
        for l in sub:
            for wl in wrap(l, SANS, W - 400, d):
                tw = d.textlength(wl, font=SANS)
                d.text(((W - tw) / 2, y), wl, font=SANS, fill=(200, 205, 212))
                y += 44
            y += 18
    return img


def main(ts, timing, markers, out):
    raw = open(ts, "rb").read()
    raw = raw[raw.index(b"\n") + 1:]          # drop the "Script started" header
    events, pos, t = [], 0, 0.0
    for l in open(timing):
        dt, n = l.split(); t += float(dt); n = int(n)
        events.append((t, raw[pos:pos + n])); pos += n
    marks = []
    for l in open(markers):
        a, name = l.split(); marks.append((float(a), name))
    # align: the first prompt "$ " of the first command = first marker
    acc, first = b"", None
    for et, chunk in events:
        acc += chunk
        if b"$ " in acc:
            first = et; break
    off = marks[0][0] - first
    marks = [(a - off, n) for a, n in marks]

    ff = subprocess.Popen(["ffmpeg", "-y", "-loglevel", "error", "-f", "rawvideo", "-pix_fmt", "rgb24",
                           "-s", "%dx%d" % (W, H), "-r", str(FPS), "-i", "-", "-an",
                           "-c:v", "libx264", "-pix_fmt", "yuv420p", "-crf", "20", "-preset", "medium",
                           "-movflags", "+faststart", out], stdin=subprocess.PIPE)
    nframes = [0]

    def emit(img, secs):
        b = img.tobytes()
        for _ in range(max(1, round(secs * FPS))):
            ff.stdin.write(b); nframes[0] += 1

    emit(card([("QX PORTMAP", SANSB), ("For every QNX symbol your code calls:", SANSM),
               ("is it still documented in QNX 8.0?", SANSM)]), 6)

    screen = pyte.Screen(COLS, ROWS); stream = pyte.ByteStream(screen)
    state = None; mi = 0; vt_prev = 0.0; last_img = None
    for et, chunk in events:
        # markers passed before this event
        while mi < len(marks) and marks[mi][0] <= et:
            name = marks[mi][1]
            if name in HOLD and last_img is not None:
                state = name
                last_img = term_frame(screen, CAPTIONS.get(name, ""))
                emit(last_img, HOLD[name])
            else:
                state = name
            mi += 1
        gap = et - vt_prev
        fast = False
        if gap > MAXGAP:
            fast = state == "quick"
            gap = SHORTGAP
        if last_img is not None:
            emit(last_img if not fast else term_frame(screen, CAPTIONS.get(state, ""), True), gap)
        stream.feed(chunk)
        vt_prev = et
        last_img = term_frame(screen, CAPTIONS.get(state, ""))
    while mi < len(marks):
        name = marks[mi][1]
        if name in HOLD:
            emit(term_frame(screen, CAPTIONS.get(name, "")), HOLD[name])
        mi += 1

    emit(card([("Measured on real QNX code", SANSB)],
              ["100 QNX symbols really called by five public QNX repositories (pinned commits).",
               "96 are resolved and quoted with the official QNX 8.0 page. The 4 others were in the 7.1 reference and are gone from the 8.0 one: the tool says so.",
               "Full mode: about 3,400 official pages rebuilt once (scripts/bootstrap_corpus.sh), then offline, with the SHA-256 of every page, and the word 'absent'."]), 12)
    emit(card([("Honest limits", SANSB)],
              ["Not shown yet: the tool running on a QNX 8.0 target itself (that needs the QNX SDP 8.0 licence). It is a host tool, which the rules allow.",
               "The QNX documentation is not redistributed: it is downloaded from the official site.",
               "AI-assisted development: every statement about a QNX symbol quotes an official page."]), 11)
    emit(card([("QX PORTMAP", SANSB), ("github.com/tgg49099-dotcom/qnx-qx-portmap", SANSM),
               ("MIT licence", SANSM)]), 5)
    ff.stdin.close(); ff.wait()
    print("frames", nframes[0], "seconds", nframes[0] / FPS, "rc", ff.returncode)


if __name__ == "__main__":
    main(*sys.argv[1:])
