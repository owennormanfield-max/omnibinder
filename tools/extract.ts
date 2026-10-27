// Walk the cards-database repo, import each card/set with bun, emit compact JSON.
import { readdirSync, statSync, writeFileSync } from 'fs'
import { join, basename } from 'path'

const ROOT = process.argv[2]
const OUT = process.argv[3]

function walk(dir: string, out: string[]) {
  for (const f of readdirSync(dir)) {
    const p = join(dir, f)
    if (statSync(p).isDirectory()) walk(p, out)
    else if (f.endsWith('.ts')) out.push(p)
  }
}

const files: string[] = []
for (const d of ['data', 'data-asia']) walk(join(ROOT, d), files)

const sets: Record<string, any> = {}
const cards: any[] = []
let bad = 0
for (const f of files) {
  let mod: any
  try { mod = (await import(f)).default } catch (e) { bad++; if (bad<3) console.error(f, String(e).slice(0,200)); continue }
  if (!mod || typeof mod !== 'object') continue
  if ('serie' in mod && 'cardCount' in mod) {
    // set
    const reg = f.includes('data-asia') ? 'asia' : 'intl'
    sets[reg+':'+mod.id] = {
      id: mod.id, name: mod.name, serie: mod.serie?.name, serieId: mod.serie?.id,
      count: mod.cardCount?.official ?? mod.cardCount?.total,
      date: mod.releaseDate, abbr: mod.abbreviations?.official,
      region: f.includes('data-asia') ? 'asia' : 'intl'
    }
  } else if ('set' in mod && 'category' in mod) {
    const num = basename(f, '.ts')
    cards.push({
      id: mod.set?.id + '-' + num, set: (f.includes('data-asia') ? 'asia' : 'intl')+':'+mod.set?.id, num,
      name: mod.name, cat: mod.category, rar: mod.rarity, hp: mod.hp, types: mod.types,
      stage: mod.stage, reg: mod.regulationMark, dex: mod.dexId, ill: mod.illustrator,
      trainerType: mod.trainerType, energyType: mod.energyType, suffix: mod.suffix,
      vars: Array.isArray(mod.variants) ? mod.variants.map((v: any) => ({t: v.type, st: v.subtype, sz: v.size, stamp: v.stamp, foil: v.foil, langs: v.languages, tp: v.thirdParty?.tcgplayer, cm: v.thirdParty?.cardmarket}))
        : (mod.variants ? Object.entries(mod.variants).filter(([,v])=>v).map(([k])=>({t: k})) : undefined),
      tp: mod.thirdParty?.tcgplayer, cm: mod.thirdParty?.cardmarket,
      region: f.includes('data-asia') ? 'asia' : 'intl'
    })
  }
}
console.log('sets', Object.keys(sets).length, 'cards', cards.length, 'bad', bad)
writeFileSync(OUT, JSON.stringify({ sets, cards }))
