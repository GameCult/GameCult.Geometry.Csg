#!/usr/bin/env bash
# third probe batch: STEP entity census, case-25 stage timing, tolerance sweep
set -u
echo "== build"; cargo build --release 2>&1 | tail -2
BIN=target/release/trucktorture
OUT=/tmp/out6; mkdir -p $OUT
echo "== step census"
for spec in "25 0.2" "12 0.05" "29 0.05" "27 0.2" "10 0.05"; do
  set -- $spec
  timeout 150 $BIN run cases.json $1 $2 $OUT > /tmp/o.txt 2>/dev/null
  f=$(ls $OUT/$(printf %02d $(($1+1)))_t$2.step 2>/dev/null)
  echo "-- case idx=$1 tol=$2 file=$f"
  if [ -n "$f" ]; then
    grep -ho '^#[0-9]* *= *[A-Z_0-9]*' $f | sed 's/#[0-9]* *= *//' | sort | uniq -c | sort -rn | head -24 | tr '\n' ';'
    echo
  fi
done
echo "== case 25 stage timing x3"
for r in 1 2 3; do
  timeout 200 $BIN run cases.json 24 0.05 $OUT 2>&1 >/dev/null | grep STAGE | tr '\n' ' '
  echo " run=$r"
done
echo "== tolerance sweep"
for idx in 0 20 24 25 26 16; do
  for t in 0.5 0.1 0.02 0.005; do
    s0=$(date +%s%N)
    timeout 200 $BIN run cases.json $idx $t $OUT > /tmp/o.txt 2> /tmp/e.txt
    rc=$?
    echo "idx=$idx tol=$t rc=$rc wall=$(( ($(date +%s%N)-s0)/1000000 ))ms $(grep '^RES' /tmp/o.txt | grep -o '"status":"[a-z_]*"\|"steps_done":[0-9]*\|"boolean_ms_total":[0-9.]*' | tr '\n' ' ')"
  done
done
echo "== done"
