// ワイヤーフレーム統合後の動線を機械集計する（wireframe-integration 手順 6 の補助ツール）。
//
//   node check-links.mjs <統合後のルートディレクトリ> [--entry <入口の相対パス>] [--json]
//   例: node .claude\skills\wireframe-integration\scripts\check-links.mjs . ^
//         --entry .aidd\wireframe\_app-shell\pages\index.html
//
// 集計するのは 2 つだけ:
//   ① リンク切れ  — 内部リンクのうち、相対パスがファイルに解決しないもの
//   ② 到達性      — 起点（入口）から辿って到達できるページ数・feature 数
//
// **判定はしない**（exit code は常に 0 — 数えるだけ）。合否は Skill 手順側で下す
// （監査スクリプト〔exit code で判定する〕とは性質が違う）。
// 状態バリエーション（error / loading 等）はどこからもリンクされないのが正常のため、
// ページ単位の到達率は判定に使わない。
import { existsSync, readdirSync, readFileSync, statSync } from "node:fs";
import { dirname, join, relative, resolve, sep } from "node:path";

const SKIP_DIRS = new Set(["node_modules", ".git", "ds", "tokens", "assets", "img", "images"]);

// href から拾わないスキーム・アンカー
const EXTERNAL = /^(https?:|mailto:|tel:|javascript:|data:|#)/i;

function listHtml(dir) {
  const found = [];
  for (const name of readdirSync(dir)) {
    const p = join(dir, name);
    if (statSync(p).isDirectory()) {
      if (!SKIP_DIRS.has(name)) found.push(...listHtml(p));
      continue;
    }
    if (name.endsWith(".html")) found.push(p);
  }
  return found.sort();
}

function stripNonContent(html) {
  return html
    .replace(/<!--[\s\S]*?-->/g, "")
    .replace(/<script[\s\S]*?<\/script>/gi, "")
    .replace(/<style[\s\S]*?<\/style>/gi, "");
}

const HREF = /<a\b[^>]*\bhref\s*=\s*(?:"([^"]*)"|'([^']*)'|([^\s">]+))/gi;

function collectHrefs(html) {
  const out = [];
  for (const m of stripNonContent(html).matchAll(HREF)) {
    const raw = (m[1] ?? m[2] ?? m[3] ?? "").trim();
    if (raw) out.push(raw);
  }
  return out;
}

