// components/*/<Name>.component-spec.json と patterns/*/pattern.json を走査して
// index.json（AI向けカタログ）を再生成する。
// --check を付けるとコミット済み index.json との差分を検出して CI を落とす。
import { readdirSync, readFileSync, writeFileSync, existsSync } from "node:fs";
import { join } from "node:path";
import { fileURLToPath } from "node:url";

const root = fileURLToPath(new URL("..", import.meta.url));
const componentsDir = join(root, "components");
const patternsDir = join(root, "patterns");

const components = readdirSync(componentsDir, { withFileTypes: true })
  .filter((d) => d.isDirectory())
  .map((d) => {
    const specPath = join(componentsDir, d.name, `${d.name}.component-spec.json`);
    if (!existsSync(specPath)) {
      console.error(`NG: ${d.name} に component-spec.json がありません（部品の追加は DS 側フローで行う）`);
      process.exit(1);
    }
    const spec = JSON.parse(readFileSync(specPath, "utf8"));
    return {
      name: spec.name,
      status: spec.status,
      purpose: spec.purpose,
      spec: `components/${d.name}/${d.name}.component-spec.json`
    };
  })
  .sort((a, b) => a.name.localeCompare(b.name));

const patterns = existsSync(patternsDir)
  ? readdirSync(patternsDir, { withFileTypes: true })
      .filter((d) => d.isDirectory())
      .map((d) => {
        const patternPath = join(patternsDir, d.name, "pattern.json");
        if (!existsSync(patternPath)) {
          console.error(`NG: patterns/${d.name} に pattern.json がありません（パターンの追加は DS 側フローで行う）`);
          process.exit(1);
        }
        const pattern = JSON.parse(readFileSync(patternPath, "utf8"));
        return {
          name: pattern.name,
          status: pattern.status,
          use_when: pattern.use_when,
          pattern: `patterns/${d.name}/pattern.json`
        };
      })
      .sort((a, b) => a.name.localeCompare(b.name))
  : [];

const index = {
  $comment: "自動生成。手で編集しない。ここに無い部品・パターンは存在しない（自作もしない）",
  generated_by: "scripts/generate-index.mjs",
  components,
  patterns,
  does_not_exist_yet: {
    // 捏造されがちな部品名（C-2 の絞りから漏れたもの。デジ庁に部品があっても
    // 第一弾の自社 DS には無い。TextField は「無い」のではなく InputText の旧称 →
    // InputText spec の confusable_with 参照）
    // Checkbox / DatePicker / RadioButton / Textarea はモック検証の起票を経て
    // 2026-08-18 に spec 追加・昇格済み（DECISIONS.md モック検証ログ参照）
    // InputNumber は GAP-12 で「作らない」と決定（2026-08-25。金額・数量は InputText の
    // numeric_input_guidance）— 捏造防止のため名前は残す
    // DateFieldSet は GAP-13 で「作らない」と決定（2026-08-25。年/月/日の分割入力は
    // DatePicker の calendar=false variant）— 捏造防止のため名前は残す
    // Skeleton は GAP-11 で 2026-08-25 に部品として新設・昇格済み（自社定義）
    // IconButton は GAP-14 で不採用（2026-08-25。行操作列を設けず、アイコンのみのボタンは
    // 作らない — Button / Table spec 参照）— 捏造防止のため名前は残す
    // FileUpload（GAP-03）/ NotificationBanner（GAP-01）/ Disclosure（GAP-07）はデジ庁公開済み
    // ガイドラインから採取し 2026-08-25 に昇格済み。Combobox（GAP-02）/ Tabs（GAP-08）は
    // デジ庁準備中のため自社翻案で同日昇格。
    // Toast は GAP-01 で不採用（自動消滅する通知は作らない — NotificationBanner spec 参照）。
    // Accordion は GAP-08 で見送り（デジ庁の用途は FAQ 等の同種セクション連続で、業務画面の
    // 情報分割には不適合 — Tabs / Disclosure spec の confusable_with 参照）
    // Pagination は GAP-06 で 2026-08-25 に自社定義で新設・昇格済み（simple / numbered）。
    // PageNavigation はデジ庁名「ページナビゲーション」の英訳で同一物のため捏造防止に残す
    // （Pagination spec の confusable_with で誘導）
    components: [
      "Accordion", "Breadcrumb", "ButtonGroup", "Card",
      "DateFieldSet", "DescriptionList", "Drawer", "IconButton",
      "InputNumber", "PageNavigation",
      "StepNavigation", "Toast", "Tooltip"
    ],
    // app-shell は 2026-08-18 MK2 レビュー指摘を受けて新規追加・昇格済み（DECISIONS.md モック検証ログ参照）
    // error-page は業務システム対応ギャップ GAP-04 で 2026-08-25 に新設・昇格済み
    // advanced-search は GAP-07 で「独立パターンにせず list-page の詳細検索パネル
    // （Disclosure）で提供」と決定したため 2026-08-25 に除外（list-page の use_when 参照）
    // login は GAP-09 で 2026-08-25 に新設・昇格済み（シェル無しパターン）
    // report は GAP-10 で 2026-08-25 に新設・昇格済み。print-preview は同 GAP で見送り
    // （ブラウザの印刷プレビューに委ねる — report パターン参照）
    // approval / inbox は GAP-16 で 2026-08-25 に新設・昇格済み（detail-page / list-page 準拠の variant）
    // 以下 PATTERN-CATALOG の Tier 2 / Tier 3（昇格は MK1 / CHK の起票経由）
    patterns: [
      "wizard", "master-maintenance", "import",
      "dashboard", "settings",
      "list-detail-split", "tree-detail", "calendar", "job-monitor",
      "audit-log", "diff-compare", "role-matrix", "print-preview",
      "board"
    ]
  },
  note_for_agents:
    "does_not_exist_yet の部品・パターンが必要になったら、実装せず人間に起票すること"
};

const out = JSON.stringify(index, null, 2) + "\n";
const indexPath = join(root, "index.json");

if (process.argv.includes("--check")) {
  const current = existsSync(indexPath) ? readFileSync(indexPath, "utf8") : "";
  if (current !== out) {
    console.error("NG: index.json が古い。npm run generate:index を実行してコミットしてください");
    process.exit(1);
  }
  console.log("OK: index.json は最新です");
} else {
  writeFileSync(indexPath, out);
  console.log(`OK: index.json を再生成（部品 ${components.length} 件 / パターン ${patterns.length} 件）`);
}
