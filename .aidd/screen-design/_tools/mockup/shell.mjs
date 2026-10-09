// mockup の共通シェル（ヘッダ）を 1 か所で組む。全 feature の生成器がこれを差し込む。
// シェルの内容の正は画面マップ §4-1（.aidd/screen-design/_app-shell/screen-map.md）、様式の正は STYLEGUIDE.md §4-10。
// ページごとに書き分けるのは現在地（ヘッダの画面名）と、入口画面での「MENU」の無効表示だけ。
// 色・px の生値をここに書かない（見た目は tokens/styleguide.css のクラスだけ）。

export const SYSTEM_NAME = "WiNG"; // 画面マップ §4-1「システム名」

// ヘッダの見出し（画面マップ §4-1「ヘッダの見出し」）とダミーの利用者情報（固定値）
const DUMMY_USER = "サンプル 利用者";
const DUMMY_ORG = "サンプル部";

export const esc = (s) =>
  String(s).replace(/&/g, "&amp;").replace(/</g, "&lt;").replace(/>/g, "&gt;").replace(/"/g, "&quot;");

// 入口（_app-shell:S-01）への相対パス。feature の pages/ から見た位置
const ENTRY_FROM_FEATURE = "../../_app-shell/pages/s-01-default.html";

/**
 * @param {object} o
 * @param {string} o.screenLabel   ヘッダの画面名の値（`[画面ID]画面名` の形。入口画面は「メニュー」）— 現在地
 * @param {boolean} [o.isEntry]    入口画面自身なら true（「MENU」を無効表示にする — 自己参照）
 * @param {string[]} [o.row1Links] 1 行目（その画面から直接飛ぶ機能）のリンクの HTML。0 本ならセルを空で残す
 */
export function header({ screenLabel, isEntry = false, row1Links = [] }) {
  const menu = isEntry
    ? `[<span class="app-header-link-disabled">MENU</span>]`
    : `[<a href="${ENTRY_FROM_FEATURE}">MENU</a>]`;
  // 「LOGOUT」は行き先（ログイン画面）が本案件の画面に無いため全画面で無効表示（画面マップ §3 ④ / §4-1）
  const logout = `[<span class="app-header-link-disabled">LOGOUT</span>]`;
  return `<table class="app-header">
  <tr>
    <td class="app-header-logo" rowspan="2">${esc(SYSTEM_NAME)}</td>
    <td class="app-header-meta">利用者 : ${esc(DUMMY_USER)}</td>
    <td class="app-header-meta">画面名 : ${esc(screenLabel)}</td>
    <td class="app-header-links">${row1Links.join(" ")}</td>
  </tr>
  <tr>
    <td class="app-header-meta">所属 : ${esc(DUMMY_ORG)}</td>
    <td class="app-header-meta"></td>
    <td class="app-header-links">${menu} ${logout}</td>
  </tr>
</table>`;
}

/** 1 ページ分の HTML。body は本文（.app-main の中身）、overlay は .app-main の外に置く重ね物（Dialog） */
export function page({ title, screenLabel, isEntry, row1Links, mainClass = "app-main", body, overlay = "" }) {
  return `<!doctype html>
<html lang="ja">
<head>
<meta charset="utf-8">
<title>${esc(title)} - ${esc(SYSTEM_NAME)}</title>
<link rel="stylesheet" href="tokens/styleguide.css">
</head>
<body>
${header({ screenLabel, isEntry, row1Links })}
<main class="${mainClass}">
${body}
</main>
${overlay}
</body>
</html>
`;
}
