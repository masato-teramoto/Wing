#!/usr/bin/env bash
# dsmock 削除スクリプト（ワークスペース直下に置いて実行する）
#
# 使い方: ./remove_dsmock.sh
#
# 流れ:
#   1. ワークスペース（このスクリプトのあるフォルダ）内を探索し、dsmock の配置場所を特定する
#      （dsmock の全ファイルの SHA-256 をこのスクリプトに埋め込んであり、内容が一致するファイルで判定。
#        README など名前が共通のファイルも、内容が違えば別物として扱う）
#   2. 候補ごとに、dsmock の一部が別の場所へ移動されていないか・余分なファイルがないかを確認して表示
#   3. 実行者が承認した場合のみ削除する
#      ・子フォルダに配置されている場合: フォルダごと削除（フォルダのパスを入力して承認）
#      ・ws 直下に展開されている場合: 内容が一致したファイルだけを個別に削除（delete-files と入力して承認）
#
# 前提: bash / find / sha256sum が使えること（Linux, WSL, Git Bash）
set -euo pipefail
export LC_ALL=C

THRESHOLD=50   # 埋め込みファイルのうち内容一致が何%以上なら dsmock の候補とするか

ws="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd -P)"

# ---- dsmock の全ファイル（SHA-256 <TAB> 相対パス）。Zone.Identifier は除外 ----
read -r -d '' MANIFEST <<'MANIFEST_EOF' || true
58cdfd89e70f69100d7eec189647c88e18126e2dbf4c6c9c01323e0492bb618a	.claude/hooks/block-protected-dirs.mjs
d56a3cd07f987769c432eefa3c013556218a5d9d4bde74250a552f61423b4945	.claude/settings.json
b8f773b461d39d1b655b8591a60ee42a90663728d09027fc880bc0b4528a8b7e	.claude/skills/aidd-system-design/SKILL.md
d0ad96970fff59d8414c5e42ea842e44ed3b63407cccbbb1d19a211a1bf925de	.claude/skills/mockup-authoring/SKILL.md
339661fbf7dc714706b00a7517cfe66454805e4be4defc5a5872b9e46b206798	.claude/skills/mockup-authoring/scripts/check-links.mjs
e1e069737533604f47d7d9dc334181e3f5372d4a77034fe35690d80868887e71	.claude/skills/mockup-authoring/scripts/check-palette.mjs
8ff5511e3d322f33e2a7437375192c2387f45c932c71588e71aa00dce3fbbfc8	.claude/skills/mockup-authoring/templates/mockup-manifest.json
47349efc31acedf7fbdfbecc7121ec76f71e6328d7d23180145463e788c3dfdd	.claude/skills/screen-map-authoring/SKILL.md
6b1206c21115e9d7e2ee9db1000d6b2298fe8c4fafe46ccc37ed96076ac79fc3	.claude/skills/screen-map-authoring/templates/screen-map.md
053c74d14751f2bf2942e3fe246a3a2c532f7b2c88c74b57af400eb23fe405d2	.claude/skills/screen-spec-authoring/SKILL.md
22d23d35a72222d58b6a31f44853f8ca03bc993f0c533b7cacb297da043c6466	.claude/skills/screen-spec-authoring/templates/screen-spec.md
6242309ac33d639783625667d89e7a0ceefeaeeb42df244c0b745a0e610b6493	.claude/skills/styleguide-authoring/SKILL.md
ece8488b6a61d27b42627925782ec1dcfeef4ca70327073a3bf66831f1d0a76f	.claude/skills/styleguide-authoring/presets/wing/README.md
7548fac842ae3d1db5e911c06cf8602f54f07736eaf210ccf72bb4cc82e8ba5d	.claude/skills/styleguide-authoring/presets/wing/STYLEGUIDE-backlog.md
b2fa754c392ef893cd6304df63a71932b5bcddecbb1f22689087163d6baffea5	.claude/skills/styleguide-authoring/presets/wing/STYLEGUIDE.md
64735639fe5e745d9f538dbd49572921b62956e986bd3f5596e4b974fe16af57	.claude/skills/styleguide-authoring/presets/wing/styleguide.css
3e9cdd7a150a9464860773f2744bd81566abf4314c5575baf382bafb1678d4aa	.claude/skills/styleguide-authoring/templates/STYLEGUIDE.md
34c4bf2edc316c095a9b1af43e1ce74fc09d4fea71eae98105d4fb8f649a8df5	.gitignore
e34cceae4a380d4a486c1a1062c9329a19e4b579cd291ace3ea0d261a6b62057	HOW-TO-USE.md
5d8404cf4fd28eee89325ec84bd8300196ecb9382877b195064a6f916c381164	README.md
ded78d63f4afd0ab41b078af8e8e207b2a4c2f286688188af3c1950a75967a72	project.example.json
MANIFEST_EOF

