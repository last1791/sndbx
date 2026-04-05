import { execSync } from 'node:child_process';
import { mkdirSync, existsSync, appendFileSync } from 'node:fs';
import path from 'node:path';

const OUT_DIR = 'sndbx';
const OUT_FILE = 'ai-news.jsonl';
const LIMIT = 5;

function fetchTechSnifAi() {
  const cmd = `techsnif search "AI" --limit ${LIMIT} --json`;
  const raw = execSync(cmd, { encoding: 'utf8' });
  const res = JSON.parse(raw);

  if (Array.isArray(res)) return res;
  if (Array.isArray(res.data)) return res.data;
  if (Array.isArray(res.results)) return res.results;
  if (Array.isArray(res.stories)) return res.stories;
  if (res.data && Array.isArray(res.data.items)) return res.data.items;
  if (res.data && Array.isArray(res.data.results)) return res.data.results;
  if (res.data && Array.isArray(res.data.stories)) return res.data.stories;

  throw new Error(`Neznámá struktura odpovědi z TechSnif: ${JSON.stringify(res).slice(0, 500)}`);
}

async function fetchHackerNewsTop() {
  const idsRes = await fetch('https://hacker-news.firebaseio.com/v0/topstories.json');
  const ids = await idsRes.json();
  const topIds = ids.slice(0, LIMIT);

  const items = await Promise.all(
    topIds.map(async (id) => {
      const itemRes = await fetch(`https://hacker-news.firebaseio.com/v0/item/${id}.json`);
      return itemRes.json();
    })
  );

  return items.filter(Boolean);
}

function normalizeItem(item, sourceSystem, category) {
  return {
    id: item.id ? String(item.id) : crypto.randomUUID(),
    fetched_at: new Date().toISOString(),
    category,
    source_system: sourceSystem,
    title: item.title || item.headline || item.leadTitle || null,
    url: item.url || item.leadUrl || item.sourcePermalink || null,
    source: item.by || item.sourcePublisher || item.publisher || null,
    raw: item
  };
}

function toJsonLines(records) {
  return records.map(r => JSON.stringify(r)).join('\n') + '\n';
}

async function main() {
  if (!existsSync(OUT_DIR)) {
    mkdirSync(OUT_DIR, { recursive: true });
  }

  const techsnif = fetchTechSnifAi().map(item => normalizeItem(item, 'techsnif', 'ai'));
  const hn = (await fetchHackerNewsTop()).map(item => normalizeItem(item, 'hackernews', 'tech'));

  const outPath = path.join(OUT_DIR, OUT_FILE);
  appendFileSync(outPath, toJsonLines([...techsnif, ...hn]), 'utf8');

  console.log(`Zapsáno ${techsnif.length + hn.length} záznamů do ${outPath}`);
}

main();
