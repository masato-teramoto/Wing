# Docs 統合の作成規則

- 承認済みfeature集合に含まれる全requirementsとdesign、およびsteeringが入力。Globで偶然見つかったファイルだけを分母にしない。tasksは入力にしない。
- featureごとにdesignのエンティティ／属性／関連、コード値／区分値／採番対象、コンポーネントと接続を抽出する。主要フローをrequirementsで補う。全specを一度に読み込まず抽出結果を積み上げる。
- feature間で同名のコード・エンティティが別形状になっていれば、両方の出典と形状を提示する。人間が正を決めるまでdocsへ採用しない。推測で統合せず、両形状や未解決のTBDを完成品へ残さない。
- 競合・欠落は不一致の design を所有者とする差戻し候補（`owner: design`、`target` に該当 `specs/<feature>/design.md`、要素・両形状・出典）として返し、waiting で docs 統合を保留する。人間が正形状を答えても、不一致 design が修正・再承認されるまで当該要素を docs へ採用しない。steeringのルール不足も同様に差戻し候補を返す。上流を直接編集・降格しない。再開時は変更した入力のハッシュを確認し、変わったfeatureの抽出だけをやり直す。以前の抽出結果の鮮度が分からなければ再抽出する。
- steering の設計ルール不足を Phase 2 へ返す場合は、そのルールに依存する design の洗い出しと再確認が必要である旨も添える。判明済みの影響 design・箇所と、未確認の範囲を区別して伝える。
- 作成順はcode-design → architecture/data-model → architecture/system-overview。code-designは業務コード・区分値・採番の集約であり、ソースコード設計ではない。
- 設計ルールはsteering、featureの実体定義はdesign、全体の集約はdocsが所有する。同じ事実をsteeringとdocsに再定義しない。
