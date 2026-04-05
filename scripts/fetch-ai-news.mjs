import { execSync } from 'node:child_process';
import { mkdirSync, existsSync, appendFileSync } from 'node:fs';
import path from 'node:path';

const OUT_DIR = 'sndbx';
const OUT_FILE = 'ai-news.jsonl';
const QUERY = 'AI';
const LIMIT = 5;

function fetchAiNews() {
  const cmd = `techsnif search "${QUERY}" --limit ${LIMIT} --json`;
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

function toJsonLines(stories) {
  const now = new Date().toISOString();

  return stories
    .map((story, index) => JSON.stringify({
      id: `${now}_${index + 1}`,
      fetched_at: now,
      category: 'ai',
      source_system: 'techsnif',
      raw: story
    }))
    .join('\n') + '\n';
}

function main() {
  if (!existsSync(OUT_DIR)) {
    mkdirSync(OUT_DIR, { recursive: true });
  }

  const stories = fetchAiNews();
  const block = toJsonLines(stories);
  const outPath = path.join(OUT_DIR, OUT_FILE);

  appendFileSync(outPath, block, 'utf8');
  console.log(`Zapsáno ${stories.length} záznamů do ${outPath}`);
}

main();
