// 生値の直書き検出。tokens/ と dist/ は対象外。
//   1. hex カラー（#fff / #ffffff / #11182780 等）
//   2. px 直書き
//   3. CSS 色キーワード（white / black / red / gray ... の named color）— CSS の値位置に限定して検出
//      （`color: white` / `border: 1px solid white` / JSX `style={{ color: "white" }}` / HTML style 属性）。
//      クラス名（.bg-white）・コメント・カスタムプロパティ名（--color-white:）・var(--...) の変数名・
//      URL 内（/white.png）は検出しない。transparent / currentColor / inherit / initial / unset は許容
//      （色ではなく「色を持たない・引き継ぐ」指定のため）
//   4. 色関数 rgb() / rgba() / hsl() / hsla() / hwb() / lab() / lch() / oklab() / oklch() の直書き
//      （半透明はトークン側で hex8 に持つ — 例: color.semantic.overlay）
//   5. 記号文字のアイコン転用（icons/ICON-MAP.md §6 — 2026-08-25 ICN-05）
//      a. class に icon を含む要素の中に空白以外のテキストがある（`<span class="ds-x-icon">✓</span>`）
//         → アイコンは語彙表の SVG。要素内にテキストを入れない
//      b. 要素の内容が記号文字だけ（`>✓<` / `>▼<` / `>×<`）→ 記号文字をアイコン代わりにしない
//         （「1366×768」のように文中に混ざる × は対象外。省略記号「…」は Pagination の正規表現のため対象外）
//      c. CSS の content: に記号文字（`content: "✓"`）
// 対象拡張子: .tsx .ts .css .html（stories とテストは除外）
// 使い方: node scripts/audit-tokens.mjs [検査対象ディレクトリ]
//   引数省略時は DS リポジトリ自身を検査。アプリ側からは監査対象ディレクトリ
//   （モック / ワイヤーフレームの出力先。例: .aidd/wireframe/<feature>/pages/）を指定して実行する。
// 検査対象ディレクトリを指定した外部監査では audit-ignore の出現自体を違反として数える
// （行単位の除外で exit 0 を作れると「監査 exit 0 = 生成の完了条件」が形骸化するため）。
// 引数省略時（DS 自己監査）のみ audit-ignore を行単位の除外として扱う。
import { readdirSync, readFileSync, statSync } from "node:fs";
import { join, relative, resolve } from "node:path";
import { fileURLToPath } from "node:url";

const dsRoot = fileURLToPath(new URL("..", import.meta.url));
// 引数あり = 外部監査（モック / ワイヤーフレーム等の成果物）。ディレクトリ名（旧: 「mock」一致）では
// 判定しない — 名前依存は対象の改名で無効化され、対象を直接指定すると相対パスに名前が残らず発火しないため
const strict = Boolean(process.argv[2]);
const target = strict ? resolve(process.argv[2]) : dsRoot;
const SKIP_DIRS = new Set(["tokens", "node_modules", "scripts", ".git"]);
const SKIP_FILE = /\.(stories|test)\.(t|j)sx?$/;
const TARGET = /\.(tsx|ts|css|html)$/;

const HEX = /#[0-9a-fA-F]{3,8}\b/g;
const PX = /(?<![\w-])\d+px\b/g;

