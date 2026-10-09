// mockup 一式の動線を機械検査する（mockup-authoring 手順の完了条件。ゲート側でも同じコマンドで再実行できる）。
//
//   node check-links.mjs <検査対象のルート> [--entry <入口の相対パス>] [--json]
//   例: node <配布ワークスペース>\.claude\skills\mockup-authoring\scripts\check-links.mjs .aidd\screen-design ^
//         --entry _app-shell\pages\s-01-default.html
//
//   <検査対象のルート> … .aidd/screen-design（feature の mockup を生成・再生成するたびに全体で回す）
//
// 検査するのは 3 つ。**Tier A の 1 つだけが fail（exit 1）で、Tier B は件数を報告するだけ**:
//   A-3 リンク切れ    — 内部の参照が実ファイルに解決すること。**遷移（<a href>）と資源（<img src> /
//                       <link href>）を分けて扱う**:
//                       ・遷移は解決しないものを 2 つに分ける
//                         **pending** = 遷移先 feature の pages/ ディレクトリがまだ無い（= 所有 feature が未生成。
//                           許容。相手が生成された時点で消える。manifest の notes[] に記録する）
//                         **broken**  = ディレクトリは在るがファイルが無い（fail → 画面設計書か画面マップを
//                           直して再生成する）
//                       ・**資源は pending にしない。解決しなければ必ず broken**。
//                         「相手 feature が未生成」という増分生成の事情は資源に無く、置き場ごと無い状態を
//                         pending に落とすと**最も壊れた状態が許容側に回る**ため。
//                         data: URI と外部 URL は対象外（EXTERNAL）
//   B-2 到達性        — 入口から生成済みの全 feature に到達できるか。**件数報告にとどめる**。
//                       状態バリエーション（空・エラー等）はどこからもリンクされないのが正常なので、
//                       **ページ単位の到達率は判定に使わない**。資源は遷移ではないので到達性に数えない
//
// 検査しないもの:
//   - リンクの意味（画面マップ §3 に在る遷移かどうか。それは画面設計書・manifest との突合で人が見る）
//   - presented/<日付>/（凍結した提示版。相手 feature を後から生成しても直せないため対象外）
//   - <img srcset> / <source> / CSS の url()（mockup は素の <img> と <link> だけを使う規約のため。
//     styleguide.css の画像は data: URI で埋め込む — styleguide-authoring の生成規約 8）
//
// **exit code で合否を出す**（broken 0 件 = 0 / broken あり = 1 / 使い方の誤り = 2）。
// 流用元（ワイヤーフレーム工程 wireframe-integration 同梱の check-links.mjs）は
// 「数えるだけ・常に exit 0」で合否を Skill 手順側に委ねていたが、本工程は exit 0 を完了条件にするため
// **判定（exit code）と pending / broken の区別**を足し、feature 名を取り出すパス解釈を
// wireframe → screen-design に差し替えてある。
//
// 既知の限界: 遷移先 feature 名の**誤記**は「まだ無い feature」と区別できず pending になる。
// 相手 feature 名を報告するので、manifest の cross_feature_links（出どころ = 画面マップ §3）と突き合わせること。
import { existsSync, readdirSync, readFileSync, statSync } from "node:fs";
import { dirname, join, relative, resolve, sep } from "node:path";

const SKIP_DIRS = new Set(["node_modules", ".git", "ds", "tokens", "assets", "img", "images", "presented"]);
const STAGE_DIR = "screen-design";

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
const IMG = /<img\b[^>]*\bsrc\s*=\s*(?:"([^"]*)"|'([^']*)'|([^\s">]+))/gi;
const LINK = /<link\b[^>]*\bhref\s*=\s*(?:"([^"]*)"|'([^']*)'|([^\s">]+))/gi;

// 資源の種別（報告と JSON の kind。遷移は "link"）
const RESOURCES = [
  ["img", IMG],
  ["stylesheet", LINK],
];

// 引数の html は stripNonContent を通したもの（呼び出し側で 1 回だけ通す）
function collectRefs(html, re) {
  const out = [];
  for (const m of html.matchAll(re)) {
    const raw = (m[1] ?? m[2] ?? m[3] ?? "").trim();
    if (raw) out.push(raw);
  }
  return out;
}

