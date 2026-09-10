// 生成したトークン CSS を DS のトークン JSON と突き合わせる
// （wireframe-authoring 手順 3 の完了条件 / wireframe-integration 手順 4 の複製前チェック）。
//
//   node check-tokens.mjs <DS の所在> <検査対象> [--profile <名前>] [--json]
//   例: node .claude\skills\wireframe-authoring\scripts\check-tokens.mjs test\work\ds ^
//         test\work\.aidd\wireframe
//       node .claude\skills\wireframe-authoring\scripts\check-tokens.mjs ds ^
//         .aidd\wireframe\loan-request-review\pages\tokens\tokens.css
//
//   <DS の所在> … DS clone のルート（tokens/*.json を読む。DS は読むだけで一切変更しない）
//   <検査対象>  … 生成した tokens.css 1 本、または配下を再帰探索するルート
//                 （ディレクトリを渡すと配下の tokens.css を全部拾う = 全 feature 一括検査）
//   --profile   … 既定 wireframe。source 順は
//                 primitive.json → semantic.json → semantic.<プロファイル>.json
//                 （定義の正は DS の tokens/config.<プロファイル>.mjs）
//
// 検査するのは 3 つ:
//   ① 値の一致       — 生成物の各変数を（生成物自身の定義で var() を再帰解決したうえで）
//                      DS の解決値と突き合わせる。未定義の var() 参照・循環参照・
//                      同名の重複定義も違反として数える
//   ② キーの網羅     — DS にあって生成物に無いキー（部分集合になっている = 全キー出力の違反）と、
//                      生成物にあって DS に無いキー（値の創作）を両方見る
//   ③ feature 間の同一性 — 対象が複数見つかった場合、全ファイルの宣言が一致するか
//                      （割れているファイルと差分キーを列挙する）
//
// 検査しないもの: CSS としての妥当性・実際の見た目・「どの変数が画面で使われているか」
//   （使用の有無でキーを絞らないのが本工程の生成仕様 — wireframe-authoring 手順 3 ②）。
//   コメント・宣言の並び順は比較対象外（③ は「変数名 → 値」の集合で比べる）。
//
// **exit code で合否を出す**（違反 0 件 = 0 / 違反あり = 1 / 使い方の誤り = 2）。
// 同じ工程の道具でも check-links.mjs（wireframe-integration 同梱）は「数えるだけ・常に exit 0」
// で合否を Skill 手順側に委ねるが、本スクリプトは「DS の値と一致するか否か」という
// 答えの決まった一致検査なので、ここで判定する（監査スクリプトと同じ扱いにできる）。
// なお tokens/ は audit-tokens.mjs / audit-components.mjs の SKIP_DIRS に入っており
// 監査では検出できない — その穴を埋めるのが本スクリプトの役割。
import { existsSync, readdirSync, readFileSync, statSync } from "node:fs";
import { basename, join, relative, resolve, sep } from "node:path";

const SKIP_DIRS = new Set(["node_modules", ".git", "ds", "dist"]);
const TOKENS_CSS = "tokens.css";

// --- DS 側: DTCG 風 JSON の読み込みと解決 ---------------------------------

// `$` 始まりのキーはメタ。`$value` を持つノードがトークン。
// キーのパス（color.semantic.background）をそのまま識別子にする。
function flattenTokens(node, path, out) {
  for (const [key, value] of Object.entries(node)) {
    if (key.startsWith("$")) continue;
    if (value === null || typeof value !== "object" || Array.isArray(value)) continue;
    if (Object.prototype.hasOwnProperty.call(value, "$value")) {
      out.set([...path, key].join("."), String(value.$value));
      continue;
    }
    flattenTokens(value, [...path, key], out);
  }
}

const DS_REF = /\{([^{}]+)\}/g;

// {color.primitive.gray.700} 形式の参照を再帰解決する。
function resolveDsValue(key, raw, raws, cache, chain) {
  if (cache.has(key)) return cache.get(key);
  if (chain.includes(key)) {
    const r = { error: `循環参照: ${[...chain, key].join(" → ")}` };
    cache.set(key, r);
    return r;
  }
  let error = null;
  const value = raw.replace(DS_REF, (_m, ref) => {
    const target = ref.trim();
    if (!raws.has(target)) {
      error ??= `未解決の参照 {${target}}`;
      return _m;
    }
    const r = resolveDsValue(target, raws.get(target), raws, cache, [...chain, key]);
    if (r.error) {
      error ??= r.error;
      return _m;
    }
    return r.value;
  });
  const result = error ? { error } : { value };
  cache.set(key, result);
  return result;
}

