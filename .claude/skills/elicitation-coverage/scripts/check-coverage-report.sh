#!/bin/bash
# =============================================================================
# check-coverage-report.sh — coverage_report の出力契約 R1〜R8 機械照合器
#（elicitation-coverage-pack §2.2 の決定論検査。WP8段階1実測ラン用）
#
# 用法:
#   check-coverage-report.sh -i <期待ID一覧ファイル(1行1ID)> -c <期待compiled_from文字列> \
#                            [-m <入力材料ファイル(evidence節参照の実在検査)>] <report.yaml>
#
# 検査: R1全件性（一意ID数=期待数・重複なし）／R2 ID整合（集合一致）／R3 enum 3値／
#       R4 条件必須（covered→evidence, uncovered→question, n/a→na_reason）／
#       R5 排他（coveredにquestion禁止・n/aにevidence/question禁止）／
#       R6 層別（C02-DEL-*→c02, F09-Q-*→f09）／R7 compiled_from転記一致／
#       R8 処理経路（uncovered→routing 必須・4値enum／uncovered以外はnull）／
#       H5 f09由来uncovered(ask-customer)のquestionに「参考質問」付記／
#       EV evidence中の §n 参照が材料に実在（-m 指定時のみ）
# 期待するreport形式: 契約§2.1のYAML（フラットなkey: value行。items配下は "- item_id:" 開始）
# 終了コード: 0=全適合 / 1=違反あり / 2=入力エラー
# 依存: bash + perl
# =============================================================================
set -u

IDS=""; COMPILED=""; MATERIAL=""
while getopts "i:c:m:h" opt; do
  case "$opt" in
    i) IDS="$OPTARG" ;;
    c) COMPILED="$OPTARG" ;;
    m) MATERIAL="$OPTARG" ;;
    *) echo "用法: $(basename "$0") -i ids.txt -c compiled_from [-m material.md] report.yaml" >&2; exit 2 ;;
  esac
done
shift $((OPTIND - 1))
REPORT="${1:-}"
[ -f "$IDS" ] && [ -n "$COMPILED" ] && [ -f "$REPORT" ] || { echo "ERROR: 引数不足（-i/-c/report必須）" >&2; exit 2; }

