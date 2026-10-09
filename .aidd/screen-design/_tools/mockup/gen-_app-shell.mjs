// _app-shell の mockup を生成する（mockup-authoring の手順 4）。
//   node .aidd/screen-design/_tools/mockup/gen-_app-shell.mjs <案件ルート>
// 入力の正: 画面設計書 .aidd/screen-design/_app-shell/screen-spec.md（§3-1 / §3-2）/
//           画面マップ §3・§4（§4-1 シェルの表示文言・§4-2 ナビ項目）/ STYLEGUIDE.md・styleguide.css。
// 手で HTML を直さない。直すときは入力を直し、本スクリプトを合わせて再生成する。
// JS を出力しない・色と px の生値を出力しない・データは固定値ダミー。
import { copyFileSync, mkdirSync, writeFileSync } from "node:fs";
import { join, resolve } from "node:path";
import { esc, page } from "./shell.mjs";

const root = resolve(process.argv[2] ?? ".");
const out = join(root, ".aidd/screen-design/_app-shell/pages");
mkdirSync(join(out, "tokens"), { recursive: true });
copyFileSync(join(root, "styleguide.css"), join(out, "tokens/styleguide.css")); // 内容を変えずに複製

// ---- S-01 メニュー（画面設計書 §3-1） -------------------------------------------------------
// ナビ項目は画面マップ §4-2 の並び順のまま。href が null の項目は無効表示（.app-menu-item-disabled）
const MENU_TITLE = "契約・管財管理"; // 画面マップ §4-1「入口画面のメニューの見出し」
const NAV_ITEMS = [
  { label: "物件基本情報登録変更", href: null }, // §4-2 #1 — property-basic-info は今回の対象外
  { label: "物件契約情報申請状況検索/一覧", href: "../../application-status-search/pages/s-01-default.html" }, // §4-2 #2
];

const menuBody = `<div class="app-menu-title">${esc(MENU_TITLE)}</div>
<ul class="app-menu">
${NAV_ITEMS.map((n) =>
  n.href
    ? `<li class="app-menu-item"><a href="${n.href}">${esc(n.label)}</a></li>`
    : `<li class="app-menu-item-disabled">${esc(n.label)}</li>`,
).join("\n")}
</ul>`;

// ---- S-02 システムエラー（画面設計書 §3-2） --------------------------------------------------
// 詳細欄・区切り・戻るボタンは置かない（画面設計書 §5-1 #4・#5）。値は §3-2-6 の mockup の例
const ERROR_ROW = {
  kind: "システムエラー", // 仮（画面設計書 §5-4 #1）
  code: "GEF-000000",
  message: "処理を続けられませんでした。お手数ですが、メニューからやり直してください。", // 仮（同上）
};

const errorBody = `<div class="system-error-title">システムエラー</div>
<table class="system-error-table">
<tr><th class="system-error-label">種別</th><th class="system-error-label">コード</th><th class="system-error-label">メッセージ</th></tr>
<tr><td class="system-error-body">${esc(ERROR_ROW.kind)}</td><td class="system-error-body">${esc(ERROR_ROW.code)}</td><td class="system-error-body">${esc(ERROR_ROW.message)}</td></tr>
</table>`;

const pages = {
  "s-01-default.html": { title: "メニュー", screenLabel: "メニュー", isEntry: true, body: menuBody },
  "s-02-default.html": { title: "システムエラー", screenLabel: "システムエラー", body: errorBody },
};

for (const [file, p] of Object.entries(pages)) {
  writeFileSync(join(out, file), page(p)); // row1Links は 0 本（画面設計書 §3-1-6 / §3-2-6 — セルを空で残す）
}
console.log(`generated ${Object.keys(pages).length} pages → ${out}`);
