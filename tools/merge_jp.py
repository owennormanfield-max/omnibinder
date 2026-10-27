#!/usr/bin/env python3
"""Attach official pokemon-card.com image paths to Japanese cards that TCGdex has no scan for."""
import json, re, collections
S_='/tmp/claude-0/-home-claude/a8fddf89-7924-5379-a951-760823380930/scratchpad/'
lst=json.load(open(S_+'ext/jp_list.json'))['cards']
det=json.load(open(S_+'ext/jp_details.json'))
d=json.load(open(S_+'data/all.json'));C=d['cards'];S=d['sets']
# official index: (setcode, num) -> image path ; also by (setcode, name) for promos without numbers
byn={};byname=collections.defaultdict(list)
def nk(x): x=str(x).strip().upper(); return x.lstrip('0') or x
for cid,info in det.items():
    if 'set' not in info: continue
    path=lst.get(cid,{}).get('path','')
    if not path or 'noimage' in path: continue
    byn.setdefault((info['set'].upper(),nk(info['num'])),path)
    byname[(info['set'].upper(),lst[cid]['name'])].append(path)
# alias table for set codes that differ between TCGdex and the official site
ALIAS={}
hit=0;miss=collections.Counter();tried=0
for c in C:
    if 'ja' not in (c.get('name') or {}) or 'ja' in (c.get('scan') or []) or c.get('img') or c.get('jp'): continue
    s=S[c['set']];code=s['id'].upper();tried+=1
    key=(ALIAS.get(code,code),nk(c['num']))
    p=byn.get(key)
    if not p:
        cands=byname.get((ALIAS.get(code,code),c['name']['ja']),[])
        if len(cands)==1:p=cands[0]
    if p:
        c['jp']=p.replace('/assets/images/card_images/large/','');hit+=1
    else: miss[s['id']]+=1
print('japanese cards lacking a TCGdex scan:',tried,'matched to official scans:',hit)
print('still missing by set:',miss.most_common(25))
json.dump(d,open(S_+'data/all.json','w'))
