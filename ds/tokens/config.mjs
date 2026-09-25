// Style Dictionary v4 設定（既定テーマ = ベースDS）。primitive.json（共有）+ semantic.json
// （既定値・プレースホルダ色）を唯一の正として3系統に配信する。dist/ 配下は生成物なので直接編集しない。
//
// サービス別テーマ（HANDOFF 設計判断14 — DS パッケージは分割しない）:
// tokens/semantic.<service>.json にブランド色の差分のみを持たせ、
// tokens/config.<service>.mjs で source に追加する（config.travel-expense-demo.mjs が実例）。
// プリミティブ層と部品実装は全テーマ共有のまま。
export default {
  source: ["tokens/primitive.json", "tokens/semantic.json"],
  platforms: {
    css: {
      transformGroup: "css",
      buildPath: "tokens/dist/",
      files: [{ destination: "tokens.css", format: "css/variables" }]
    },
    ts: {
      transformGroup: "js",
      buildPath: "tokens/dist/",
      files: [{ destination: "theme.ts", format: "javascript/es6" }]
    },
    // Claude Design の /design-sync に食わせる用（中身は css と同一でよい）
    claudeDesign: {
      transformGroup: "css",
      buildPath: "tokens/dist/",
      files: [{ destination: "theme-claude-design.css", format: "css/variables" }]
    }
  }
};
