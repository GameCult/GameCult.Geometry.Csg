#!/usr/bin/env bash
# usage: job.sh <tol>   (runs inside the stopgap rust container, cwd = repo root)
TOLS="${*:-0.05}"
set -u
OUT=/tmp/out; mkdir -p $OUT
echo "== build"
cargo build --release 2>&1 | tail -30
BIN=target/release/trucktorture
[ -x $BIN ] || { echo BUILD-FAILED; exit 1; }
echo "== prims"
$BIN prims 2>&1 | tail -8
N=$(grep -c '"name"' cases.json)
echo "cases=$N"
for TOL in $TOLS; do
echo "== cases tol=$TOL"
for i in $(seq 0 $((N-1))); do
  s=$(date +%s.%N)
  timeout ${CASE_TIMEOUT:-150} $BIN run cases.json $i $TOL $OUT > /tmp/case_$i.out 2> /tmp/case_$i.err
  rc=$?
  e=$(date +%s.%N)
  echo "CASE idx=$i rc=$rc wall=$(echo "$e - $s" | bc 2>/dev/null || echo ?)"
  grep -h '^RES' /tmp/case_$i.out | cut -c1-1500
  if [ $rc -ne 0 ]; then echo "STDERR-TAIL idx=$i: $(tail -c 400 /tmp/case_$i.err | tr '\n' ' ')"; fi
done
done
echo "== python/ocp"
apt-get update -qq 2>&1 | tail -2
apt-get install -y -qq python3 python3-pip libgl1 libglu1-mesa libxrender1 2>&1 | tail -3
PY=python3
$PY -m pip install -q --break-system-packages cadquery-ocp 2>&1 | tail -3
$PY -c "import OCP; print('OCP ok')" 2>&1 | tail -2
echo "== ref (OCCT reference booleans)"
$PY check.py ref cases.json $OUT 2>&1 | cut -c1-400
echo "== check truck output (STEP via OCCT, OBJ independent)"
$PY check.py all $OUT 2>&1 | cut -c1-500
echo "== truck reads OCCT-written STEP"
for f in $OUT/ref_*.step; do timeout 120 $BIN readstep $f 2>&1 | grep -h '^RES' | cut -c1-500 || echo "READSTEP-FAIL $f"; done
echo "== done"
