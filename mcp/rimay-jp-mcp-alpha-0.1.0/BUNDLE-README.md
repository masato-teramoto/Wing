# Rimay-JP MCP alpha 内部検証bundle

このディレクトリはprivate環境での内部検証専用です。同梱固定Grammarの原典には
ライセンス許諾がないため、公開・第三者配布・一般配布を行わないでください。

## セットアップ

1. Python 3.12以上を使用します。
2. `python -m pip install -r requirements.txt`を実行します。
3. このディレクトリをClaude Codeのprojectとして開きます。`.mcp.json`により
   `rimay-jp` stdio MCPサーバーが自動起動します。
4. 日本語要件の検査・壁打ちは`/rimay-spec-alpha-check`を手動実行します。
5. `python prototype/rimay-jp/adapters/mcp/smoke_test.py`で、44 MCPツールと
   同梱固定Grammarを検証できます。

`RIMAY_FIXED_GRAMMAR`は任意で、同梱Grammarを別実体で上書きするときだけ使います。
上書き先が存在しない場合やhash不一致はfail-closedになります。配布内容の正確な一覧は
`bundle-manifest.json`と`SHA256SUMS`に記録されています。beta以降は外部提供MCPへ
切り替え、このローカルサーバーとGrammar bundleを除去します。
