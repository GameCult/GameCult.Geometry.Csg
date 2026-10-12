#!/usr/bin/env bash
# Yggdrasil job: build the driver with the Manifold kernel and run every case; results go to stdout as a
# base64 tarball between markers (the log is the only channel back).
set -euo pipefail
cd spikes/boolean-weld
echo "TOOLS cmake=$(command -v cmake || echo none) cxx=$(command -v c++ || echo none) git=$(command -v git || echo none)"
if ! command -v cmake >/dev/null; then (apt-get update -qq && apt-get install -y -qq cmake) || pip install cmake || true; fi
t0=$(date +%s); cargo build --release --features manifold 2>&1 | tail -20; echo "BUILD_SECONDS $(( $(date +%s) - t0 ))"
mkdir -p runs
python3 - <<'PY'
import json, subprocess
for c in json.load(open('cutters/cases.json')):
    r = subprocess.run(['target/release/spike-boolean-weld', 'manifold', c['op'], 'fixtures/hull_nobevel.obj', c['cutter'], 'runs/manifold_' + c['name']], capture_output=True, text=True)
    print(c['name'], r.stdout.strip() or ('FAIL ' + r.stderr.strip()[-400:]))
PY
echo "BEGIN_TARBALL"; tar czf - runs | base64 -w0; echo; echo "END_TARBALL"
ls runs | wc -l
