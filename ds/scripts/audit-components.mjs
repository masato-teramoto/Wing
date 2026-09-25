// アプリ側リポジトリで実行する想定の「野良UI部品」検出。
// DS 外からの UI ライブラリ import と、DS に無い ds- 接頭辞クラスを検出する。
// 使い方: node scripts/audit-components.mjs [検査対象ディレクトリ]
//   引数省略時は DS リポジトリ自身を検査。対象拡張子: .tsx .ts .html
//   （モック / ワイヤーフレームの HTML も検査対象。audit-ignore の禁止判定は
//   audit-tokens 側で行う: 除外機構を持つのがあちらのみのため）
import { readdirSync, readFileSync, statSync, existsSync } from "node:fs";
import { join, relative, resolve } from "node:path";
import { fileURLToPath } from "node:url";

const dsRoot = fileURLToPath(new URL("..", import.meta.url));
const target = process.argv[2] ? resolve(process.argv[2]) : dsRoot;
const dsIndexPath = join(dsRoot, "index.json");
const known = existsSync(dsIndexPath)
  ? new Set(JSON.parse(readFileSync(dsIndexPath, "utf8")).components.map((c) => c.name.toLowerCase()))
  : new Set();

const BANNED_IMPORTS = [/@mui\//, /antd/, /react-bootstrap/, /chakra-ui/];
const SKIP = new Set(["node_modules", ".git", "dist", "tokens"]);
let violations = 0;

function walk(dir) {
  for (const name of readdirSync(dir)) {
    const p = join(dir, name);
    if (statSync(p).isDirectory()) { if (!SKIP.has(name)) walk(p); continue; }
    if (!/\.(tsx|ts|html)$/.test(name)) continue;
    const text = readFileSync(p, "utf8");
    text.split("\n").forEach((line, i) => {
      for (const b of BANNED_IMPORTS) {
        if (b.test(line) && line.includes("import")) {
          console.error(`NG ${relative(target, p)}:${i + 1} DS外UIライブラリの import: ${line.trim()}`);
          violations++;
        }
      }
      for (const m of line.matchAll(/ds-([a-z]+)/g)) {
        if (known.size > 0 && !known.has(m[1])) {
          console.error(`NG ${relative(target, p)}:${i + 1} index.json に無い部品クラス "ds-${m[1]}"（捏造の疑い）`);
          violations++;
        }
      }
    });
  }
}
walk(target);
if (violations > 0) process.exit(1);
console.log("OK: 野良UI部品なし");
