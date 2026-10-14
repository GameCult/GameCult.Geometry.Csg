import sys, re, collections
for f in sys.argv[1:]:
    t = open(f).read()
    ec = set(re.findall(r"#(\d+)=EDGE_CURVE", t))
    uses = collections.Counter()
    for m in re.finditer(r"ORIENTED_EDGE\([^,]*,\*,\*,#(\d+),", t):
        uses[m.group(1)] += 1
    hist = collections.Counter(uses.values())
    print("EDGES", f.split("/")[-1], "edge_curves", len(ec), "oriented_edge_uses_per_edge_histogram", dict(hist), "edges_never_used", len(ec - set(uses)))