// href（クエリ・ハッシュを除いた相対パス）を実ファイルへ解決する。
// ディレクトリ指定・末尾スラッシュは index.html を試す。
// 解決できない場合は、**置き場が在るか**で pending / broken を分ける:
//   遷移先の置き場（= 相手 feature の pages/）自体が無い → pending（相手が未生成）
//   置き場は在るがファイルが無い                        → broken（誤ったリンク）
function resolveHref(fromFile, href) {
  const bare = href.split("#")[0].split("?")[0];
  if (!bare) return { status: "anchor" }; // 同一ページ内アンカーのみ
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
      if (existsSync(idx)) return { status: "resolved", target: idx };
      return { status: "broken", target: idx };
    }
    return { status: "resolved", target };
  }
  return { status: existsSync(dirname(target)) ? "broken" : "pending", target };
}

// 資源（画像・スタイルシート）の解決。**pending にしない**（→ 冒頭の A-3）。
// 「相手 feature が未生成」という事情は資源に無いため、置き場ごと無い状態も broken として扱う。
function resolveResource(fromFile, ref) {
  const r = resolveHref(fromFile, ref);
  return r.status === "pending" ? { status: "broken", target: r.target } : r;
}

// .aidd/screen-design/<feature>/pages/… のパスから feature 名を取り出す。
// ルートに .aidd/screen-design 自体を渡した場合は直下のディレクトリ名を feature とみなす。
function featureOf(relPath) {
  const parts = relPath.split(sep);
  if (parts[0] === "..") return null; // ルートの外
  const i = parts.indexOf(STAGE_DIR);
  if (i >= 0 && parts[i + 1]) return parts[i + 1];
  return parts.length > 1 ? parts[0] : null;
}

function check(rootArg, entryArg) {
  const root = resolve(rootArg);
  if (!existsSync(root) || !statSync(root).isDirectory()) {
    fail(`検査対象のルートが見つからない: ${rootArg}（.aidd/screen-design を渡す）`);
  }
  const pages = listHtml(root);
  const known = new Set(pages);

  const broken = [];
  const pending = [];
  const graph = new Map(); // page -> Set<page>
  let internalTotal = 0; // <a href> の内部リンク
  let resourceTotal = 0; // <img src> / <link href> の内部参照

  for (const page of pages) {
    const doc = stripNonContent(readFileSync(page, "utf8"));
    const from = relative(root, page).split(sep).join("/");

    // 遷移（<a href>）— pending / broken に分ける。到達性のグラフに積むのはこれだけ
    const next = new Set();
    for (const href of collectRefs(doc, HREF)) {
      if (EXTERNAL.test(href)) continue;
      internalTotal++;
      const r = resolveHref(page, href);
      if (r.status === "anchor") continue;
      if (r.status === "resolved") {
        if (known.has(r.target)) next.add(r.target);
        continue;
      }
      const entry = { from, href, target: featureOf(relative(root, r.target)), kind: "link" };
      (r.status === "pending" ? pending : broken).push(entry);
    }
    graph.set(page, next);

    // 資源（<img src> / <link href>）— pending にせず、解決しなければ broken
    for (const [kind, re] of RESOURCES) {
      for (const ref of collectRefs(doc, re)) {
        if (EXTERNAL.test(ref)) continue;
        resourceTotal++;
        const r = resolveResource(page, ref);
        if (r.status === "resolved" || r.status === "anchor") continue;
        broken.push({ from, href: ref, target: featureOf(relative(root, r.target)), kind });
      }
    }
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
      fail(`起点が見つからない: ${entryArg}（入口は画面マップ §4 の入口ページを渡す）`);
    }
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
    const unreachedPages = pages
      .filter((p) => !seen.has(p))
      .map((p) => relative(root, p).split(sep).join("/"));
    const reachedFeatures = [];
    const unreachedFeatures = [];
    for (const [f, fp] of [...features.entries()].sort()) {
      (fp.some((p) => seen.has(p)) ? reachedFeatures : unreachedFeatures).push(f);
    }
    reachability = {
      entry: relative(root, entry).split(sep).join("/"),
      reachedPages: seen.size,
      unreachedPages,
      reachedFeatures,
      unreachedFeatures,
    };
  }

  const pendingTargets = [...new Set(pending.map((p) => p.target).filter(Boolean))].sort();

  return {
    root: root.split(sep).join("/"),
    pages: pages.length,
    features: features.size,
    internalLinks: internalTotal,
    internalResources: resourceTotal,
    broken,
    pending,
    pendingTargets,
    reachability,
    violations: broken.length, // Tier A（fail の対象）
    notices: pending.length, // Tier B / 許容（報告のみ）
    ok: broken.length === 0,
  };
}

