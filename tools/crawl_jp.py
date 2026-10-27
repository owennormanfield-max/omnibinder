#!/usr/bin/env python3
"""Crawl the official Japanese Pokémon card database (pokemon-card.com).
Phase 1: listing pages -> ext/jp_list.json  [{cardID, path, name}]
Phase 2: detail pages for cards in sets Omnibinder lacks scans for -> ext/jp_details.json {cardID: {set, num, total}}
Polite: ~4 req/s, retries, resumable."""
import json, re, sys, time, os, urllib.request, urllib.parse
UA = {'User-Agent': 'Mozilla/5.0 (Macintosh; Intel Mac OS X 14_0) AppleWebKit/537.36 Chrome/124 Safari/537.36 Omnibinder/1.0 (+https://owennormanfield-max.github.io/omnibinder/)'}
EXT = '/tmp/claude-0/-home-claude/a8fddf89-7924-5379-a951-760823380930/scratchpad/ext'
def get(url, tries=3):
    for i in range(tries):
        try:
            req = urllib.request.Request(url, headers=UA)
            with urllib.request.urlopen(req, timeout=30) as r:
                return r.read().decode('utf-8', 'ignore')
        except Exception as e:
            time.sleep(1.5 * (i + 1))
    return None

LIST = os.path.join(EXT, 'jp_list.json')
lst = json.load(open(LIST)) if os.path.exists(LIST) else {'pages': {}, 'cards': {}}
base = 'https://www.pokemon-card.com/card-search/resultAPI.php?keyword=&se_ta=&regulation_sidebar_form=all&pg=&illust=&sm_and_keyword=true&page='
first = get(base + '1')
maxp = json.loads(first)['maxPage']
print('pages', maxp, flush=True)
for p in range(1, maxp + 1):
    if str(p) in lst['pages']:
        continue
    t = get(base + str(p))
    if not t:
        print('fail page', p, flush=True); continue
    try:
        j = json.loads(t)
    except Exception:
        print('bad json', p, flush=True); continue
    for c in j.get('cardList', []):
        lst['cards'][c['cardID']] = {'path': c['cardThumbFile'], 'name': c['cardNameAltText']}
    lst['pages'][str(p)] = len(j.get('cardList', []))
    if p % 25 == 0:
        json.dump(lst, open(LIST, 'w'), ensure_ascii=False)
        print('page', p, 'cards', len(lst['cards']), flush=True)
    time.sleep(0.25)
json.dump(lst, open(LIST, 'w'), ensure_ascii=False)
print('listing done', len(lst['cards']), flush=True)

# Phase 2: which set folders do we need?
need = set(json.load(open(os.path.join(EXT, 'jp_need_sets.json'))))
DET = os.path.join(EXT, 'jp_details.json')
W = int(sys.argv[1]) if len(sys.argv) > 1 else 0; NW = int(sys.argv[2]) if len(sys.argv) > 2 else 1
DET = os.path.join(EXT, f'jp_details_{W}.json') if NW > 1 else DET
det = json.load(open(DET)) if os.path.exists(DET) else {}
det = {k: v for k, v in det.items() if 'err' not in v}
todo = [cid for cid, c in lst['cards'].items() if cid not in det and len(c['path'].split('/'))>5 and c['path'].split('/')[5] in need]
todo = [cid for i, cid in enumerate(sorted(todo)) if i % NW == W]
print('details to fetch', len(todo), flush=True)
rx = re.compile(r'regulation_logo_1/([^"]+)\.gif"[^>]*>\s*((?:&nbsp;|[^<])*?)\s*<', re.S)
n = 0
for cid in todo:
    t = get(f'https://www.pokemon-card.com/card-search/details.php/card/{cid}/regu/all')
    if not t:
        det[cid] = {'err': 1}; continue
    m = rx.search(t)
    if m:
        code = m.group(1); txt = m.group(2).replace('&nbsp;', ' ').strip()
        mm = re.match(r'(\S+)\s*/\s*(\S+)', txt)
        det[cid] = {'set': code, 'num': mm.group(1) if mm else txt, 'total': mm.group(2) if mm else ''}
    else:
        det[cid] = {'err': 2}
    n += 1
    if n % 100 == 0:
        json.dump(det, open(DET, 'w'), ensure_ascii=False)
        print('details', n, '/', len(todo), flush=True)
    time.sleep(0.25)
json.dump(det, open(DET, 'w'), ensure_ascii=False)
print('details done', len(det), flush=True)
