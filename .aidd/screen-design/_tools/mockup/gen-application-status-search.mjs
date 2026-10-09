// application-status-search の mockup を生成する（mockup-authoring の手順 4）。
//   node .aidd/screen-design/_tools/mockup/gen-application-status-search.mjs <案件ルート>
// 入力の正: 画面設計書 .aidd/screen-design/application-status-search/screen-spec.md（§3-1）/
//           画面マップ §3・§4 / STYLEGUIDE.md・styleguide.css。
// 手で HTML を直さない。直すときは入力を直し、本スクリプトを合わせて再生成する。
// JS を出力しない・色と px の生値を出力しない・データは固定値ダミー（識別子は汎用の数値）。
import { copyFileSync, mkdirSync, writeFileSync } from "node:fs";
import { join, resolve } from "node:path";
import { esc, page } from "./shell.mjs";

const root = resolve(process.argv[2] ?? ".");
const out = join(root, ".aidd/screen-design/application-status-search/pages");
mkdirSync(join(out, "tokens"), { recursive: true });
copyFileSync(join(root, "styleguide.css"), join(out, "tokens/styleguide.css")); // 内容を変えずに複製

const TITLE = "物件契約情報申請状況検索/一覧"; // 画面設計書 §3-1-6 <title>
const SCREEN_LABEL = "[GWTG060]物件契約情報申請状況検索/一覧"; // 同「シェル上の画面名」

// ---- ページのファイル名（画面 × 状態 = 1 ページ） -------------------------------------------
const P = {
  initial: "s-01-initial.html",
  default: "s-01-default.html",
  zero: "s-01-zero.html",
  loading: "s-01-loading.html",
  inputError: "s-01-input-error.html",
  overLimit: "s-01-over-limit.html",
  warning: "s-01-warning-confirm.html",
  importing: "s-01-importing.html",
  external: "s-01-external.html",
  longText: "s-01-long-text.html",
  calendar: "s-01-calendar.html",
};

// ---- 部品の小さな組み立て -----------------------------------------------------------------
const label = (t) => `<td class="condition-label">${esc(t)}</td>`;
const value = (h) => `<td class="condition-value">${h}</td>`;
const empty = () => `<td class="condition-value"></td>`; // 空けた組（格子を保つ）
const emptyLabel = () => `<td class="condition-label"></td>`;
const text = (cls, v = "", extra = "") =>
  `<input type="text" class="field-input ${cls}${extra}" value="${esc(v)}">`;
const ro = (cls, v = "") => `<input type="text" class="field-input ${cls} field-input-readonly" value="${esc(v)}" readonly>`;
const select = (opts, sel = "", extra = "") =>
  `<select class="select${extra}">${opts.map((o) => `<option${o === sel ? " selected" : ""}>${esc(o)}</option>`).join("")}</select>`;
// 日付欄 — mockup では欄そのものを a で描き、月次カレンダーの状態ページへ遷移させる（STYLEGUIDE.md §9 #11 (6) / #14）
const date = (v = "", err = false) =>
  `<a class="field-input field-input-sm field-input-date${err ? " field-input-error" : ""}" href="${P.calendar}">${esc(v)}</a>`;
const time = (v) => text("field-input-sm", v);
const dtRange = () => `${date()} ${time("00:00")} 〜 ${date()} ${time("23:59")}`;
const dRange = (fromV = "", fromErr = false) => `${date(fromV, fromErr)} 〜 ${date()}`;