function report(r) {
  console.log(`\n=== 動線検査: ${r.root} （${r.pages} ページ / ${r.features} feature） ===`);

  console.log(
    `\n[Tier A] ① リンク切れ（broken）: ${r.broken.length} 件` +
      `（遷移 ${r.internalLinks} 本 / 資源 ${r.internalResources} 本中）`,
  );
  if (r.broken.length === 0) {
    console.log("  リンク切れなし");
  }
  const WHY = { link: "置き場は在るがファイルが無い", img: "画像が無い", stylesheet: "スタイルシートが無い" };
  for (const b of r.broken) {
    console.log(`  - [${b.kind}] ${b.from} → "${b.href}"（${WHY[b.kind] ?? "解決しない"}）`);
  }
  if (r.broken.some((b) => b.kind !== "link")) {
    console.log(
      "  → 資源は pending にしない（相手 feature の未生成という事情が無いため）。参照先を直すか、",
    );
    console.log(
      "    装飾画像は styleguide.css の data: URI に寄せる（styleguide-authoring の生成規約 8）",
    );
  }

  console.log(`\n[許容] ② 未生成の遷移先（pending）: ${r.pending.length} 件`);
  if (r.pending.length === 0) {
    console.log("  pending なし");
  }
  for (const p of r.pending) {
    console.log(`  - ${p.from} → "${p.href}"（所有 feature ${p.target ?? "不明"} が未生成）`);
  }
  if (r.pending.length > 0) {
    console.log(`  → manifest の notes[] と checks.links.pending に記録する（相手: ${r.pendingTargets.join(" / ")}）`);
    console.log("  → feature 名の誤記も pending になる。画面マップ §3 の遷移と突き合わせること");
  }

  if (!r.reachability) {
    console.log("\n[Tier B] ③ 到達性: --entry が未指定のためスキップ");
  } else {
    const re = r.reachability;
    console.log(`\n[Tier B] ③ 到達性（起点: ${re.entry}）— 報告のみ・fail にしない`);
    console.log(`  到達ページ: ${re.reachedPages} / ${r.pages}（状態バリエーションは未到達が正常）`);
    console.log(`  到達 feature: ${re.reachedFeatures.length} / ${r.features}`);
    if (re.unreachedFeatures.length > 0) {
      console.log(`  未到達 feature ${re.unreachedFeatures.length}: ${re.unreachedFeatures.join(" / ")}`);
      console.log("  → ナビ項目が画面マップ §4 と一致しているかを確かめる");
    } else {
      console.log("  未到達 feature: なし");
    }
  }

  console.log(`\nTier A の違反: ${r.violations} 件 / pending: ${r.notices} 件`);
  console.log(
    r.ok
      ? "OK: リンク切れなし（pending は相手 feature の生成で消える）"
      : "NG: 画面設計書か画面マップを直して再生成する（ページを手で直さない）",
  );
}

function fail(message) {
  console.error(`エラー: ${message}`);
  process.exit(2);
}

const argv = process.argv.slice(2);
const asJson = argv.includes("--json");
const entryIdx = argv.indexOf("--entry");
const entryValueIdx = entryIdx >= 0 ? entryIdx + 1 : -1;
const entry = entryValueIdx >= 0 ? argv[entryValueIdx] : null;
const positional = argv.filter((a, i) => !a.startsWith("--") && i !== entryValueIdx);

if (positional.length !== 1) {
  console.error("使い方: node check-links.mjs <検査対象のルート> [--entry <起点の相対パス>] [--json]");
  process.exit(2);
}

const result = check(positional[0], entry);
if (asJson) {
  console.log(JSON.stringify(result, null, 2));
} else {
  report(result);
}
process.exit(result.ok ? 0 : 1);
