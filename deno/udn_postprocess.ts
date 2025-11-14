import { readJSON, writeJSON } from "https://deno.land/x/flat@0.0.15/mod.ts";

const [filename] = Deno.args;
if (!filename) {
  console.error("Flat Data postprocess script requires a filename argument");
  Deno.exit(1);
}

const ensureDir = async (path: string) => {
  try {
    await Deno.mkdir(path, { recursive: true });
  } catch (error) {
    if (!(error instanceof Deno.errors.AlreadyExists)) {
      throw error;
    }
  }
};

const normalizeArticle = (article: Record<string, unknown>) => {
  const title = typeof article.title === "string" ? article.title.trim() : "";
  const link = typeof article.titleLink === "string" ? article.titleLink : "";
  const summary =
    typeof article.paragraph === "string" ? article.paragraph.trim() : "";
  const image =
    typeof article.url === "string" && article.url.length > 0
      ? article.url
      : undefined;

  const rawTime = article.time;
  let timeValue: unknown = rawTime;

  if (rawTime && typeof rawTime === "object") {
    const timeCandidate = (rawTime as Record<string, unknown>).date ??
      (rawTime as Record<string, unknown>).time ??
      (rawTime as Record<string, unknown>).datetime ??
      "";
    timeValue = timeCandidate;
  }

  const time = typeof timeValue === "string" ? timeValue.trim() : timeValue;

  const normalized: Record<string, unknown> = {
    title,
    link: new URL(link, "https://udn.com").toString(),
  };

  if (summary) {
    normalized.summary = summary;
  }
  if (time) {
    normalized.time = time;
  }
  if (image) {
    normalized.image = image;
  }

  return normalized;
};

const payload = await readJSON(filename) as Record<string, unknown>;
const lists = Array.isArray(payload.lists) ? payload.lists : [];

const articles = lists
  .filter((item): item is Record<string, unknown> =>
    item !== null && typeof item === "object"
  )
  .map(normalizeArticle)
  .filter((item) => item.title && item.link);

await ensureDir("data");

const outputPath = "data/udn_breaking.json";
await writeJSON(outputPath, articles, { spaces: 2 });

console.log(
  `Normalized ${articles.length} breaking news items to ${outputPath}`,
);