// CSS named color のうち主要なもの（意味色 + 無彩色 + 代表的な light/dark 系）。
// 一般英単語と重なる名前（tan / gold / snow / linen / olive / coral / plum 等）は誤検出を避けるため含めない。
const NAMED_COLORS = [
  "white", "black", "red", "gray", "grey", "blue", "green", "yellow", "orange", "purple", "pink",
  "silver", "navy", "teal", "aqua", "cyan", "magenta", "fuchsia", "maroon", "crimson", "indigo",
  "violet", "turquoise", "lavender", "whitesmoke", "gainsboro", "lightgray", "lightgrey",
  "darkgray", "darkgrey", "dimgray", "dimgrey", "lightblue", "darkblue", "lightgreen", "darkgreen",
  "darkred", "skyblue", "steelblue", "slategray", "slategrey", "rebeccapurple", "aliceblue",
  "ghostwhite", "floralwhite", "lightyellow", "lightpink", "hotpink", "deeppink", "royalblue",
  "dodgerblue", "cornflowerblue", "midnightblue", "forestgreen", "seagreen", "limegreen",
  "springgreen", "darkorange", "orangered", "firebrick", "darkviolet", "blueviolet", "mediumpurple"
];
// 値位置に限定: 「: 〜 値 〜」が ; } または行末で終わる区間（{ を含む区間 = セレクタ側は対象外）。
// キーワードの前後に / . - _ が続くものは URL・ファイル名・識別子の一部とみなして除外。
const NAMED_COLOR_IN_VALUE = new RegExp(
  `:\\s*[^;{}]*?(?<![\\w/.\\-])(${NAMED_COLORS.join("|")})(?![\\w/.\\-])(?=[^;{}]*(?:[;}]|$))`,
  "gi"
);
const COLOR_FUNC = /(?<![\w-])(rgba?|hsla?|hwb|lab|lch|oklab|oklch)\(/g;

// 記号文字のアイコン転用（ICON-MAP §6）。+ − は文中で頻出するため b では対象にせず a（icon 要素内）でのみ拾う。
const ICON_SYMBOLS = "✓✔✕✗✖×▼▲▶◀►◄→←↑↓⚠ⓘ●■◆★☆";
// class のトークンが「icon」そのもの、または「-icon」で終わるもの（ds-notificationbanner-icon 等）を対象にする。
// ds-button--icon-lead のような「アイコン付きラベル」のクラスはテキストを持つのが正しいため対象外
const ICON_ELEMENT_WITH_TEXT = /<(\w+)[^>]*\bclass(?:Name)?=["'](?:[^"']*[\s-])?icon(?:\s[^"']*)?["'][^>]*>\s*([^<\s][^<]*)</gu;
const SYMBOL_ONLY_CONTENT = new RegExp(`>\\s*([${ICON_SYMBOLS}])\\s*<`, "gu");
const SYMBOL_IN_CSS_CONTENT = new RegExp(`content\\s*:\\s*["'][^"']*[${ICON_SYMBOLS}+−]`, "gu");

// 色キーワード・色関数の検出前に、誤検出源を行から取り除く（hex / px の検出は従来どおり生の行で行う）
function stripForColorCheck(line) {
  return line
    .replace(/\/\*.*?\*\//g, " ")          // ブロックコメント（行内で閉じるもの）
    .replace(/(^|\s)\/\/.*$/, "$1")        // 行コメント（http:// のような URL は空白が前に無いため残る）
    .replace(/var\(\s*--[\w-]+/g, "var(") // var(--color-white) の変数名部分（fallback 値は残して検査する）
    .replace(/--[\w-]+\s*:/g, "-- :");     // カスタムプロパティ名（--color-white:）— 値側は残して検査する
}

let violations = 0;
function walk(dir) {
  for (const name of readdirSync(dir)) {
    const p = join(dir, name);
    if (statSync(p).isDirectory()) {
      if (!SKIP_DIRS.has(name)) walk(p);
      continue;
    }
    if (!TARGET.test(name) || SKIP_FILE.test(name)) continue;
    const rel = relative(target, p);
    const text = readFileSync(p, "utf8");
    text.split("\n").forEach((line, i) => {
      if (line.includes("audit-ignore")) {
        if (!strict) return; // DS 自己監査（引数なし）では従来どおり行単位の除外として扱う
        console.error(`NG ${rel}:${i + 1} 外部監査（検査対象ディレクトリ指定時）では audit-ignore 使用禁止 — 除外せず違反として数える`);
        violations++;
      }
      for (const m of [...(line.match(HEX) ?? []), ...(line.match(PX) ?? [])]) {
        console.error(`NG ${rel}:${i + 1} 生値 "${m}" → トークン（var(--...)）を使う`);
        violations++;
      }
      const stripped = stripForColorCheck(line);
      for (const m of stripped.matchAll(NAMED_COLOR_IN_VALUE)) {
        console.error(`NG ${rel}:${i + 1} 色キーワード "${m[1]}" の直書き → 役割トークン（tokens/ROLE-MAP.md 参照。白は background / on-primary、灰は surface / border 等）を使う`);
        violations++;
      }
      for (const m of stripped.matchAll(COLOR_FUNC)) {
        console.error(`NG ${rel}:${i + 1} 色関数 "${m[1]}(" の直書き → トークンを使う（半透明が必要なら hex8 のトークン。例: color.semantic.overlay）`);
        violations++;
      }
      for (const m of line.matchAll(ICON_ELEMENT_WITH_TEXT)) {
        console.error(`NG ${rel}:${i + 1} アイコン用要素 <${m[1]} class*="icon"> にテキスト "${m[2].trim()}" → icons/ICON-MAP.md の語彙（SVG）を使い、要素内にテキストを入れない`);
        violations++;
      }
      for (const m of line.matchAll(SYMBOL_ONLY_CONTENT)) {
        console.error(`NG ${rel}:${i + 1} 記号文字 "${m[1]}" をアイコン代わりに使用 → icons/ICON-MAP.md の語彙（SVG）を使う（brand-principles.md 禁止リスト）`);
        violations++;
      }
      for (const m of line.matchAll(SYMBOL_IN_CSS_CONTENT)) {
        console.error(`NG ${rel}:${i + 1} CSS "${m[0]}" — content: に記号文字 → 擬似要素でアイコンを描かず icons/ICON-MAP.md の語彙（SVG）を使う`);
        violations++;
      }
    });
  }
}
walk(target);
if (violations > 0) {
  console.error(`\n${violations} 件の違反（hex / px / 色キーワード / 色関数 / 記号文字アイコン）。対応するトークン・アイコンが無い場合は audit-triage スキル参照（勝手にトークン・語彙を追加しない）`);
  process.exit(1);
}
console.log("OK: 生値の直書き・記号文字アイコンなし（hex / px / 色キーワード / 色関数 / 記号文字）");
