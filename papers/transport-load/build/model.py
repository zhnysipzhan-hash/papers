"""Four-step transport demand model and user-equilibrium (Frank-Wolfe) load model
for a conditional 9-node urban district network.

Usage: python3 model.py [out_dir]
Prints all numbers used in the paper and writes results.json.
"""
import json, math, sys
import numpy as np
import networkx as nx
from scipy import stats

OUT = sys.argv[1] if len(sys.argv) > 1 else '.'

# ---------------- network ----------------
# node: (x km, y km)
NODES = {1: (0, 0), 2: (2, 0), 3: (4, 0), 4: (0, 2), 5: (2, 2), 6: (4, 2),
         7: (0, 4), 8: (2, 4), 9: (4, 4)}
# undirected link: (a, b, class)
ART, COL, LOC = 'art', 'col', 'loc'
CLASS = {ART: dict(v=50, c=1800), COL: dict(v=40, c=1200), LOC: dict(v=30, c=900)}
UNDIR = [(1, 2, COL), (2, 3, COL), (4, 5, ART), (5, 6, ART), (7, 8, COL), (8, 9, LOC),
         (1, 4, COL), (4, 7, LOC), (2, 5, ART), (5, 8, ART), (3, 6, COL), (6, 9, COL)]

def build(extra=(), cap_mult=None):
    links = []
    for a, b, cl in list(UNDIR) + list(extra):
        (xa, ya), (xb, yb) = NODES[a], NODES[b]
        L = math.hypot(xa - xb, ya - yb)
        v, c = CLASS[cl]['v'], CLASS[cl]['c']
        for u, w in ((a, b), (b, a)):
            cc = c * (cap_mult.get((u, w), 1.0) if cap_mult else 1.0)
            links.append(dict(a=u, b=w, L=L, t0=L / v * 60, c=cc, cls=cl))
    return links

# ---------------- zones ----------------
ZN = ['A', 'B', 'C', 'D', 'E', 'F']
ZNODE = [1, 3, 5, 7, 9, 2]
POP = np.array([45, 40, 15, 50, 10, 20], float) * 1000
JOBS = np.array([5, 6, 35, 4, 25, 10], float) * 1000
RATE = 0.09          # peak-hour person trips per resident
ATTR_J, ATTR_P = 0.16, 0.01
BETA = 0.10          # gravity deterrence, 1/min
LAM, ASC_CAR = 0.08, -0.30   # logit
PT_FACTOR, PT_WAIT, PARK = 1.5, 8.0, 5.0
OCC = 1.3
T_INTRA = 3.0
ALPHA_BPR, BETA_BPR = 0.15, 4.0

def skim(links, times):
    G = nx.DiGraph()
    for l, t in zip(links, times):
        G.add_edge(l['a'], l['b'], w=t)
    n = len(ZNODE)
    T = np.zeros((n, n))
    for i, zi in enumerate(ZNODE):
        d = nx.single_source_dijkstra_path_length(G, zi, weight='w')
        for j, zj in enumerate(ZNODE):
            T[i, j] = T_INTRA if i == j else d[zj]
    return T

def furness(O, D, F, it=200):
    b = np.ones(len(D))
    for _ in range(it):
        a = O / (F @ b)
        b = D / (F.T @ a)
    return (a[:, None] * F) * b[None, :]

def demand(links, pop=POP, jobs=JOBS, beta=BETA):
    O = RATE * pop
    D = ATTR_J * jobs + ATTR_P * pop
    D = D * O.sum() / D.sum()
    t0 = np.array([l['t0'] for l in links])
    C = skim(links, t0)
    T = furness(O, D, np.exp(-beta * C))
    Vc = ASC_CAR - LAM * (C + PARK)
    Vp = -LAM * (PT_FACTOR * C + PT_WAIT)
    Pcar = 1 / (1 + np.exp(Vp - Vc))
    car = T * Pcar / OCC
    np.fill_diagonal(car, 0.0)     # intra-zonal trips do not load the network
    return dict(O=O, D=D, C=C, T=T, Pcar=Pcar, car=car)

