// Emit a language-independent fingerprint per card: fp.json {cardKey: {...}}
import { readdirSync, statSync, writeFileSync } from 'fs'
import { join, basename } from 'path'
const ROOT = process.argv[2], OUT = process.argv[3]
function walk(dir: string, out: string[]) { for (const f of readdirSync(dir)) { const p = join(dir, f); if (statSync(p).isDirectory()) walk(p, out); else if (f.endsWith('.ts')) out.push(p) } }
const files: string[] = []; for (const d of ['data', 'data-asia']) walk(join(ROOT, d), files)
const out: Record<string, any> = {}
for (const f of files) {
  let m: any; try { m = (await import(f)).default } catch { continue }
  if (!m || typeof m !== 'object' || !('set' in m && 'category' in m)) continue
  const key = (f.includes('data-asia') ? 'asia' : 'intl') + ':' + m.set?.id + '-' + basename(f, '.ts')
  out[key] = {
    cat: m.category, tt: m.trainerType, et: m.energyType, ill: m.illustrator, hp: m.hp, stage: m.stage, dex: m.dexId, types: m.types,
    ab: (m.abilities || []).length,
    at: (m.attacks || []).map((a: any) => [(a.cost || []).slice().sort().join(''), String(a.damage ?? '')]),
    wk: (m.weaknesses || []).map((w: any) => w.type + (w.value || '')).sort(), rs: (m.resistances || []).map((w: any) => w.type + (w.value || '')).sort(),
    rt: m.retreat, date: m.set?.releaseDate, en: m.name?.en, ja: m.name?.ja, enEffect: m.effect?.en, item: m.item?.name?.en
  }
}
console.log(Object.keys(out).length); writeFileSync(OUT, JSON.stringify(out))
