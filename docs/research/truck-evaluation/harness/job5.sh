#!/usr/bin/env bash
# second probe batch: STEP entity census, determinism, tolerance sweep, licences, wasm
set -u
echo "== build"; cargo build --release 2>&1 | tail -2
BIN=target/release/trucktorture
OUT=/tmp/out5; mkdir -p $OUT
apt-get update -qq 2>&1 | tail -1; apt-get install -y -qq python3 2>&1 | tail -1
echo "== step census"
for spec in "25 0.2" "12 0.05" "29 0.05" "27 0.2"; do set -- $spec
  timeout 150 $BIN run cases.json $1 $2 $OUT > /tmp/o.txt 2>/dev/null
  f=$(ls $OUT/$(printf %02d $(($1+1)))_t$2.step 2>/dev/null)
  echo "-- case idx=$1 tol=$2 file=$f"
  [ -n "$f" ] && { grep -ho '^#[0-9]*= *[A-Z_0-9]*' $f | sed 's/#[0-9]*= *//' | sort | uniq -c | sort -rn | head -22 | tr '\n' ';'; echo; grep -m3 -n 'FILE_SCHEMA\|FILE_NAME\|MANIFOLD_SOLID_BREP\|CLOSED_SHELL' $f | cut -c1-120; }
done
echo "== determinism (3 runs each, tol 0.05)"
for idx in 10 12 25 27 29; do for r in 1 2 3; do
  timeout 150 $BIN run cases.json $idx 0.05 $OUT 2>/dev/null | grep '^RES' | grep -o '"status":"[a-z_]*"\|"faces":[0-9]*\|"vol":[-0-9.e]*' | head -4 | tr '\n' ' '; echo " idx=$idx run=$r"
done; done
echo "== tolerance sweep"
for idx in 0 20 24 25 26 16; do for t in 0.5 0.1 0.02 0.005; do
  /usr/bin/time -f "wall=%es rss=%MKB" timeout 200 $BIN run cases.json $idx $t $OUT > /tmp/o.txt 2> /tmp/e.txt
  echo "idx=$idx tol=$t rc=$? $(grep '^RES' /tmp/o.txt | grep -o '"status":"[a-z_]*"\|"steps_done":[0-9]*\|"boolean_ms_total":[0-9.]*' | tr '\n' ' ') $(tail -1 /tmp/e.txt)"
done; done
echo "== licences (transitive deps of harness)"
cargo metadata --format-version 1 > /tmp/md.json 2>/dev/null
python3 -c "
import json,collections
d=json.load(open('/tmp/md.json'));c=collections.Counter();odd=[]
for p in d['packages']:
    c[p.get('license') or 'NONE']+=1
    if not p.get('license') or 'GPL' in (p.get('license') or '') or 'MPL' in (p.get('license') or ''): odd.append((p['name'],p.get('license')))
print('n_packages',len(d['packages']));print(c.most_common(12));print('odd',odd)
"
echo "== wasm build of truck-js"
rustup target add wasm32-unknown-unknown 2>&1 | tail -1
D=$(ls -d /usr/local/cargo/git/checkouts/truck-*/88ed005 | head -1); echo "checkout=$D"
cd $D && (time cargo build --release --target wasm32-unknown-unknown -p truck-js 2>&1 | tail -4)
ls -la target/wasm32-unknown-unknown/release/*.wasm 2>&1 | head -3
cd $D && grep -c "wasm_bindgen" truck-js/src/*.rs | tr '\n' ' '
echo "== done"