// href（クエリ・ハッシュを除いた相対パス）を実ファイルへ解決する。
// ディレクトリ指定・末尾スラッシュは index.html を試す。解決できなければ null。
function resolveHref(fromFile, href) {
  const bare = href.split("#")[0].split("?")[0];
  if (!bare) return null; // 同一ページ内アンカーのみ
  let decoded = bare;
  try {
    decoded = decodeURIComponent(bare);
  } catch {
    // 不正なパーセントエンコードはそのまま扱う
  }
  const target = resolve(dirname(fromFile), decoded.replace(/\//g, sep));
  if (existsSync(target)) {
    if (statSync(target).isDirectory()) {
      const idx = join(target, "index.html");
      return existsSync(idx) ? idx : null;
    }
    return target;
  }
  return null;
}

// .aidd/wireframe/<feature>/... のパスから feature 名を取り出す。
// ルートに .aidd/wireframe 自体を渡した場合は直下のディレクトリ名を feature とみなす。
function featureOf(relPath) {
  const parts = relPath.split(sep);
  const i = parts.indexOf("wireframe");
  if (i >= 0 && parts[i + 1]) return parts[i + 1];
  return parts.length > 1 ? parts[0] : null;
}

function check(rootArg, entryArg) {
  const root = resolve(rootArg);
  const pages = listHtml(root);
  const known = new Set(pages);

  const broken = [];
  const graph = new Map(); // page -> Set<page>
  let internalTotal = 0;

  for (const page of pages) {
    const html = readFileSync(page, "utf8");
    const next = new Set();
    for (const href of collectHrefs(html)) {
      if (EXTERNAL.test(href)) continue;
      internalTotal++;
      const target = resolveHref(page, href);
      if (!target) {
        broken.push({ from: relative(root, page), href });
        continue;
      }
      if (known.has(target)) next.add(target);
    }
    graph.set(page, next);
  }

  const features = new Map(); // feature -> pages[]
  for (const page of pages) {
    const f = featureOf(relative(root, page));
    if (!f) continue;
    if (!features.has(f)) features.set(f, []);
    features.get(f).push(page);
  }

  let reachability = null;
  if (entryArg) {
    const entry = resolve(root, entryArg.replace(/\//g, sep));
    if (!existsSync(entry)) {
      reachability = { error: `起点が見つからない: ${entryArg}` };
    } else {
      // 起点からの幅優先探索（到達 = そのページへリンクを辿って行ける）
      const seen = new Set([entry]);
      const queue = [entry];
      while (queue.length > 0) {
        const cur = queue.shift();
        for (const nxt of graph.get(cur) ?? []) {
          if (seen.has(nxt)) continue;
          seen.add(nxt);
          queue.push(nxt);
        }
      }
      const unreachedPages = pages.filter((p) => !seen.has(p)).map((p) => relative(root, p));
      const reachedFeatures = [];
      const unreachedFeatures = [];
      for (const [f, fp] of [...features.entries()].sort()) {
        (fp.some((p) => seen.has(p)) ? reachedFeatures : unreachedFeatures).push(f);
      }
      reachability = {
        entry: relative(root, entry),
        reachedPages: seen.size,
        unreachedPages,
        reachedFeatures,
        unreachedFeatures,
      };
    }
  }

  return {
    root,
    pages: pages.length,
    features: features.size,
    internalLinks: internalTotal,
    broken,
    reachability,
  };
}

function report(r) {
  console.log(`\n=== 動線チェック: ${r.root} （${r.pages} ページ / ${r.features} feature） ===`);

  console.log(`\n① リンク切れ: ${r.broken.length} 件（内部リンク ${r.internalLinks} 本中）`);
  if (r.broken.length === 0) {
    console.log("  リンク切れなし");
  }
  for (const b of r.broken) console.log(`  - ${b.from} → "${b.href}"`);

  if (!r.reachability) {
    console.log("\n② 到達性: --entry が未指定のためスキップ");
    return;
  }
  if (r.reachability.error) {
    console.log(`\n② 到達性: ${r.reachability.error}`);
    return;
  }
  const re = r.reachability;
  console.log(`\n② 到達性（起点: ${re.entry}）`);
  console.log(`  到達ページ: ${re.reachedPages} / ${r.pages}`);
  console.log(`  到達 feature: ${re.reachedFeatures.length} / ${r.features}`);
  if (re.unreachedFeatures.length > 0) {
    console.log(`  未到達 feature ${re.unreachedFeatures.length}: ${re.unreachedFeatures.join(" / ")}`);
  } else {
    console.log("  未到達 feature: なし");
  }
  if (re.unreachedPages.length > 0) {
    console.log(`  未到達ページ ${re.unreachedPages.length}:`);
    for (const p of re.unreachedPages) console.log(`    - ${p}`);
  }
}

const argv = process.argv.slice(2);
const asJson = argv.includes("--json");
const entryIdx = argv.indexOf("--entry");
const entryValueIdx = entryIdx >= 0 ? entryIdx + 1 : -1;
const entry = entryValueIdx >= 0 ? argv[entryValueIdx] : null;
const positional = argv.filter((a, i) => !a.startsWith("--") && i !== entryValueIdx);

if (positional.length !== 1) {
  console.error(
    "使い方: node check-links.mjs <ルートディレクトリ> [--entry <起点の相対パス>] [--json]",
  );
  process.exit(2);
}

const result = check(positional[0], entry);
if (asJson) {
  console.log(JSON.stringify(result, null, 2));
} else {
  report(result);
}