def bpr(l, x):
    return l['t0'] * (1 + ALPHA_BPR * (x / l['c']) ** BETA_BPR)

def aon(links, times, od):
    G = nx.DiGraph()
    idx = {}
    for k, (l, t) in enumerate(zip(links, times)):
        G.add_edge(l['a'], l['b'], w=t); idx[(l['a'], l['b'])] = k
    y = np.zeros(len(links))
    for i, zi in enumerate(ZNODE):
        paths = nx.single_source_dijkstra_path(G, zi, weight='w')
        for j, zj in enumerate(ZNODE):
            if i == j or od[i, j] <= 0:
                continue
            p = paths[zj]
            for u, w in zip(p[:-1], p[1:]):
                y[idx[(u, w)]] += od[i, j]
    return y

def frank_wolfe(links, od, gap_tol=1e-5, max_it=500):
    t = np.array([l['t0'] for l in links])
    x = aon(links, t, od)
    for it in range(max_it):
        t = np.array([bpr(l, xi) for l, xi in zip(links, x)])
        y = aon(links, t, od)
        gap = (t @ (x - y)) / (t @ x)
        if gap < gap_tol:
            break
        d = y - x
        lo, hi = 0.0, 1.0
        for _ in range(50):  # bisection on derivative of Beckmann objective
            m = (lo + hi) / 2
            g = sum(bpr(l, xi) * di for l, xi, di in zip(links, x + m * d, d))
            lo, hi = (m, hi) if g < 0 else (lo, m)
        x = x + (lo + hi) / 2 * d
    return x, it + 1, gap

def indicators(links, x):
    t = np.array([bpr(l, xi) for l, xi in zip(links, x)])
    vc = x / np.array([l['c'] for l in links])
    L = np.array([l['L'] for l in links])
    tstt = float(x @ t) / 60               # veh-h
    vkt = float(x @ L)                     # veh-km
    return dict(TSTT=tstt, VKT=vkt, speed=vkt / tstt, maxVC=float(vc.max()),
                n09=int((vc > 0.9).sum()), n10=int((vc > 1.0).sum()),
                meanVC=float(vc.mean()), vc=vc, t=t)

def run(links, dem):
    x, it, gap = frank_wolfe(links, dem['car'])
    return x, it, gap, indicators(links, x)