declare -A want        # 相対パス -> 期待ハッシュ
total=0
while IFS=$'\t' read -r h p; do
  [ -n "$p" ] || continue
  want["$p"]="$h"; total=$((total + 1))
done <<<"$MANIFEST"

echo "ワークスペース: $ws"
echo "探索中（dsmock 由来のファイルを内容で照合）..."
echo

# ---- 探索: 相対パスが一致するファイルを列挙し、親を「候補ルート」としてハッシュ照合 ----
declare -A match_count   # 候補ルート -> 一致数
declare -A seen_root
declare -A mismatch      # 候補ルート\t相対パス -> 1（名前は同じだが内容が違う）
for p in "${!want[@]}"; do
  while IFS= read -r -d '' f; do
    root="${f%/$p}"
    seen_root["$root"]=1
    h="$(sha256sum -- "$f" | cut -d' ' -f1)"
    if [ "$h" = "${want[$p]}" ]; then
      match_count["$root"]=$(( ${match_count["$root"]:-0} + 1 ))
    else
      mismatch["$root"$'\t'"$p"]=1
    fi
  done < <(find "$ws" \( -name .git -o -name node_modules \) -prune -o -type f -path "*/$p" -print0 2>/dev/null)
done

candidates=()
for root in "${!match_count[@]}"; do
  mc="${match_count["$root"]}"; pct=$(( mc * 100 / total ))
  if [ "$pct" -ge "$THRESHOLD" ]; then candidates+=("$root"); fi
done

if [ "${#candidates[@]}" -eq 0 ]; then
  echo "dsmock と判定できる場所が見つかりませんでした（一致 ${THRESHOLD}% 以上のフォルダなし）。何も削除しません。"
  exit 0
fi

if [ ! -t 0 ]; then
  echo "エラー: 対話端末ではないため承認できません。削除しません。" >&2
  exit 1
fi

