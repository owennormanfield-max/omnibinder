#!/usr/bin/env python3
"""Attach official asia.pokemon-card.com scans (per language) and pokemoncard.co.kr scans + Korean names.
Stores card['ox'] = {lang: image path suffix} ; card['name']['ko'] added when the Korean site has the card."""
import json, glob, collections, os
S_ = '/tmp/claude-0/-home-claude/a8fddf89-7924-5379-a951-760823380930/scratchpad/'
d = json.load(open(S_ + 'data/all.json')); C = d['cards']; S = d['sets']
def nk(x): x = str(x).strip().upper().split('/')[0].strip(); return x.lstrip('0') or x
byset = collections.defaultdict(list)
for c in C: byset[S[c['set']]['id'].upper()].append(c)
report = {}
# ---- asia regions ----
for reg, lang in [('tw', 'zh-tw'), ('th', 'th'), ('id', 'id')]:
    det = {}
    for f in glob.glob(S_ + f'ext/asia_{reg}_[0-9].json'): det.update(json.load(open(f)))
    idx = {}
    for v in det.values():
        if v.get('set') and v.get('num') and v.get('img'): idx.setdefault((v['set'].upper(), nk(v['num'])), v['img'])
    hit = 0; tried = 0
    for c in C:
        if lang not in (c.get('name') or {}) or lang in (c.get('scan') or []): continue
        tried += 1
        p = idx.get((S[c['set']]['id'].upper(), nk(c['num'])))
        if p: c.setdefault('ox', {})[lang] = p; hit += 1
    report[lang] = (tried, hit, len(det))
# ---- korean ----
det = {}
for f in glob.glob(S_ + 'ext/kr_cards_[0-9].json'): det.update(json.load(open(f)))
idx = {}
for v in det.values():
    if v.get('set') and v.get('num'): idx.setdefault((v['set'].upper(), nk(v['num'])), v)
hit = 0; named = 0
for c in C:
    s = S[c['set']]
    if s['region'] != 'asia': continue
    v = idx.get((s['id'].upper(), nk(c['num'])))
    if not v: continue
    if 'ko' not in c['name'] and v.get('name'): c['name']['ko'] = v['name']; named += 1
    if 'ko' not in (c.get('scan') or []) and v.get('img'): c.setdefault('ox', {})['ko'] = v['img']; hit += 1
report['ko'] = ('n/a', hit, len(det), 'names added', named)
json.dump(d, open(S_ + 'data/all.json', 'w'))
for k, v in report.items(): print(k, v)