if __name__ == '__main__':
    base = build()
    dem = demand(base)
    res = {}
    print('O', dem['O'].round(0), 'D', dem['D'].round(0))
    print('person trips', dem['T'].sum().round(0), 'car share (trip-weighted, excl intra)',
          (dem['T'] * dem['Pcar'] * (1 - np.eye(6))).sum() / (dem['T'] * (1 - np.eye(6))).sum())
    print('car veh/h', dem['car'].sum().round(1))
    print('car OD\n', dem['car'].round(0))
    print('skim\n', dem['C'].round(1))
    # AON free flow
    t0 = np.array([l['t0'] for l in base])
    xa = aon(base, t0, dem['car'])
    ia = indicators(base, xa)
    xb, it, gap, ib = run(base, dem)
    print('AON', {k: v for k, v in ia.items() if k not in ('vc', 't')})
    print('UE ', {k: v for k, v in ib.items() if k not in ('vc', 't')}, it, gap)
    for l, x1, x2, v1, v2 in zip(base, xa, xb, ia['vc'], ib['vc']):
        print(f"{l['a']}->{l['b']} {l['cls']} c={l['c']:.0f} AON={x1:7.0f} vc={v1:.2f} | UE={x2:7.0f} vc={v2:.2f}")
    res['base'] = dict(AON=ia, UE=ib, x_aon=xa.tolist(), x_ue=xb.tolist())

    # ---------------- design scenarios ----------------
    SCEN = {
        'S0': dict(extra=(), cm=None, mod=None),
        'S1': dict(extra=(), cm=None, mod=('7-8', ART)),   # 7-8 reconstructed to arterial
        'S2': dict(extra=((7, 5, ART),), cm=None, mod=None),  # new diagonal 7-5
    }
    def build_s(s):
        sc = SCEN[s]
        if sc['mod']:
            saved = list(UNDIR)
            UNDIR[:] = [(a, b, sc['mod'][1]) if f'{a}-{b}' == sc['mod'][0] else (a, b, c) for a, b, c in UNDIR]
            L = build(sc['extra']); UNDIR[:] = saved
            return L
        return build(sc['extra'])
    out = {}
    for s in SCEN:
        L = build_s(s)
        x, it, gap, ind = run(L, dem)
        out[s] = dict(ind={k: v for k, v in ind.items() if k not in ('vc', 't')}, it=it, gap=gap,
                      links=[dict(a=l['a'], b=l['b'], cls=l['cls'], c=l['c'], x=float(xi), vc=float(v), t0=l['t0'], t=float(tt))
                             for l, xi, v, tt in zip(L, x, ind['vc'], ind['t'])])
        print(s, out[s]['ind'], it)
        print('   top vc:', sorted([(round(d['vc'], 2), f"{d['a']}->{d['b']}") for d in out[s]['links']], reverse=True)[:5])
    # OD travel time D->C under each scenario
    # ---------------- Monte Carlo sensitivity ----------------
    rng = np.random.default_rng(2026)
    N = 300
    mc = {s: [] for s in SCEN}; mcmax = {s: [] for s in SCEN}
    nets = {s: build_s(s) for s in SCEN}
    for k in range(N):
        g = rng.uniform(0.9, 1.2)
        pop = POP * rng.uniform(0.85, 1.15, 6) * g
        jobs = JOBS * rng.uniform(0.85, 1.15, 6) * g
        beta = rng.uniform(0.08, 0.12)
        dm = demand(nets['S0'], pop, jobs, beta)   # demand from base skims (same OD for all scenarios)
        for s in SCEN:
            x, it, gap, ind = run(nets[s], dm)
            mc[s].append(ind['TSTT']); mcmax[s].append(ind['maxVC'])
    for s in SCEN:
        a = np.array(mc[s]); m = np.array(mcmax[s])
        print(s, 'TSTT mean', a.mean().round(1), 'sd', a.std(ddof=1).round(1), 'maxVC mean', m.mean().round(3),
              'share maxVC>1', (m > 1).mean().round(3))
    for s in ('S1', 'S2'):
        d = np.array(mc['S0']) - np.array(mc[s])
        w = stats.wilcoxon(np.array(mc['S0']), np.array(mc[s]), alternative='greater')
        rel = d / np.array(mc['S0']) * 100
        print(s, 'diff mean', d.mean().round(1), 'rel% mean', rel.mean().round(1), 'min', rel.min().round(1), 'max', rel.max().round(1),
              'n improved', int((d > 0).sum()), 'W', w.statistic, 'p', w.pvalue)
    d12 = np.array(mc['S1']) - np.array(mc['S2'])
    print('S1-S2 diff mean', d12.mean().round(1), 'n S2 better', int((d12 > 0).sum()), stats.wilcoxon(np.array(mc['S1']), np.array(mc['S2'])))
    json.dump(dict(base_dem=dict(O=dem['O'].tolist(), D=dem['D'].tolist(), car=dem['car'].tolist(), C=dem['C'].tolist(),
                                 T=dem['T'].tolist(), Pcar=dem['Pcar'].tolist()),
                   aon=dict(ind={k: v for k, v in ia.items() if k not in ('vc', 't')}, x=xa.tolist()),
                   scen=out, mc=mc, mcmax=mcmax), open(f'{OUT}/results.json', 'w'), indent=1)
