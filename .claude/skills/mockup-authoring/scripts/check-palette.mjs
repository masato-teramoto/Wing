// mockup のページが「見た目の正 = STYLEGUIDE.md / styleguide.css の 1 枚」だけを見ているかを検査する
// （mockup-authoring 手順の完了条件。ゲート側でも同じコマンドで再実行できる）。
//
//   node check-palette.mjs <案件ルート> <検査対象> [--json]
//   例: node <配布ワークスペース>\.claude\skills\mockup-authoring\scripts\check-palette.mjs ^
//         . .aidd\screen-design
//       node check-palette.mjs . .aidd\screen-design\loan-request-review\pages
//
//   <案件ルート> … 出力ルート。**直下の styleguide.css が正**（案件に 1 枚）
//   <検査対象>   … feature の pages/ 1 つ、または配下を再帰探索するルート
//                  （.aidd/screen-design を渡すと全 feature 一括検査 = feature 間の同一性も見る）
//
// 検査するのは 3 つ。**Tier A の 2 つだけが fail（exit 1）で、Tier B は件数を報告するだけ**:
//   A-1 生値          — pages/*.html に色（hex / rgb / rgba / hsl / hsla）と px の生値が無いこと。
//                       30 ページ中の 1 行の color: #333 は目視で見えず、しかも STYLEGUIDE.md の版を
//                       上げても生値のページは追従しない（「見た目の正は 1 枚」が静かに崩れる）
//   A-2 複製の同一性  — 各 pages/tokens/styleguide.css が案件直下の正と同一（= feature 間でも同一）。
//                       複製を置く理由は presented/<日付>/ が単体で開けること 1 点で、ここがずれると
//                       「顧客が見た版」の証跡が黙って無効になる
//   B-1 部品クラス    — HTML の class に、styleguide.css が定義していないクラスが無いか。
//                       **件数報告にとどめる**（雛形由来のクラス等で過検出して正常系が fail するのを避ける）。
//                       突合対象は styleguide.css が定義するクラスの集合に限る
//
// 検査しないもの:
//   - styleguide.css 自身の中身（生値が在るのが正しい。トークンと部品クラスの正）
//   - styleguide.css の読み込み切れ・崩れ・見た目（人の目視が持つ）
//   - HTML コメントの中身（描画されないため A-1 の対象外。行番号は保つ）
//   - presented/<日付>/（凍結した提示版。版を上げた後は正と差が出るのが正常）
//
// **exit code で合否を出す**（Tier A 違反 0 件 = 0 / 違反あり = 1 / 使い方の誤り = 2）。
// 同じ工程の check-links.mjs と同じ慣行。流用元の check-tokens.mjs（wireframe-authoring 同梱）とは
// 検査対象が違う（あちらは DS のトークン JSON との突合で、本工程は DS を持たない）。
import { existsSync, readdirSync, readFileSync, statSync } from "node:fs";
import { dirname, join, relative, resolve, sep } from "node:path";

const SKIP_DIRS = new Set(["node_modules", ".git", "presented", "assets", "img", "images"]);
const STYLEGUIDE_CSS = "styleguide.css";
const TOKENS_DIR = "tokens";

// --- 収集 -----------------------------------------------------------------

function walk(dir, hit, found) {
  for (const name of readdirSync(dir)) {
    const p = join(dir, name);
    if (statSync(p).isDirectory()) {
      if (!SKIP_DIRS.has(name)) walk(p, hit, found);
      continue;
    }
    if (hit(name, p)) found.push(p);
  }
  return found;
}

function collectPages(targetArg) {
  const target = resolve(targetArg);
  if (!existsSync(target)) fail(`検査対象が見つからない: ${targetArg}`);
  if (!statSync(target).isDirectory()) {
    return target.endsWith(".html") ? [target] : fail(`検査対象が .html でもディレクトリでもない: ${targetArg}`);
  }
  return walk(target, (name) => name.endsWith(".html"), []).sort();
}

// --- A-1 生値 --------------------------------------------------------------

// コメントは描画されないので対象外。ただし**空白に置き換えて長さと改行を保つ**
// （後続の行番号がずれないようにするため）。
const stripComments = (html) =>
  html.replace(/<!--[\s\S]*?-->/g, (m) => m.replace(/[^\n]/g, " "));

// 走査するのは「見た目を決められる場所」だけ。本文テキストや href / id の中の
// #abc（アンカー・データ）を違反にしないため、属性は塗り・寸法を持つものに限る。
const PAINT_ATTRS = new Set([
  "style",
  "bgcolor",
  "background",
  "color",
  "fill",
  "stroke",
  "stop-color",
  "flood-color",
  "lighting-color",
  "border",
  "cellpadding",
  "cellspacing",
  "hspace",
  "vspace",
]);

const STYLE_BLOCK = /<style\b[^>]*>([\s\S]*?)<\/style>/gi;
const ATTR = /([A-Za-z_:][-A-Za-z0-9_:.]*)\s*=\s*(?:"([^"]*)"|'([^']*)'|([^\s">]+))/g;