# ---- 候補ごとの確認と承認 ----
deleted=0
mapfile -t sorted_candidates < <(printf '%s\n' "${candidates[@]}" | sort)
for root in "${sorted_candidates[@]}"; do
  rel="${root#"$ws"}"; rel="${rel#/}"; [ -n "$rel" ] || rel="."
  mc="${match_count["$root"]}"; pct=$(( mc * 100 / total ))
  echo "================================================================"
  echo "候補: $rel   （内容一致 ${mc}/$total = ${pct}%）"
  echo "================================================================"

  # 削除してはいけない場所
  if [ "$root" = "$ws" ]; then
    # ws 直下に展開されている場合: フォルダごとは消さず、内容が一致したファイルだけを個別に削除する
    echo "  ! ワークスペース直下に展開されています。フォルダごとは削除せず、"
    echo "    内容が dsmock と一致したファイルだけを個別に削除します（別物・dsmock に無いファイルには触れません）。"
    echo
    del_list=(); keep_list=()
    for p in $(printf '%s\n' "${!want[@]}" | sort); do
      f="$root/$p"
      if [ -f "$f" ] && [ ! -L "$f" ] && [ "$(sha256sum -- "$f" | cut -d' ' -f1)" = "${want[$p]}" ]; then
        del_list+=("$p")
      elif [ -e "$f" ]; then
        keep_list+=("$p")
      fi
    done
    echo "[削除するファイル] ${#del_list[@]} 件（内容が dsmock と完全一致）"
    printf '  %s\n' "${del_list[@]}"
    echo
    echo "[削除しないファイル] ${#keep_list[@]} 件（名前は同じだが内容が dsmock と異なる）"
    if [ "${#keep_list[@]}" -gt 0 ]; then printf '  %s\n' "${keep_list[@]}"; else echo "  なし"; fi
    echo
    if [ "${#del_list[@]}" -eq 0 ]; then echo "削除対象がありません。"; echo; continue; fi
    echo "削除後、空になったフォルダは削除します（他のファイルが残るフォルダは残します）。"
    printf '削除する場合は 次の文字列を入力してください（それ以外はスキップ）\n  delete-files\n> '
    read -r answer
    if [ "$answer" = "delete-files" ]; then
      for p in "${del_list[@]}"; do rm -f -- "$root/$p"; done
      for p in "${del_list[@]}"; do
        d="$(dirname "$p")"
        while [ "$d" != "." ] && rmdir -- "$root/$d" 2>/dev/null; do d="$(dirname "$d")"; done
      done
      echo "削除しました: ${#del_list[@]} ファイル"; deleted=$((deleted + 1))
    else
      echo "スキップしました。"
    fi
    echo; continue
  fi
  if [ -L "$root" ]; then
    echo "  ! シンボリックリンクのため対象外にします。"; echo; continue
  fi
  case "$ws/" in
    "$root"/*) echo "  ! ワークスペースを含むフォルダのため対象外にします。"; echo; continue ;;
  esac

  warn=0
  echo "[確認1] dsmock のファイルの状態"
  for p in $(printf '%s\n' "${!want[@]}" | sort); do
    f="$root/$p"
    if [ ! -f "$f" ]; then
      # この候補に無い -> ワークスペース内の別の場所へ移動されていないか（内容一致で探す）
      moved="$(find "$ws" \( -name .git -o -name node_modules \) -prune -o -type f -name "$(basename "$p")" -print 2>/dev/null \
        | while IFS= read -r c; do
            case "$c" in "$root"/*) continue ;; esac
            [ "$(sha256sum -- "$c" | cut -d' ' -f1)" = "${want[$p]}" ] && echo "${c#"$ws"/}"
          done | head -3)"
      if [ -n "$moved" ]; then
        echo "  移動? $p  -> ここに無く、別の場所に同一内容あり:"; echo "$moved" | sed 's/^/            /'; warn=1
      else
        echo "  欠落  $p  -> ここにも ws 内にも見当たらない"; warn=1
      fi
    elif [ "$(sha256sum -- "$f" | cut -d' ' -f1)" = "${want[$p]}" ]; then
      :  # 一致（一覧が長くなるので表示しない）
    else
      echo "  別物  $p  -> 名前は同じだが内容が dsmock と異なる（編集済み or 別プロジェクトのファイル）"; warn=1
    fi
  done
  [ "$warn" -eq 1 ] || echo "  全ファイルが dsmock と一致"
  echo

  echo "[確認2] dsmock に無い余分なファイル（削除すると失われる）"
  extra="$(find "$root" -type f ! -name '*:Zone.Identifier' -printf '%P\n' 2>/dev/null | sort \
    | while IFS= read -r p; do [ -n "${want[$p]+x}" ] || echo "$p"; done)"
  if [ -n "$extra" ]; then
    echo "$extra" | head -20 | sed 's/^/  /'
    [ "$(echo "$extra" | wc -l)" -le 20 ] || echo "  ...ほか $(( $(echo "$extra" | wc -l) - 20 )) 件"
    warn=1
  else
    echo "  なし"
  fi
  echo

  echo "[確認3] シンボリックリンク・マウントポイント"
  lk=0
  while IFS= read -r -d '' l; do echo "  リンク: ${l#"$root"/} -> $(readlink -f -- "$l")"; lk=1; warn=1; done < <(find "$root" -type l -print0)
  while IFS= read -r -d '' d; do
    if mountpoint -q -- "$d" 2>/dev/null; then echo "  マウント: ${d#"$root"/}"; lk=1; warn=1; fi
  done < <(find "$root" -type d -print0)
  [ "$lk" -eq 1 ] || echo "  なし"
  echo

  echo "削除対象: $root  （$(find "$root" -type f | wc -l) ファイル / $(du -sh -- "$root" | cut -f1)）"
  [ "$warn" -eq 0 ] || echo "警告: 上記に確認が必要な項目があります。内容を確認してから承認してください。"
  printf '削除する場合は 次のパスを入力してください（それ以外はスキップ）\n  %s\n> ' "$rel"
  read -r answer
  if [ "$answer" = "$rel" ]; then
    rm -rf -- "$root"
    echo "削除しました: $rel"; deleted=$((deleted + 1))
  else
    echo "スキップしました。"
  fi
  echo
done

echo "完了: $deleted 件削除しました。"
