#!/usr/bin/env bash
# usage: hf_fetch.sh <job_id> <out_path_without_ext>
id="$1"; out="$2"
json="$(higgsfield generate wait "$id" --json --timeout 30m --quiet 2>&1)"
url="$(printf '%s' "$json" | python -c "import sys,json; d=json.load(sys.stdin); print(d.get('result_url') or '')" 2>/dev/null)"
status="$(printf '%s' "$json" | python -c "import sys,json; d=json.load(sys.stdin); print(d.get('status'))" 2>/dev/null)"
if [ -z "$url" ]; then echo "FAIL $id status=$status :: $(printf '%s' "$json" | head -c 400)"; exit 1; fi
ext="${url##*.}"; ext="${ext%%\?*}"
curl -sL "$url" -o "$out.$ext" && echo "OK $id -> $out.$ext"