const RAW_VALUE = [
  // #rgb / #rgba / #rrggbb / #rrggbbaa
  { kind: "色（hex）", re: /#(?:[0-9a-fA-F]{8}|[0-9a-fA-F]{6}|[0-9a-fA-F]{3,4})\b/g },
  { kind: "色（関数）", re: /\b(?:rgba?|hsla?)\s*\([^)]*\)/gi },
  { kind: "px", re: /(?<![-\w.])\d*\.?\d+px\b/gi },
];

const lineAt = (text, index) => text.slice(0, index).split("\n").length;

// 走査対象の断片（内容 + 元テキストでの開始位置 + どこで見つけたか）を集める
function paintSegments(src) {
  const segments = [];
  for (const m of src.matchAll(STYLE_BLOCK)) {
    segments.push({ text: m[1], start: m.index + m[0].indexOf(m[1]), where: "<style>" });
  }
  for (const m of src.matchAll(ATTR)) {
    const name = m[1].toLowerCase();
    if (!PAINT_ATTRS.has(name)) continue;
    const value = m[2] ?? m[3] ?? m[4] ?? "";
    if (!value) continue;
    segments.push({ text: value, start: m.index + m[0].indexOf(value), where: `${name}=` });
  }
  return segments;
}

function checkRawValues(page, label) {
  const src = stripComments(readFileSync(page, "utf8"));
  const found = [];
  for (const seg of paintSegments(src)) {
    for (const { kind, re } of RAW_VALUE) {
      for (const v of seg.text.matchAll(new RegExp(re.source, re.flags))) {
        found.push({
          file: label,
          line: lineAt(src, seg.start + v.index),
          kind,
          value: v[0],
          where: seg.where,
        });
      }
    }
  }
  return found;
}

// --- A-2 複製の同一性 ------------------------------------------------------

// 改行コードだけを揃えて比較する（内容同一が条件。コメント・並び順も比較対象）。
const normalizeCss = (text) => text.replace(/\r\n/g, "\n").replace(/\n+$/, "\n");

function firstDiffLine(a, b) {
  const la = a.split("\n");
  const lb = b.split("\n");
  for (let i = 0; i < Math.max(la.length, lb.length); i++) {
    if (la[i] !== lb[i]) return { line: i + 1, source: la[i] ?? "（行なし）", copy: lb[i] ?? "（行なし）" };
  }
  return null;
}

// html を持つディレクトリ（= pages/）ごとに tokens/styleguide.css を要求する
function checkCopies(pages, sourceText, labelOf) {
  const pageDirs = [...new Set(pages.map((p) => dirname(p)))].sort();
  return pageDirs.map((dir) => {
    const copy = join(dir, TOKENS_DIR, STYLEGUIDE_CSS);
    const label = labelOf(copy);
    if (!existsSync(copy)) return { file: label, status: "missing", detail: "複製が無い" };
    const text = normalizeCss(readFileSync(copy, "utf8"));
    if (text === sourceText) return { file: label, status: "identical" };
    return { file: label, status: "different", detail: firstDiffLine(sourceText, text) };
  });
}

// --- B-1 部品クラスの集合突合 ----------------------------------------------

// 宣言ブロック（{...}）を落とし、セレクタ部分からクラス名を拾う。
// 値の中の url(a.png) や .5rem を拾わないため、必ず「{ の手前」だけを見る。
function definedClasses(css) {
  const src = css.replace(/\/\*[\s\S]*?\*\//g, " ");
  const names = new Set();
  let depth = 0;
  let selector = "";
  for (const ch of src) {
    if (ch === "{") {
      if (depth === 0) {
        for (const m of selector.matchAll(/\.([-_a-zA-Z][-_a-zA-Z0-9]*)/g)) names.add(m[1]);
      }
      depth++;
      selector = "";
      continue;
    }
    if (ch === "}") {
      depth = Math.max(0, depth - 1);
      selector = "";
      continue;
    }
    if (depth === 0) selector += ch;
  }
  return names;
}

const CLASS_ATTR = /\bclass\s*=\s*(?:"([^"]*)"|'([^']*)'|([^\s">]+))/gi;

function usedClasses(page, label) {
  const src = stripComments(readFileSync(page, "utf8"));
  const out = [];
  for (const m of src.matchAll(CLASS_ATTR)) {
    const value = m[1] ?? m[2] ?? m[3] ?? "";
    for (const name of value.split(/\s+/)) {
      if (name) out.push({ name, file: label, line: lineAt(src, m.index) });
    }
  }
  return out;
}

// --- 検査本体 --------------------------------------------------------------