perl -CSD -Mutf8 -e '
  my ($idsf, $compiled, $material, $report) = @ARGV;
  my (%expect, @viol);
  open(my $if, "<:utf8", $idsf) or die; while (<$if>) { chomp; s/\r$//; $expect{$_}=1 if $_ ne "" } close $if;
  my $nexp = scalar keys %expect;

  my %mat_secs;
  if ($material ne "-") {
    open(my $mf, "<:utf8", $material) or die "material open: $!";
    while (<$mf>) { $mat_secs{$1}=1 while /(§\d+(?:[-.]\d+)?)/g }
    close $mf;
  }

  open(my $rf, "<:utf8", $report) or die "report open: $!";
  my ($in_items, $pcf, @entries, $cur) = (0, "");
  while (<$rf>) {
    chomp; s/\r$//;
    $pcf = $1 if /^\s*pack_compiled_from:\s*"?(.*?)"?\s*$/ && !$in_items;
    $in_items = 1 if /^\s*items:\s*$/;
    next unless $in_items;
    if (/^\s*-\s*item_id:\s*"?([^"]*?)"?\s*(#.*)?$/) { $cur = { item_id => $1 }; push @entries, $cur; next }
    if ($cur && /^\s*(verdict|evidence|question|na_reason|source_block|routing):\s*(.*?)\s*(#.*)?$/) {
      my ($k, $v) = ($1, $2);
      $v =~ s/^"//; $v =~ s/"$//;
      $cur->{$k} = $v;
    }
  }
  close $rf;

  # R7
  push @viol, "R7: pack_compiled_from 不一致: got=\"$pcf\" want=\"$compiled\"" unless $pcf eq $compiled;

  # R1/R2
  my (%seen, %dup);
  for my $e (@entries) { $dup{$e->{item_id}}++ if $seen{$e->{item_id}}++; }
  my $nuniq = scalar keys %seen;
  push @viol, "R1: 重複ID: $_（${\ ($dup{$_}+1)}回）" for sort keys %dup;
  push @viol, "R1: 一意ID数 $nuniq ≠ 注入観点数 $nexp" if $nuniq != $nexp;
  for my $id (sort keys %seen)   { push @viol, "R2: 注入集合に無いID（発明/改変）: $id" unless $expect{$id} }
  for my $id (sort keys %expect) { push @viol, "R2: 欠落ID: $id" unless $seen{$id} }

  my $n = 0;
  for my $e (@entries) {
    $n++;
    my $id = $e->{item_id} // "(no-id)";
    my $v  = $e->{verdict} // "";
    my $isnull = sub { my $x = shift // "null"; return ($x eq "null" || $x eq "~" || $x eq "") ? 1 : 0 };
    # R3
    unless ($v =~ /^(covered|uncovered|not_applicable)$/) { push @viol, "R3: $id verdict不正: \"$v\""; next }
    # R4
    push @viol, "R4: $id covered だが evidence 空"        if $v eq "covered"        && $isnull->($e->{evidence});
    push @viol, "R4: $id uncovered だが question 空"      if $v eq "uncovered"      && $isnull->($e->{question});
    push @viol, "R4: $id not_applicable だが na_reason 空" if $v eq "not_applicable" && $isnull->($e->{na_reason});
    # R5
    push @viol, "R5: $id covered に question 記載"        if $v eq "covered" && !$isnull->($e->{question});
    push @viol, "R5: $id not_applicable に evidence 記載" if $v eq "not_applicable" && !$isnull->($e->{evidence});
    push @viol, "R5: $id not_applicable に question 記載" if $v eq "not_applicable" && !$isnull->($e->{question});
    # R6
    my $want_block = $id =~ /^C02-DEL-/ ? "c02" : $id =~ /^F09-Q-/ ? "f09" : "?";
    push @viol, "R6: $id source_block=\"$e->{source_block}\" ≠ 由来 \"$want_block\""
      if ($e->{source_block} // "") ne $want_block;
    # R8 処理経路（2026-08-03 追加・締める変更）: uncovered の宛先を明示させる。
    #    uncovered を一律「顧客への質問」に整形すると、弊社内で決める事項や
    #    LLM が下書きできる事項まで顧客質問として数えられ、件数が実態から乖離するため。
    if ($v eq "uncovered") {
      my $r = $e->{routing} // "";
      push @viol, "R8: $id uncovered だが routing 空（ask-customer|request-material|internal-decide|draft-then-confirm）"
        if $isnull->($r);
      push @viol, "R8: $id routing 不正: \"$r\""
        if !$isnull->($r) && $r !~ /^(ask-customer|request-material|internal-decide|draft-then-confirm)$/;
    } else {
      push @viol, "R8: $id verdict=$v に routing 記載（uncovered 以外は null）"
        unless $isnull->($e->{routing});
    }
    # H5（routing=ask-customer のときのみ。弊社内タスク・資料請求・下書きには参考質問の付記を求めない）
    push @viol, "H5: $id f09由来uncovered(ask-customer)のquestionに「参考質問」付記なし"
      if $want_block eq "f09" && $v eq "uncovered" && ($e->{routing} // "") eq "ask-customer"
         && !$isnull->($e->{question}) && $e->{question} !~ /参考質問/;
    # EV
    if ($material ne "-" && $v eq "covered" && !$isnull->($e->{evidence})) {
      for my $sec ($e->{evidence} =~ /(§\d+(?:[-.]\d+)?)/g) {
        push @viol, "EV: $id evidence参照 $sec が材料に実在しない" unless $mat_secs{$sec};
      }
    }
  }

  if (@viol) { print "VIOLATION: $_\n" for @viol; print "NG (violations=" . scalar(@viol) . ", entries=$n)\n"; exit 1 }
  print "OK: R1-R8適合 entries=$n uniq=$nuniq expected=$nexp compiled_from一致\n";
  exit 0;
' "$IDS" "$COMPILED" "${MATERIAL:--}" "$REPORT"
