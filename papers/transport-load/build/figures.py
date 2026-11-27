"""Figures for the transport paper. Usage: python3 figures.py results.json out_dir"""
import json, sys, math
import matplotlib
matplotlib.use('Agg')
import matplotlib.pyplot as plt
from matplotlib.patches import FancyBboxPatch, FancyArrowPatch
from matplotlib.lines import Line2D

plt.rcParams['font.family'] = 'Liberation Serif'
plt.rcParams.update({'mathtext.fontset': 'custom', 'mathtext.rm': 'Liberation Serif', 'mathtext.it': 'Liberation Serif:italic'})
RES, OUT = sys.argv[1], sys.argv[2]
GRAY, EDGE = '#f2f2f2', '#404040'

def box(ax, x, y, w, h, fill='white', lw=1.6):
    ax.add_patch(FancyBboxPatch((x, y), w, h, boxstyle='round,pad=0,rounding_size=0.06',
                                fc=fill, ec=EDGE, lw=lw))

def txt(ax, x, y, s, size=15, bold=False):
    ax.text(x, y, s, ha='center', va='center', fontsize=size, fontweight='bold' if bold else 'normal',
            linespacing=1.25)

def arrow(ax, x1, y1, x2, y2):
    ax.add_patch(FancyArrowPatch((x1, y1), (x2, y2), arrowstyle='-|>', mutation_scale=16, lw=1.6, color=EDGE))

# ---------------- Figure 1: four-step model ----------------
fig = plt.figure(figsize=(14.4, 11.15), dpi=200)
ax = fig.add_axes([0, 0, 1, 1]); ax.set_xlim(0, 14.4); ax.set_ylim(0, 11.15); ax.axis('off')
stages = [
    ('1. ГЕНЕРАЦИЯ', 'Қанша сапар\nпайда болады?', 'Аймақтан шығатын ($O_i$) және\nаймаққа келетін ($D_j$) сапарлар',
     'тұрғындар мен жұмыс орындары бойынша'),
    ('2. ТАРАЛУ', 'Сапарлар қайда\nбағытталады?', 'Корреспонденция матрицасы $T_{ij}$',
     'гравитациялық модель, Фурнесс әдісі'),
    ('3. КӨЛІК ТҮРІН\nТАҢДАУ', 'Немен\nбарады?', 'Жеке көлік пен қоғамдық көлік үлесі',
     'бинарлық логит модель'),
    ('4. ЖҮКТЕМЕНІ\nТАРАТУ', 'Қай жолмен\nжүреді?', 'Желі сілтемелеріндегі ағын $x_a$',
     'Вардроп тепе-теңдігі, BPR, Франк–Вулф'),
]
top = 10.85; rowh = 1.85; gap = 0.42
for k, (lab, q, main, sub) in enumerate(stages):
    y = top - (k + 1) * rowh - k * gap
    box(ax, 0.3, y, 10.6, rowh)
    box(ax, 0.45, y + 0.15, 2.6, rowh - 0.3, fill=GRAY)
    txt(ax, 1.75, y + rowh * 0.66, lab, 16, True)
    txt(ax, 1.75, y + rowh * 0.27, q, 14)
    box(ax, 3.3, y + 0.15, 7.45, rowh - 0.3)
    txt(ax, 7.02, y + rowh * 0.62, main, 16, True)
    txt(ax, 7.02, y + rowh * 0.3, sub, 14)
    ax.plot([10.9, 11.3], [y + rowh / 2] * 2, color=EDGE, lw=1.6)
    if k < 3:
        arrow(ax, 5.6, y - 0.02, 5.6, y - gap + 0.04)
ybot = top - 4 * rowh - 3 * gap
box(ax, 11.3, ybot, 2.8, top - ybot, fill=GRAY)
txt(ax, 12.7, (top + ybot) / 2 + 1.9, 'КЕРІ\nБАЙЛАНЫС', 17, True)
txt(ax, 12.7, (top + ybot) / 2 - 0.5,
    'Жүктемеге сай\nжүру уақыты\nқайта есептеліп,\nалдыңғы\nсатыларға\nберіледі\n\nКіріс деректер:\nаймақтар,\nжелі, өткізу\nқабілеті', 14)
