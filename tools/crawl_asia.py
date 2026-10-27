#!/usr/bin/env python3
"""Crawl asia.pokemon-card.com for a region (tw/th/id/hk/sg) -> ext/asia_<region>.json
   {cardId: {set, num, img}} for cards in the sets listed in ext/asia_need_<lang>.json.
usage: crawl_asia.py REGION LANG [worker nworkers]"""
import json, re, sys, time, os, urllib.request
REG, LANG = sys.argv[1], sys.argv[2]
W = int(sys.argv[3]) if len(sys.argv) > 3 else 0; NW = int(sys.argv[4]) if len(sys.argv) > 4 else 1
UA = {'User-Agent': 'Mozilla/5.0 (Macintosh; Intel Mac OS X 14_0) AppleWebKit/537.36 Chrome/124 Safari/537.36 Omnibinder/1.0'}
EXT = '/tmp/claude-0/-home-claude/a8fddf89-7924-5379-a951-760823380930/scratchpad/ext'
BASE = f'https://asia.pokemon-card.com/{REG}'
def get(url, tries=3):
    for i in range(tries):
        try:
            with urllib.request.urlopen(urllib.request.Request(url, headers=UA), timeout=30) as r:
                return r.read().decode('utf-8', 'ignore')
        except Exception:
            time.sleep(1.5 * (i + 1))
    return None
need = json.load(open(os.path.join(EXT, f'asia_need_{LANG}.json')))
IDS = os.path.join(EXT, f'asia_ids_{REG}.json')
ids = json.load(open(IDS)) if os.path.exists(IDS) else {}
# Phase 1 (worker 0 only, or if missing): list card ids per needed set
if W == 0:
    for code in need:
        if code in ids: continue
        found = []; p = 1
        while True:
            t = get(f'{BASE}/card-search/list/?expansionCodes={code}&pageNo={p}')
            if not t: break
            got = re.findall(r'/card-search/detail/(\d+)/', t)
            got = [g for g in got if g not in found]
            if not got: break
            found += got
            m = re.search(r'pageNo=(\d+)', t)
            if f'pageNo={p+1}' not in t: break
            p += 1; time.sleep(0.2)
        ids[code] = found
        json.dump(ids, open(IDS, 'w'))
        print('set', code, len(found), flush=True)
        time.sleep(0.2)
else:
    while not os.path.exists(IDS) or len(json.load(open(IDS))) < len(need):
        time.sleep(10)
    ids = json.load(open(IDS))
# Phase 2: details
OUT = os.path.join(EXT, f'asia_{REG}_{W}.json')
det = json.load(open(OUT)) if os.path.exists(OUT) else {}
todo = sorted({cid for lst in ids.values() for cid in lst if cid not in det})
todo = [c for i, c in enumerate(todo) if i % NW == W]
print('details to fetch', len(todo), flush=True)
rxn = re.compile(r'collectorNumber">\s*([^<]*?)\s*<')
rxs = re.compile(r'expansionCodes=([A-Za-z0-9-]+)')
rxi = re.compile(r'(https://asia\.pokemon-card\.com/' + REG + r'/card-img/[^"]+\.png)')
n = 0
for cid in todo:
    t = get(f'{BASE}/card-search/detail/{cid}/')
    if not t: det[cid] = {'err': 1}; continue
    mn = rxn.search(t); ms = rxs.search(t); mi = rxi.search(t)
    det[cid] = {'num': (mn.group(1) if mn else '').strip(), 'set': ms.group(1) if ms else '', 'img': mi.group(1).replace('https://asia.pokemon-card.com/', '') if mi else ''}
    n += 1
    if n % 100 == 0:
        json.dump(det, open(OUT, 'w')); print('details', n, '/', len(todo), flush=True)
    time.sleep(0.2)
json.dump(det, open(OUT, 'w'))
print('done', REG, W, len(det), flush=True)