// ---- 検索条件（画面設計書 §3-1-2 の組み方 / §3-1-3 の項目定義） ----------------------------
function conditions({ external = false, err = false, filled = false } = {}) {
  const pc = (v, e) => text("field-input-xs", v, e ? " field-input-error" : "");
  const progressDays = external ? null : pc(err ? "1a" : "", err);
  const progressSel = external ? null : select(["以上", "以下"], "以上");
  const company = external ? select(["サンプル会社（自社）"], "サンプル会社（自社）", " select-readonly") : select([""]);
  const shozoku = (n) => (external ? ro("field-input-lg") : text("field-input-lg"));
  const rows = [
    [label("申請No") + value(text("")), label("稟議ﾊﾞｰｺｰﾄﾞNo") + value(text("field-input-lg")), label("基地局番号") + value(text(""))],
    [label("ｴﾘｱ") + value(select([""])), label("基地局名") + value(text("field-input-lg")), label("ｽﾃｰﾀｽ") + value(select([""]))],
    [label("状態") + value(select([""])), label("契約稟議起案担当者") + value(text("field-input-lg")), label("更新者") + value(text(""))],
    [label("契約稟議起案会社名") + value(company), label("契約稟議起案所属①") + value(shozoku(1)),
      label("依頼内容") + value(select(["", "稟議依頼", "再製本依頼"], filled ? "稟議依頼" : ""))],
    [label("施策") + value(select([""])), label("契約稟議起案所属②") + value(shozoku(2)), label("押印種別") + value(select([""]))],
    [progressDays === null ? emptyLabel() + empty() : label("進捗検索(日数)") + value(progressDays),
      label("発送書類名") + value(text("field-input-lg")),
      progressSel === null ? emptyLabel() + empty() : label("進捗検索(選択)") + value(progressSel)],
    [label("転貸借契約種別") + value(select([""])), label("案件小ｸﾞﾙｰﾌﾟ") + value(text("field-input-lg")), emptyLabel() + empty()],
  ];
  const rowsB = [
    [label("起案日時") + value(dtRange()), label("稟議承認日") + value(dRange(err ? "2026/02/30" : "", err))],
    [label("申請日時") + value(dtRange()), label("初回支払日") + value(dRange())],
    [label("確認日時") + value(dtRange()), label("発送希望日") + value(dRange())],
  ];
  const table = (rs) =>
    `<div class="condition-scroll">\n<table class="condition-table">\n${rs.map((r) => `<tr>${r.join("")}</tr>`).join("\n")}\n</table>\n</div>`;
  return `<fieldset class="section">
<legend class="section-title">検索条件</legend>
${table(rows)}
${table(rowsB)}
</fieldset>`;
}

// アクション行（条件表の下）— 遷移表: 検索 → 通常 / ｸﾘｱ → 初期表示 / CSV 出力 → 同画面のまま
const actions = () => `<div class="button-area">
<a class="btn" href="${P.default}">検索(F)</a>
<a class="btn" href="${P.initial}">ｸﾘｱ(R)</a>
<a class="btn" href="${P.default}">CSV出力(O)</a>
</div>`;

// ---- 一覧（§3-1-3 #39〜#52 / §3-1-2 の列幅の割り付け） ---------------------------------------
const COLS = [
  ["申請No", "list-col-narrow"], ["依頼内容", "list-col-narrow"], ["審査フェーズ", "list-col-default"],
  ["状態", "list-col-narrow"], ["稟議バーコードNo", "list-col-wide"], ["基地局番号", "list-col-default"],
  ["基地局名", "list-col-wide"], ["案件小グループ", "list-col-default"], ["起案会社名", "list-col-wide"],
  ["エリア", "list-col-default"], ["起案担当者", "list-col-narrow"], ["起案日", "list-col-narrow"],
  ["発送希望日", "list-col-narrow"], ["施策", "list-col-default"],
];

// 表示バイト数で切る（全角 2・半角 1）。全文のツールチップは STYLEGUIDE.md §4 に器が無いため描かない（missing[]）
const cut = (s, max) => {
  let n = 0, r = "";
  for (const ch of s) {
    const c = ch.codePointAt(0);
    const b = c < 0x80 || (c >= 0xff61 && c <= 0xff9f) ? 1 : 2;
    if (n + b > max) break;
    n += b; r += ch;
  }
  return r;
};