arrow(ax, 5.6, ybot - 0.02, 5.6, ybot - 0.55)
box(ax, 0.3, 0.25, 13.8, 1.35, fill=GRAY)
txt(ax, 7.2, 1.18, 'НӘТИЖЕ', 18, True)
txt(ax, 7.2, 0.62, 'сілтемелердің жүктелу деңгейі (V/C), желідегі жалпы жүру уақыты, жобалық нұсқаларды салыстыру', 15)
fig.savefig(f'{OUT}/fig1.png'); plt.close(fig)

# ---------------- Figure 2: network loads S0 vs S2 ----------------
r = json.load(open(RES))
NODES = {1: (0, 0), 2: (2, 0), 3: (4, 0), 4: (0, 2), 5: (2, 2), 6: (4, 2), 7: (0, 4), 8: (2, 4), 9: (4, 4)}
ZL = {1: 'A', 3: 'B', 5: 'C', 7: 'D', 9: 'E', 2: 'F'}
LEV = [(0.6, '#bdbdbd', 'V/C < 0,6'), (0.9, '#e6a23c', '0,6–0,9'), (1.0, '#d9531e', '0,9–1,0'),
       (9e9, '#8b0000', 'V/C > 1,0')]
def col(vc):
    for lim, c, _ in LEV:
        if vc < lim:
            return c

fig, axs = plt.subplots(1, 2, figsize=(14.4, 7.6), dpi=200)
for ax, s, title in zip(axs, ('S0', 'S2'), ('а) Базалық желі (S0)', 'ә) Жаңа 7–5 көшесімен (S2)')):
    ax.set_aspect('equal'); ax.axis('off'); ax.set_xlim(-0.8, 4.8); ax.set_ylim(-0.9, 4.75)
    for d in r['scen'][s]['links']:
        (xa, ya), (xb, yb) = NODES[d['a']], NODES[d['b']]
        L = math.hypot(xb - xa, yb - ya); nx_, ny_ = -(yb - ya) / L, (xb - xa) / L
        off = 0.09
        w = 1.2 + d['x'] / 140
        sh = 0.22
        x1, y1 = xa + nx_ * off + (xb - xa) / L * sh, ya + ny_ * off + (yb - ya) / L * sh
        x2, y2 = xb + nx_ * off - (xb - xa) / L * sh, yb + ny_ * off - (yb - ya) / L * sh
        ax.plot([x1, x2], [y1, y2], color=col(d['vc']), lw=w, solid_capstyle='butt')
        if d['x'] > 400:
            mx, my = (x1 + x2) / 2 + nx_ * (0.16 + w / 260), (y1 + y2) / 2 + ny_ * (0.16 + w / 260)
            ax.text(mx, my, f"{d['vc']:.2f}".replace('.', ','), fontsize=11, ha='center', va='center',
                    bbox=dict(fc='white', ec='none', pad=0.5))
    for n, (x, y) in NODES.items():
        z = ZL.get(n)
        ax.add_patch(plt.Circle((x, y), 0.2, fc=GRAY if z else 'white', ec=EDGE, lw=1.4, zorder=5))
        ax.text(x, y, f'{n}', ha='center', va='center', fontsize=13, fontweight='bold', zorder=6)
        if z:
            ax.text(x - 0.32, y + 0.3, z, ha='center', va='center', fontsize=14, fontstyle='italic', zorder=6)
    ind = r['scen'][s]['ind']
    ax.text(2, -0.62, f"{title}\nTSTT = {ind['TSTT']:.0f} авт·сағ, max V/C = {ind['maxVC']:.2f}".replace('.', ','),
            ha='center', va='center', fontsize=15)
handles = [Line2D([0], [0], color=c, lw=6, label=l) for _, c, l in LEV]
fig.legend(handles=handles, loc='upper center', ncol=4, fontsize=14, frameon=False, bbox_to_anchor=(0.5, 0.995))
fig.subplots_adjust(left=0.01, right=0.99, top=0.93, bottom=0.01, wspace=0.05)
fig.savefig(f'{OUT}/fig2.png'); plt.close(fig)
print('ok')
