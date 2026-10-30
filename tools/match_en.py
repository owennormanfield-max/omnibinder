import json,collections,re
S_='/tmp/claude-0/-home-claude/a8fddf89-7924-5379-a951-760823380930/scratchpad/'
fp=json.load(open(S_+'data/fp.json'))
def nill(x): return re.sub(r'[^a-z]','',(x or '').lower())
def yr(v):
    d=v.get('date') or ''
    if isinstance(d,dict): d=min(d.values()) if d else ''
    return int(d[:4]) if d[:4].isdigit() else 0
def nd(x): return re.sub(r'\s','',str(x)).replace('＋','+').replace('×','x').replace('−','-').replace('－','-')
def pk(v): return ('P',v.get('hp'),tuple(v.get('types') or []),v.get('ab'),tuple((a[0],nd(a[1])) for a in v.get('at') or []))
en=collections.defaultdict(list); enL=collections.defaultdict(list); enT=collections.defaultdict(list)
def pl(v): return ('L',v.get('hp'),tuple(v.get('types') or []),tuple(a[0] for a in v.get('at') or []))
for k,v in fp.items():
    if not k.startswith('intl:') or not v.get('en'): continue
    if v['cat']=='Pokemon': en[pk(v)].append((nill(v.get('ill')),yr(v))); enL[pl(v)].append((nill(v.get('ill')),tuple(nd(a[1]) for a in v.get('at') or []),yr(v)))
    else: enT[(v['cat'],v.get('tt') or v.get('et'),nill(v.get('ill')))].append(yr(v))
stat=collections.Counter();noen=[]
for k,v in fp.items():
    if not k.startswith('asia:') or not v.get('ja'): continue
    y=yr(v)
    if v['cat']=='Pokemon':
        cands=en.get(pk(v),[])
        ok=any((not y or not y2 or abs(y2-y)<=3) and (nill(v.get('ill'))==il or not v.get('ill') or not il) for il,y2 in cands)
        if not ok:
            dm=tuple(nd(a[1]) for a in v.get('at') or []); il=nill(v.get('ill'))
            ok=any((not y or not y2 or abs(y2-y)<=4) and ((il and il==il2) or dm==dm2) for il2,dm2,y2 in enL.get(pl(v),[])) and stat.update(['loose']) is None
        stat['P',ok]+=1
    else:
        if not v.get('ill'): stat['T',None]+=1; continue
        cands=enT.get((v['cat'],v.get('tt') or v.get('et'),nill(v.get('ill'))),[])
        ok=any((not y or not y2 or -1<=y2-y<=3) for y2 in cands)
        stat['T',ok]+=1
    if not ok and v['cat']=='Pokemon': noen.append(k)
print(stat); print(len(noen),'Japanese cards with no English match')
print(collections.Counter(k.split('-')[0] for k in noen).most_common(30))
json.dump(noen,open(S_+'data/noen.json','w'))
