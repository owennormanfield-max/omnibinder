#!/usr/bin/env python3
"""all.json -> db.b64 (gzipped, base64) consumed by build.sh.
Card row: [set, num, names, cat, rar, hp, types, stage, reg, dex, ill, variants, suffix, img(ptcg), alt(ptcg), scanLangs, jp]
  img/alt: pokemontcg.io path suffix (set/num.png) ; scanLangs: languages TCGdex has a scan for ; jp: official pokemon-card.com path suffix"""
import json, gzip, base64
S_ = '/tmp/claude-0/-home-claude/a8fddf89-7924-5379-a951-760823380930/scratchpad/'
d = json.load(open(S_ + 'data/all.json')); C = d['cards']; S = d['sets']
def idx(lst, v):
    if v is None: return -1
    if v not in lst: lst.append(v)
    return lst.index(v)
rar = []; cat = []; stage = []; typ = []; ill = []; ser = []; VT = []; VST = []; VSTAMP = []; VFOIL = []
setids = sorted(S.keys()); sets = []
for sid in setids:
    s = S[sid]; sn = s.get('serie') or {}
    sname = sn.get('en') or sn.get('ja') or (list(sn.values())[0] if sn else '')
    sets.append({'i': s['id'], 'n': s.get('name') or {}, 's': idx(ser, sname), 'si': s.get('serieId'), 'd': s.get('date'), 'c': s.get('count'), 'a': s.get('abbr'), 'r': s.get('region')})
simap = {sid: i for i, sid in enumerate(setids)}
def normstamp(x): return x.lower().replace(' ', '-')
PFX = 'https://images.pokemontcg.io/'
cards = []; nv = 0
import re
BASIC_EN=re.compile(r'^(Basic )?(Grass|Fire|Water|Lightning|Psychic|Fighting|Darkness|Metal|Fairy|Dragon|Colorless) Energy$',re.I)
BASIC_JA=re.compile(r'^基本.*エネルギー$')
def is_basic_energy(c):
    if c.get('cat')!='Energy': return False
    if c.get('energyType')=='Normal': return True
    if c.get('energyType')=='Special': return False
    n=c.get('name') or {}
    return bool(BASIC_EN.match(n.get('en','')) or BASIC_JA.match(n.get('ja','')))
def tpid(c):
    if c.get('tp'): return c['tp']
    for v in (c.get('vars') or []):
        if isinstance(v, dict) and v.get('tp'): return v['tp']
    return 0
EXCL=json.load(open(S_+'exclusions.json'))
skipped=0;excluded=0
for c in C:
    if c['set'] not in simap: continue
    if is_basic_energy(c): skipped+=1; continue
    ex=EXCL.get(c['set']+'-'+c['num'])
    if ex=='all': excluded+=1; continue
    if isinstance(ex,list):
        c=dict(c); c['name']={k:v for k,v in c['name'].items() if k not in ex}
        if not c['name']: excluded+=1; continue
    r = c.get('rar'); r = None if r in (None, 'None') else r
    rg = c.get('reg'); rg = None if rg in (None, 'None') else rg.upper()
    vs = []
    for v in (c.get('vars') or []):
        if isinstance(v, str): v = {'t': v}
        stamps = sorted({normstamp(x) for x in (v.get('stamp') or [])})
        row = [idx(VT, v.get('t') or 'normal'), idx(VST, v.get('st')), [idx(VSTAMP, x) for x in stamps], idx(VFOIL, v.get('foil')), 1 if v.get('sz') == 'jumbo' else 0]
        if row not in vs: vs.append(row)
    if not vs: vs = [[idx(VT, 'normal'), -1, [], -1, 0]]
    nv += len(vs)
    img = c.get('img') or ''; alt = c.get('alt') or ''
    img = img.replace(PFX, '') if img.startswith(PFX) else img
    alt = alt.replace(PFX, '') if alt.startswith(PFX) else alt
    cards.append([simap[c['set']], c['num'], c.get('name') or {}, idx(cat, c.get('cat')), idx(rar, r), c.get('hp') or 0,
                  [idx(typ, t) for t in (c.get('types') or [])], idx(stage, c.get('stage')), rg or '', (c.get('dex') or [0])[0] or 0,
                  idx(ill, c.get('ill')), vs, c.get('suffix') or '', img, alt, c.get('scan') or [], c.get('jp') or '', c.get('ox') or {}, tpid(c), c.get('local') or ''])
def sdate(s):
    dd = s['d']
    if isinstance(dd, dict): dd = min(dd.values()) if dd else ''
    return dd or ''
cards.sort(key=lambda c: (sdate(sets[c[0]]), c[1].zfill(4) if c[1].isdigit() else c[1]))
out = {'rar': rar, 'cat': cat, 'stage': stage, 'typ': typ, 'ill': ill, 'ser': ser, 'vt': VT, 'vst': VST, 'vstamp': VSTAMP, 'vfoil': VFOIL, 'sets': sets, 'cards': cards}
rawb = json.dumps(out, separators=(',', ':'), ensure_ascii=False).encode()
open(S_ + 'data/db.b64', 'w').write(base64.b64encode(gzip.compress(rawb, 9)).decode())
print(len(cards), 'cards', len(sets), 'sets', nv, 'printings', len(rawb), 'bytes raw', skipped, 'basic energies excluded', excluded, 'language exclusions applied')