// CSS 変数名 = キーのドットをハイフンに落としたもの
const cssName = (key) => `--${key.replace(/\./g, "-")}`;

function loadDs(dsRootArg, profile) {
  const dsRoot = resolve(dsRootArg);
  const tokensDir = join(dsRoot, "tokens");
  if (!existsSync(tokensDir)) {
    fail(`DS の tokens/ が見つからない: ${tokensDir}（<DS の所在> は DS clone のルートを渡す）`);
  }
  // source 順 = tokens/config.<プロファイル>.mjs の source（後勝ち = オーバーレイ）
  const sources = [join(tokensDir, "primitive.json"), join(tokensDir, "semantic.json")];
  const overlay = join(tokensDir, `semantic.${profile}.json`);
  if (existsSync(overlay)) {
    sources.push(overlay);
  } else if (profile !== "base") {
    fail(`プロファイル "${profile}" の source が見つからない: ${overlay}`);
  }

  const raws = new Map();
  for (const file of sources) {
    if (!existsSync(file)) fail(`DS の source が見つからない: ${file}`);
    let json;
    try {
      json = JSON.parse(readFileSync(file, "utf8"));
    } catch (e) {
      fail(`DS の source を JSON として読めない: ${file}（${e.message}）`);
    }
    const one = new Map();
    flattenTokens(json, [], one);
    for (const [key, value] of one) raws.set(key, value); // 後から読んだ source が上書き
  }

  const cache = new Map();
  const values = new Map(); // CSS 変数名 -> 解決値
  const unresolved = [];
  for (const [key, raw] of raws) {
    const r = resolveDsValue(key, raw, raws, cache, []);
    if (r.error) {
      unresolved.push({ key, detail: r.error });
      continue;
    }
    values.set(cssName(key), r.value);
  }
  return { dsRoot, sources, values, unresolved };
}

// --- 生成物側: CSS の宣言の読み取りと解決 ---------------------------------

const DECL = /(--[A-Za-z0-9_-]+)\s*:\s*([^;{}]*)(?=[;}])/g;
const VAR_ONLY = /^var\(\s*(--[A-Za-z0-9_-]+)\s*(?:,([\s\S]*))?\)$/;

