// Style Dictionary v4 設定（プロファイル: wireframe = 無彩色）。
// ベース（primitive.json + semantic.json）に semantic.wireframe.json を追加ソースとして重ね、
// 操作要素・ブランドの色だけを無彩色へ落とす。dist/ 配下は生成物なので直接編集しない。
//
// 【案件テーマとの違い】案件テーマ（config.<project>.mjs）は「この案件のブランド色」を入れるための
// オーバーレイだが、wireframe は案件をまたいで使うベースDS 側のプロファイルであり、
// 要件定義工程のワイヤーフレーム / ローファイプロトタイプ専用。したがって examples/ ではなく
// tokens/ 直下に置く。設計工程以降（顧客確認用モック・実装）では使わない。
//
// パスは実行時のカレントディレクトリ（リポジトリルート）からの相対。
export default {
  source: [
    "tokens/primitive.json",
    "tokens/semantic.json",
    "tokens/semantic.wireframe.json"
  ],
  platforms: {
    css: {
      transformGroup: "css",
      buildPath: "tokens/dist/wireframe/",
      files: [{ destination: "tokens.css", format: "css/variables" }]
    },
    ts: {
      transformGroup: "js",
      buildPath: "tokens/dist/wireframe/",
      files: [{ destination: "theme.ts", format: "javascript/es6" }]
    },
    // Claude Design の /design-sync に食わせる用（中身は css と同一でよい）
    claudeDesign: {
      transformGroup: "css",
      buildPath: "tokens/dist/wireframe/",
      files: [{ destination: "theme-claude-design.css", format: "css/variables" }]
    }
  }
};
