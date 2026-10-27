#!/bin/bash
# Assemble index.html + omnibinder.db.wasm from the source parts.
set -e
S=/tmp/claude-0/-home-claude/a8fddf89-7924-5379-a951-760823380930/scratchpad
OUT=/home/claude/omnibinder
BUILD=$(date -u +%Y-%m-%d.%H%M)
base64 -d "$S/data/db.b64" > "$OUT/omnibinder.db.wasm"
{ cat "$S/app_head.html"; printf '<script>const BUILD="%s";</script>\n' "$BUILD"; cat "$S/app_tail.html"; } > "$OUT/index.html"
python3 -I -c "import re;s=open('$OUT/index.html').read();open('$S/check.js','w').write(re.findall(r'<script>(.*?)</script>',s,re.S)[-1])" && node --check "$S/check.js"
ls -la "$OUT"