function parseCss(text) {
  const src = text.replace(/\/\*[\s\S]*?\*\//g, " "); // コメントは比較対象外
  const decls = new Map(); // 変数名 -> 宣言された値（正規化前）
  const duplicated = [];
  for (const m of src.matchAll(DECL)) {
    const name = m[1];
    const value = m[2].trim().replace(/\s+/g, " ");
    if (decls.has(name) && !duplicated.includes(name)) duplicated.push(name);
    decls.set(name, value); // CSS の後勝ちに合わせる
  }
  return { decls, duplicated };
}

// 生成物自身の定義で var() を再帰解決する。fallback は使わない
// （未定義参照を fallback で隠すと「DS と一致しているか」が確かめられなくなるため違反にする）。
function resolveCssValue(name, decls, cache, chain) {
  if (cache.has(name)) return cache.get(name);
  if (chain.includes(name)) {
    const r = { error: `循環参照: ${[...chain, name].join(" → ")}` };
    cache.set(name, r);
    return r;
  }
  const raw = decls.get(name);
  if (raw === undefined) {
    const r = { error: `未定義の変数 ${name}` };
    cache.set(name, r);
    return r;
  }
  const m = VAR_ONLY.exec(raw);
  if (!m) {
    const r = { value: raw };
    cache.set(name, r);
    return r;
  }
  const inner = resolveCssValue(m[1], decls, cache, [...chain, name]);
  const r = inner.error
    ? { error: inner.error === `未定義の変数 ${m[1]}` ? `未定義の参照 var(${m[1]})` : inner.error }
    : { value: inner.value };
  cache.set(name, r);
  return r;
}

// 色の大文字小文字と hex の短縮形を正規化して比較する
function normalize(value) {
  const s = value.trim().replace(/\s+/g, " ").toLowerCase();
  const m = /^#([0-9a-f]{3}|[0-9a-f]{4})$/.exec(s);
  if (m) return `#${[...m[1]].map((c) => c + c).join("")}`;
  return s;
}

// --- 検査対象の収集 -------------------------------------------------------

function collectTargets(targetArg) {
  const target = resolve(targetArg);
  if (!existsSync(target)) fail(`検査対象が見つからない: ${targetArg}`);
  if (!statSync(target).isDirectory()) return [target];
  const found = [];
  const walk = (dir) => {
    for (const name of readdirSync(dir)) {
      const p = join(dir, name);
      if (statSync(p).isDirectory()) {
        if (!SKIP_DIRS.has(name)) walk(p);
        continue;
      }
      if (name === TOKENS_CSS) found.push(p);
    }
  };
  walk(target);
  return found.sort();
}

// --- 検査本体 -------------------------------------------------------------

function checkFile(path, ds, label) {
  const { decls, duplicated } = parseCss(readFileSync(path, "utf8"));
  const cache = new Map();

  const mismatched = [];
  const unresolved = [];
  const missing = [];
  const extra = [];

  // ② キーの網羅（DS 側にあって生成物に無い / 生成物にあって DS に無い）
  for (const name of ds.values.keys()) if (!decls.has(name)) missing.push(name);
  for (const name of decls.keys()) if (!ds.values.has(name)) extra.push(name);

  // ① 値の一致（両方にあるキーのみ。片側だけのキーは ② で数える）
  for (const [name, expected] of ds.values) {
    if (!decls.has(name)) continue;
    const actual = resolveCssValue(name, decls, cache, []);
    if (actual.error) {
      unresolved.push({ name, declared: decls.get(name), detail: actual.error });
      continue;
    }
    if (normalize(actual.value) !== normalize(expected)) {
      mismatched.push({ name, expected, actual: actual.value, declared: decls.get(name) });
    }
  }
  // DS に無いキーも参照が解決するかだけは見る（未定義参照の見落としを防ぐ）
  for (const name of extra) {
    const actual = resolveCssValue(name, decls, cache, []);
    if (actual.error) unresolved.push({ name, declared: decls.get(name), detail: actual.error });
  }

  const violations =
    mismatched.length + unresolved.length + missing.length + extra.length + duplicated.length;

  return {
    path,
    label,
    declarations: decls.size,
    decls,
    mismatched,
    unresolved,
    missing: missing.sort(),
    extra: extra.sort(),
    duplicated,
    violations,
  };
}

// ③ feature 間の同一性: 変数名 → 宣言値（正規化）の集合で比べる
function checkIdentity(files) {
  if (files.length < 2) return null;
  const ref = files[0];
  const diverged = [];
  for (const f of files.slice(1)) {
    const onlyInReference = [];
    const onlyInFile = [];
    const differentValue = [];
    for (const [name, value] of ref.decls) {
      if (!f.decls.has(name)) onlyInReference.push(name);
      else if (normalize(f.decls.get(name)) !== normalize(value)) {
        differentValue.push({ name, reference: value, file: f.decls.get(name) });
      }
    }
    for (const name of f.decls.keys()) if (!ref.decls.has(name)) onlyInFile.push(name);
    if (onlyInReference.length + onlyInFile.length + differentValue.length > 0) {
      diverged.push({
        label: f.label,
        onlyInReference: onlyInReference.sort(),
        onlyInFile: onlyInFile.sort(),
        differentValue,
      });
    }
  }
  return { reference: ref.label, compared: files.length, diverged };
}

// --- 出力 -----------------------------------------------------------------

function report(r) {
  console.log(
    `\n=== トークン CSS 検査: ${r.target} （${r.files.length} ファイル / プロファイル ${r.profile}） ===`,
  );
  console.log(`DS: ${r.ds} — source ${r.sources.join(" → ")}`);
  console.log(`DS のキー数: ${r.dsKeys}`);
  if (r.dsUnresolved.length > 0) {
    console.log(`\n! DS 側で解決できないトークン ${r.dsUnresolved.length} 件（DS の問題 — 生成物の違反ではない）:`);
    for (const u of r.dsUnresolved) console.log(`  - ${u.key}: ${u.detail}`);
  }

  for (const f of r.files) {
    console.log(`\n--- ${f.label} （宣言 ${f.declarations} 件 / 違反 ${f.violations} 件） ---`);
    if (f.violations === 0) {
      console.log("  OK: 全キーが DS の解決値と一致");
      continue;
    }
    if (f.mismatched.length > 0) {
      console.log(`  ① 値の不一致 ${f.mismatched.length} 件:`);
      for (const m of f.mismatched) {
        console.log(`    - ${m.name}: DS "${m.expected}" ≠ 生成物 "${m.actual}"（宣言: ${m.declared}）`);
      }
    }
    if (f.unresolved.length > 0) {
      console.log(`  ① 解決できない参照 ${f.unresolved.length} 件:`);
      for (const u of f.unresolved) console.log(`    - ${u.name}: ${u.detail}（宣言: ${u.declared}）`);
    }
    if (f.duplicated.length > 0) {
      console.log(`  ① 同名の重複定義 ${f.duplicated.length} 件: ${f.duplicated.join(" / ")}`);
    }
    if (f.missing.length > 0) {
      console.log(
        `  ② DS にあって生成物に無いキー ${f.missing.length} 件（全キー出力の違反 — 使用の有無でキーを絞らない）:`,
      );
      for (const n of f.missing) console.log(`    - ${n}`);
    }
    if (f.extra.length > 0) {
      console.log(`  ② DS に無いキー ${f.extra.length} 件（値の創作 — DS に無い値を足さない）:`);
      for (const n of f.extra) console.log(`    - ${n}`);
    }
  }

  if (!r.identity) {
    console.log("\n③ feature 間の同一性: 対象が 1 ファイルのためスキップ");
  } else if (r.identity.diverged.length === 0) {
    console.log(`\n③ feature 間の同一性: ${r.identity.compared} ファイルすべて同一内容`);
  } else {
    console.log(
      `\n③ feature 間の同一性: ${r.identity.diverged.length} ファイルが基準（${r.identity.reference}）と割れている`,
    );
    for (const d of r.identity.diverged) {
      console.log(`  - ${d.label}`);
      if (d.onlyInReference.length > 0) {
        console.log(`      基準にのみ存在 ${d.onlyInReference.length}: ${d.onlyInReference.join(" / ")}`);
      }
      if (d.onlyInFile.length > 0) {
        console.log(`      このファイルにのみ存在 ${d.onlyInFile.length}: ${d.onlyInFile.join(" / ")}`);
      }
      for (const v of d.differentValue) {
        console.log(`      値違い ${v.name}: 基準 "${v.reference}" ≠ "${v.file}"`);
      }
    }
  }

  console.log(`\n合計違反: ${r.violations} 件`);
  console.log(
    r.violations === 0
      ? "OK: DS の解決結果と全キー・全値が一致（feature 間も同一）"
      : "NG: 生成し直す（DS のファイルは編集しない・DS に無い値を足さない）",
  );
}

function fail(message) {
  console.error(`エラー: ${message}`);
  process.exit(2);
}

// --- 引数 -----------------------------------------------------------------

const argv = process.argv.slice(2);
const asJson = argv.includes("--json");
const profileIdx = argv.indexOf("--profile");
const profileValueIdx = profileIdx >= 0 ? profileIdx + 1 : -1;
const profile = profileValueIdx >= 0 ? argv[profileValueIdx] : "wireframe";
const positional = argv.filter((a, i) => !a.startsWith("--") && i !== profileValueIdx);

if (positional.length !== 2 || !profile) {
  console.error(
    "使い方: node check-tokens.mjs <DS の所在> <検査対象> [--profile <名前>] [--json]",
  );
  process.exit(2);
}

const ds = loadDs(positional[0], profile);
const targets = collectTargets(positional[1]);
if (targets.length === 0) {
  fail(`検査対象の ${TOKENS_CSS} が見つからない: ${resolve(positional[1])}`);
}

const targetRoot = resolve(positional[1]);
const labelOf = (p) => {
  const rel = relative(targetRoot, p);
  return rel && !rel.startsWith("..") ? rel : basename(p);
};
const files = targets.map((p) => checkFile(p, ds, labelOf(p)));
const identity = checkIdentity(files);

const violations =
  files.reduce((n, f) => n + f.violations, 0) + (identity ? identity.diverged.length : 0);

const result = {
  ds: ds.dsRoot,
  profile,
  sources: ds.sources.map((s) => relative(ds.dsRoot, s).split(sep).join("/")),
  target: targetRoot,
  dsKeys: ds.values.size,
  dsUnresolved: ds.unresolved,
  files: files.map(({ decls, ...rest }) => rest),
  identity,
  violations,
  ok: violations === 0,
};

if (asJson) {
  console.log(JSON.stringify(result, null, 2));
} else {
  report({ ...result, files });
}
process.exit(violations === 0 ? 0 : 1);