// ダミーの業務状態名は画面設計書 §3-1-6 の名称だけ（審査フェーズ: 未起案 / 承認済、状態: 下書き / 取込中 / 完了）
function rows({ long = false, importingNo = null } = {}) {
  const list = [];
  for (let i = 0; i < 50; i++) {
    const no = 1000128 - i;
    const k = i % 10;
    let phase = k % 3 === 0 ? "未起案" : "承認済";
    let state = phase === "未起案" ? "下書き" : "完了";
    if (k === 4) phase += "(再申請)";
    if (k === 7 || no === importingNo) state = "取込中";
    const multi = k === 2 ? 2 : 0;
    const noIssue = k === 5; // 発行依頼書の無い申請 — その列は空
    const stName = long ? "サンプル長い名称の基地局" + (i + 1) : "サンプル基地局" + (i + 1);
    const grp = long ? "サンプル案件小グループの長い名称" : "案件グループ" + ((i % 3) + 1);
    const comp = long ? "サンプル会社の長い正式名称株式会社" : "サンプル会社" + ((i % 5) + 1);
    const area = long ? "01:サンプルエリアの長い名称" : "0" + ((i % 4) + 1) + ":エリア" + ((i % 4) + 1);
    const person = long ? "サンプル担当者長い氏名" : "担当者 " + ((i % 7) + 1);
    const day = String(28 - (i % 28)).padStart(2, "0");
    list.push({
      no, state,
      cells: [
        null, // 申請No（下で組む）
        k === 6 ? "再製本依頼" : "稟議依頼",
        phase,
        state,
        "2026" + String(100000 + no).slice(-6),
        String(100000000 + no) + (multi ? `他${multi}局` : ""),
        (long ? cut(stName, 16) : stName) + (multi ? `他${multi}局` : ""),
        noIssue ? "" : long ? cut(grp, 15) : grp,
        noIssue ? "" : long ? cut(comp, 22) : comp,
        long ? cut(area, 15) : area,
        noIssue ? "" : long ? cut(person, 10) : person,
        phase === "未起案" ? "" : `2026/09/${day}`,
        `2026/10/${day}`,
        "施策" + "ABC"[i % 3],
      ],
    });
  }
  return list;
}

function listArea(opts = {}) {
  const head = `<colgroup>${COLS.map(([, c]) => `<col class="${c}">`).join("")}</colgroup>
<thead><tr>${COLS.map(([h]) => `<th class="list-header">${esc(h)}</th>`).join("")}</tr></thead>`;
  if (opts.zero) {
    return `<div class="list-scroll">
<table class="list-table">
${head}
<tbody></tbody>
</table>
</div>
<div class="empty-state">該当するデータはありません</div>`;
  }
  const body = rows(opts)
    .map((r) => {
      // 申請No のリンク — 行き先（物件基本情報登録変更画面）は画面マップ §3 に無いので href を持たない a（pending）。
      // 取込中の行はリンクにしない（AC 2.8）
      const noCell = r.state === "取込中" ? esc(r.no) : `<a>${esc(r.no)}</a>`;
      const cells = r.cells.map((v, i) => {
        const num = i === 11 || i === 12;
        return `<td class="${num ? "list-cell list-cell-num" : "list-cell"}">${i === 0 ? noCell : esc(v)}</td>`;
      });
      return `<tr class="list-row">${cells.join("")}</tr>`;
    })
    .join("\n");
  return `<div class="list-caption">1-50件目/128件</div>
<div class="list-scroll">
<table class="list-table">
${head}
<tbody>
${body}
</tbody>
</table>
</div>
<div class="pagination">
<span class="pagination-side">＜前へ</span>
<span class="pagination-current">1</span>
<a class="pagination-link" href="${P.default}">2</a>
<a class="pagination-link" href="${P.default}">3</a>
<a class="pagination-side" href="${P.default}">次へ＞</a>
</div>`;
}

const bannerError = (lines) =>
  `<div class="banner-error"><ul class="banner-list">${lines.map((l) => `<li>${esc(l)}</li>`).join("")}</ul></div>`;
