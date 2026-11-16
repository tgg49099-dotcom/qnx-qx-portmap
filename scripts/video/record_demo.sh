#!/bin/bash
# Records the terminal session of the QX PORTMAP demo video, from the PUBLIC repository.
# Every command shown is really executed, starting with a fresh git clone.
# Usage (140x38 terminal):
#   script -q -T timing.log -c "stty cols 140 rows 38; scripts/video/record_demo.sh /tmp/vid/markers.txt" typescript
# Then: python3 scripts/video/render_demo.py typescript timing.log /tmp/vid/markers.txt demo.mp4
# Needs network access to github.com and www.qnx.com (about 76 pages at one request per second).
M=${1:-/tmp/vid/markers.txt}; mkdir -p "$(dirname "$M")"; : > "$M"
REPO=${QX_PORTMAP_REPO:-https://github.com/tgg49099-dotcom/qnx-qx-portmap}
export HOME=/tmp/judge; rm -rf /tmp/judge; mkdir -p /tmp/judge; cd /tmp/judge || exit 1
run() { echo "$(date +%s.%N) $1" >> "$M"; printf '$ '; local s="$2"; for ((i=0;i<${#s};i++)); do printf '%s' "${s:$i:1}"; sleep 0.03; done; sleep 0.4; printf '\n'; eval "$2"; echo "$(date +%s.%N) end$1" >> "$M"; sleep 1; }
clear
run cd "git clone -q $REPO && cd qnx-qx-portmap && git log -1 --format=%h && python3 --version"
run quick "python3 -m qnx_portmap --quick abort bzero zzz_fonction_inexistante; echo \"exit code: \$?\""
clear
run qnx "python3 -m qnx_portmap --quick accept MsgSend; echo \"exit code: \$?\""
clear
run json "python3 -m qnx_portmap --quick --format json MsgSend 2>/dev/null | head -30"
clear
run tests "python3 -m unittest discover -s tests -t . 2>&1 | tail -3"
sleep 1
