// scripts/fetch-ai-news.mjs
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

  if (!res.ok) {
    throw new Error('TechSnif CLI vrátilo ok=false');
  }

  return res.data;
}

function toJsonLines(stories) {
  const now = new Date().toISOString();

  return stories
    .map(story => JSON.stringify({
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