const bannerWarning = (lines) =>
  `<div class="banner-warning"><ul class="banner-list">${lines.map((l) => `<li>${esc(l)}</li>`).join("")}</ul></div>`;

// ---- 状態ごとのページ（画面設計書 §3-1-5） ---------------------------------------------------
const W_DS_100024 = "DS-100024：検索結果が上限件数を超えました。条件を絞り込んでください。"; // drafted_wording
const W_DS_100025 = "DS-100025：検索結果の件数が多くなっています。検索を続行しますか。"; // drafted_wording

const pages = {
  [P.initial]: { body: [conditions(), actions()] },
  [P.default]: { body: [conditions({ filled: true }), actions(), listArea()] },
  [P.zero]: { body: [conditions({ filled: true }), actions(), listArea({ zero: true })] },
  [P.loading]: {
    body: [conditions({ filled: true }), actions(), `<div class="wait-message">処理中です。しばらくお待ちください。</div>`],
  },
  [P.inputError]: {
    body: [
      bannerError(["WTG-000003：稟議承認日From:日付が不正です", "GEF-000014：進捗検索(日数):数値を入力して下さい"]),
      conditions({ err: true }), actions(),
    ],
  },
  [P.overLimit]: { body: [bannerError([W_DS_100024]), conditions({ filled: true }), actions()] },
  [P.warning]: {
    body: [conditions({ filled: true }), actions()],
    overlay: `<div class="dialog-backdrop">
<div class="dialog-panel">
<p>${esc(W_DS_100025)}</p>
<div class="button-area">
<a class="btn" href="${P.default}">続行(Y)</a>
<a class="btn" href="${P.initial}">中止(N)</a>
</div>
</div>
</div>`,
  },
  [P.importing]: {
    body: [
      bannerWarning(["WTG-100018：取込処理中のため登録画面へ遷移できません"]),
      conditions({ filled: true }), actions(), listArea({ importingNo: 1000125 }),
    ],
  },
  [P.external]: { body: [conditions({ external: true }), actions(), listArea()] },
  [P.longText]: { body: [conditions({ filled: true }), actions(), listArea({ long: true })] },
  [P.calendar]: {
    body: [conditions(), actions()],
    // 月次カレンダー — 固定の 1 か月（2026 年 10 月。今日 = 9 日・選択中なし）。
    // 月送り（.calendar-nav）と曜日見出し（.calendar-weekday）の文言、閉じる（.dialog-close）のラベルは
    // STYLEGUIDE.md に無いため描かない（missing[]）。日のセルはただの表示（§9 #14）
    overlay: `<div class="dialog-backdrop">
<div class="dialog-panel">
<div class="calendar-panel">
<div class="calendar-header"><span class="calendar-title">2026年10月</span></div>
<table class="calendar-table">
${calendarRows()}
</table>
</div>
</div>
</div>`,
  },
};

function calendarRows() {
  // 日曜始まり。2026/10/01 は木曜。前月末（9/27〜30）と翌月頭（11/1〜7）は当月外
  const cells = [];
  for (let d = 27; d <= 30; d++) cells.push([d, "calendar-day calendar-day-outside"]);
  for (let d = 1; d <= 31; d++) cells.push([d, d === 9 ? "calendar-day calendar-day-today" : "calendar-day"]);
  for (let d = 1; cells.length % 7 !== 0; d++) cells.push([d, "calendar-day calendar-day-outside"]);
  const trs = [];
  for (let i = 0; i < cells.length; i += 7)
    trs.push(`<tr>${cells.slice(i, i + 7).map(([d, c]) => `<td class="${c}">${d}</td>`).join("")}</tr>`);
  return trs.join("\n");
}

for (const [file, p] of Object.entries(pages)) {
  writeFileSync(
    join(out, file),
    page({ title: TITLE, screenLabel: SCREEN_LABEL, body: p.body.join("\n"), overlay: p.overlay ?? "" }),
  );
}
console.log(`generated ${Object.keys(pages).length} pages → ${out}`);
