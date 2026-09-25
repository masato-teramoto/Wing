// Style Dictionary v4 設定（travel-expense-demo = 案件テーマの【参考実装例】）。
// ベース（primitive.json + semantic.json）に semantic.travel-expense-demo.json を
// 追加ソースとして重ね、primary 系キーだけをこの案件のブランド色で上書きする。
// dist/ 配下は生成物なので直接編集しない。
//
// 【注意】これは examples/ 配下のサンプルであり、実案件では本ファイルを
// tokens/config.<project>.mjs、semantic を tokens/semantic.<project>.json に置く
// （AGENTS.md / tokens/HARVESTING.md の規約）。詳細は同ディレクトリの README.md。
// パスは実行時のカレントディレクトリ（リポジトリルート）からの相対。
export default {
  source: [
    "tokens/primitive.json",
    "tokens/semantic.json",
    "examples/travel-expense-demo/semantic.travel-expense-demo.json"
  ],
  platforms: {
    css: {
      transformGroup: "css",
      buildPath: "tokens/dist/travel-expense-demo/",
      files: [{ destination: "tokens.css", format: "css/variables" }]
    },
    ts: {
      transformGroup: "js",
      buildPath: "tokens/dist/travel-expense-demo/",
      files: [{ destination: "theme.ts", format: "javascript/es6" }]
    },
    claudeDesign: {
      transformGroup: "css",
      buildPath: "tokens/dist/travel-expense-demo/",
      files: [{ destination: "theme-claude-design.css", format: "css/variables" }]
    }
  }
};
