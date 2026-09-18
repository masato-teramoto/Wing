# 記入例: 実装計画とタスク間の受け渡し

**説明専用・未実行。** [要件例](requirements.md)を入力とする架空の計画である。
例の依頼条件として、TypeScriptで実装し、次のパスをすべて新規作成先に決めた設定とする。
実在するリポジトリのパス確認や、作成済みファイルを意味しない。実案件では対象構造を確認してから決める。

タスクIDの母集合は **TASK-01、TASK-02の2件**。依存はTASK-02 → TASK-01のみ。
データ・API・画面の技術層ごとに分けず、TASK-01で利用者が一機能を試せる範囲をまとめる。

## TASK-01: 選んだ本を既読にし、反復・不明IDでも状態を保つ

- **要求参照**: FR-01、FR-02、FR-03、NFR-02。
- **作成先**: `src/bookshelf.ts`、`src/bookshelf-page.ts`、`public/bookshelf.html`、`tests/bookshelf-behavior.spec.ts`。
  親ディレクトリ`src/`、`public/`、`tests/`も作成対象に含める。
- **入力データ**: `{id: 'b1', title: 'サンプルの本A', isRead: false}` と
  `{id: 'b2', title: 'サンプルの本B', isRead: false}`。不明IDは`missing-book`。
- **作業**: 本の一覧・既読操作・既読表示を一緒に実装する。対象だけを既読にし、既読対象への反復では値を
  変えず、不明IDでは理由を表示して操作前の値を返す。操作情報を外部へ送らない。正常・反復・不明IDと
  通信の観測を[検証仕様](verification-spec.md)のCHECK-01〜04に対応させる。
- **Consumes**: 先行タスクなし。上記の初期データと要件例の5件を入力とする。
- **Produces**: `src/bookshelf.ts`で以下の型・関数を公開し、画面と後続の性能確認が同じ定義を使う。

```ts
export type Book = { id: string; title: string; isRead: boolean };
export type MarkReadResult =
  | { ok: true; books: Book[] }
  | { ok: false; reason: 'not_found'; books: Book[] };
export function markRead(books: readonly Book[], bookId: string): MarkReadResult;
```

成功時も失敗時も入力配列の内容を変更せず、結果の配列を返す。画面は成功時の配列で表示を更新し、
失敗時は理由を表示する。このシグネチャは例の設計上の決定であり、要件本文に内部実装を要求したものではない。

- **完了の確認**: CHECK-01〜04の期待結果を観測し、対象・方法・結果を残す。現時点ではすべて未実施。
- **引き渡すもの**: 上記の公開型・関数と画面。性能基準の達成はTASK-02で確認するため、ここで全機能完成とは宣言しない。

## TASK-02: 操作の表示応答時間を測り、例の基準へ収める

- **要求参照**: NFR-01。変更した場合の回帰確認対象はFR-01、FR-02、FR-03、NFR-02。
- **先行条件**: TASK-01の出力が利用できること。未来のタスクの出力は前提にしない。
- **作成先**: `tests/bookshelf-performance.spec.ts`、`reports/bookshelf-performance.json`。
  `reports/`の作成を含める。必要な調整先はTASK-01で作る`src/bookshelf.ts`と`src/bookshelf-page.ts`。
- **Consumes**: TASK-01の`Book`、`MarkReadResult`と、
  `markRead(books: readonly Book[], bookId: string): MarkReadResult`。画面の操作開始と対象行表示を観測する。
- **作業**: CHECK-05の条件で性能を測る。必要な調整を行った場合は、対象だけを既読にする挙動、反復・
  不明IDの結果、外部送信がないこともCHECK-01〜04で再確認する。回帰確認だけを性能達成の代わりにしない。
- **Produces**: `reports/bookshelf-performance.json`に
  `environment: string`、`bookCount: number`、`runs: {durationsMs: number[]; p95Ms: number}[]`を残す。
  実測前にこのファイルや値を生成済みと扱わない。入力関数の名前・引数・返り値型はTASK-01と一致させる。
- **完了の確認**: 要件例の測定条件に従い、各回のp95と個別値を突合する。期待未達や測定不能はそのまま報告する。
  現時点では測定・調整とも未実施。

## 計画作成時の自己確認

FR-01・FR-02・FR-03・NFR-02はTASK-01、NFR-01はTASK-02に明示参照がある。各タスクは対象、作業、
確認、受取・提供を持つ。これは計画文面の確認であって実装済みの証拠ではない。
対応を表として読む場合は[被覆6表](traceability-complete.md)を参照する。
