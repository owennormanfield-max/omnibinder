#!/usr/bin/env python3
"""Crawl pokemoncard.co.kr: list every card via the load-more endpoint, then detail pages
-> ext/kr_cards.json {CardNum: {name, num, set, img}}.  usage: crawl_kr.py [worker nworkers]"""
import json, re, sys, time, os, urllib.request, urllib.parse
W = int(sys.argv[1]) if len(sys.argv) > 1 else 0; NW = int(sys.argv[2]) if len(sys.argv) > 2 else 1
EXT = '/tmp/claude-0/-home-claude/a8fddf89-7924-5379-a951-760823380930/scratchpad/ext'
UA = 'Mozilla/5.0 (Macintosh; Intel Mac OS X 14_0) AppleWebKit/537.36 Chrome/124 Safari/537.36 Omnibinder/1.0'
def post(limit, ctn, goods=''):
    data = urllib.parse.urlencode({'action': 'get_more_cards', 'limit': limit, 'GoodsName': goods, 'CardTypeNum': ctn, 'CardType': '', 'CardMonType': '', 'Weakness': '', 'Resistance': '', 'TechErg': '', 'ability_label1': '', 'hp': '0,999', 'retreat': '0,9', 'order': 'ASC', 'orderby': 'CardNum'}).encode()
    for i in range(3):
        try:
            req = urllib.request.Request('https://pokemoncard.co.kr/v2/ajax2_dev2', data=data, headers={'User-Agent': UA, 'X-Requested-With': 'XMLHttpRequest', 'Referer': 'https://pokemoncard.co.kr/cards'})
            with urllib.request.urlopen(req, timeout=30) as r: return json.loads(r.read().decode('utf-8', 'ignore'))
        except Exception: time.sleep(1.5 * (i + 1))
    return None
def get(url):
    for i in range(3):
        try:
            with urllib.request.urlopen(urllib.request.Request(url, headers={'User-Agent': UA}), timeout=30) as r: return r.read().decode('utf-8', 'ignore')
        except Exception: time.sleep(1.5 * (i + 1))
    return None
LIST = os.path.join(EXT, 'kr_list.json')
if W == 0 and not os.path.exists(LIST):
    lst = {}
    # eras hidden by default (BW, XY, 썬&문) need an explicit GoodsName; collect those names from the form
    html = get('https://pokemoncard.co.kr/cards') or ''
    goods = [''] + [g for g in re.findall(r'<option value="([^"]+)"', html) if re.search(r'BW|XY|썬&문', g) and '전체' not in g]
    for g in goods:
        for ctn in (1, 2, 3):
            limit = 0; seen = 0
            while True:
                j = post(limit, ctn, g)
                if not j or not j.get('count'): break
                res = j['result']; res = list(res.values()) if isinstance(res, dict) else res
                for v in res: lst[v['CardNum']] = {'img': v.get('feature_image', '').split('?')[0]}
                limit = j.get('limit', limit + 1); seen += len(res)
                time.sleep(0.2)
            print('goods', g[:20] or '(default)', 'type', ctn, 'cards', seen, 'total', len(lst), flush=True)
    json.dump(lst, open(LIST, 'w'), ensure_ascii=False)
    print('listing done', len(lst), flush=True)
else:
    while not os.path.exists(LIST): time.sleep(10)
lst = json.load(open(LIST))
OUT = os.path.join(EXT, f'kr_cards_{W}.json')
det = json.load(open(OUT)) if os.path.exists(OUT) else {}
todo = [c for i, c in enumerate(sorted(k for k in lst if k not in det)) if i % NW == W]
print('details to fetch', len(todo), flush=True)
rxn = re.compile(r'class="p_num">\s*([^<]*?)\s*<'); rxs = re.compile(r'images/symbol/([A-Za-z0-9-]+)\.png'); rxt = re.compile(r'card-hp title">\s*([^<]*?)\s*<'); rxi = re.compile(r'wmimages/([^"?]+)')
n = 0
for cid in todo:
    t = get(f'https://pokemoncard.co.kr/cards/detail/{cid}')
    if not t: det[cid] = {'err': 1}; continue
    syms = [s for s in rxs.findall(t) if not re.fullmatch(r'[A-J]|type\d+', s)]
    mn = rxn.search(t); mt = rxt.search(t); mi = rxi.search(t)
    det[cid] = {'num': (mn.group(1) if mn else '').strip(), 'set': syms[0] if syms else '', 'name': (mt.group(1) if mt else '').strip(), 'img': mi.group(1) if mi else lst[cid]['img']}
    n += 1
    if n % 100 == 0: json.dump(det, open(OUT, 'w'), ensure_ascii=False); print('details', n, '/', len(todo), flush=True)
    time.sleep(0.2)
json.dump(det, open(OUT, 'w'), ensure_ascii=False)
print('done', W, len(det), flush=True)