function check(rootArg, targetArg) {
  const root = resolve(rootArg);
  if (!existsSync(root) || !statSync(root).isDirectory()) {
    fail(`案件ルートが見つからない: ${rootArg}（出力ルート = 直下に styleguide.css が在るディレクトリ）`);
  }
  const source = join(root, STYLEGUIDE_CSS);
  if (!existsSync(source)) {
    fail(`案件ルート直下に ${STYLEGUIDE_CSS} が無い: ${source}（見た目の正は案件に 1 枚 — 先に SG を実行する）`);
  }
  const sourceText = normalizeCss(readFileSync(source, "utf8"));

  const pages = collectPages(targetArg);
  const target = resolve(targetArg);
  const labelOf = (p) => {
    const rel = relative(root, p);
    return (rel && !rel.startsWith("..") ? rel : p).split(sep).join("/");
  };

  const rawValues = [];
  const used = new Map(); // クラス名 -> 出現箇所
  for (const page of pages) {
    const label = labelOf(page);
    rawValues.push(...checkRawValues(page, label));
    for (const u of usedClasses(page, label)) {
      if (!used.has(u.name)) used.set(u.name, []);
      used.get(u.name).push(`${u.file}:${u.line}`);
    }
  }

  const copies = checkCopies(pages, sourceText, labelOf);

  const defined = definedClasses(readFileSync(source, "utf8"));
  const undefinedClasses = [...used.entries()]
    .filter(([name]) => !defined.has(name))
    .map(([name, at]) => ({ name, count: at.length, at }))
    .sort((a, b) => a.name.localeCompare(b.name));

  const violations = rawValues.length + copies.filter((c) => c.status !== "identical").length;

  return {
    root: root.split(sep).join("/"),
    target: target.split(sep).join("/"),
    styleguide: labelOf(source),
    pages: pages.length,
    definedClasses: defined.size,
    rawValues,
    copies,
    undefinedClasses,
    violations, // Tier A（fail の対象）
    notices: undefinedClasses.length, // Tier B（報告のみ）
    ok: violations === 0,
  };
}

// --- 出力 -----------------------------------------------------------------

function report(r) {
  console.log(`\n=== パレット検査: ${r.target} （${r.pages} ページ） ===`);
  console.log(`見た目の正: ${r.styleguide}（部品クラス ${r.definedClasses} 個）`);

  console.log(`\n[Tier A] ① 生値: ${r.rawValues.length} 件`);
  if (r.rawValues.length === 0) {
    console.log("  生値なし（見た目は styleguide.css の変数・部品クラスだけから引けている）");
  }
  for (const v of r.rawValues) {
    console.log(`  - ${v.file}:${v.line} ${v.where} に ${v.kind} "${v.value}"`);
  }

  const broken = r.copies.filter((c) => c.status !== "identical");
  console.log(
    `\n[Tier A] ② 複製の同一性（pages/tokens/${STYLEGUIDE_CSS}）: ${r.copies.length} 件中 ${broken.length} 件が不一致`,
  );
  if (broken.length === 0) {
    console.log("  全複製が案件直下の正と同一（= feature 間でも同一）");
  }
  for (const c of broken) {
    if (c.status === "missing") {
      console.log(`  - ${c.file}: ${c.detail}（案件直下の ${STYLEGUIDE_CSS} を複製する）`);
      continue;
    }
    const d = c.detail;
    console.log(`  - ${c.file}: 正と内容が違う（${d.line} 行目）`);
    console.log(`      正   : ${d.source}`);
    console.log(`      複製 : ${d.copy}`);
  }

  console.log(
    `\n[Tier B] ③ styleguide.css に定義の無い部品クラス: ${r.undefinedClasses.length} 種（報告のみ — fail にしない）`,
  );
  for (const c of r.undefinedClasses) {
    console.log(`  - .${c.name}（${c.count} 箇所）: ${c.at.slice(0, 5).join(" / ")}${c.at.length > 5 ? " …" : ""}`);
  }
  if (r.undefinedClasses.length > 0) {
    console.log(
      "  → STYLEGUIDE.md §4 に在る部品か確かめる。無い部品なら作らず manifest の missing[] に記録する",
    );
  }

  console.log(`\nTier A の違反: ${r.violations} 件 / Tier B の報告: ${r.notices} 種`);
  console.log(
    r.ok
      ? "OK: 生値なし・複製は正と同一"
      : "NG: 入力（画面設計書 / STYLEGUIDE.md）を直して再生成する（ページを手で直さない）",
  );
}

function fail(message) {
  console.error(`エラー: ${message}`);
  process.exit(2);
}

// --- 引数 -----------------------------------------------------------------

const argv = process.argv.slice(2);
const asJson = argv.includes("--json");
const positional = argv.filter((a) => !a.startsWith("--"));

if (positional.length !== 2) {
  console.error("使い方: node check-palette.mjs <案件ルート> <検査対象> [--json]");
  process.exit(2);
}

const result = check(positional[0], positional[1]);
if (asJson) {
  console.log(JSON.stringify(result, null, 2));
} else {
  report(result);
}
process.exit(result.ok ? 0 : 1);
