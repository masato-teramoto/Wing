#!/usr/bin/env python3
"""Prepare an extracted trial at its final location, then open Claude Code."""
import argparse
import json
from pathlib import Path
import shutil
import subprocess
import sys


ROOT = Path(__file__).resolve().parent


def run(script, *arguments):
    return subprocess.run(
        [sys.executable, '-X', 'utf8', '-B', '-S', str(ROOT / script), *arguments],
        cwd=ROOT,
        check=True,
    )


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--prepare-only', action='store_true',
                        help='prepare/check the workspace without opening the CLI')
    args = parser.parse_args()
    if sys.version_info < (3, 10):
        parser.error('Use Python 3.10 or newer for this trial launcher.')
    try:
        git = shutil.which('git')
        if not git:
            raise ValueError('Gitが見つかりません。Gitを導入してから同じフォルダで再実行してください。')
        if not (ROOT / '.git').exists():
            subprocess.run([git, 'init', '--quiet', str(ROOT)], cwd=ROOT, check=True)
            print('この案件専用のローカルGitを初期化しました。コミット・リモート登録・pushは行いません。', flush=True)
        repository = subprocess.run([git, 'rev-parse', '--show-toplevel'], cwd=ROOT,
                                    check=True, capture_output=True, encoding='utf-8')
        if Path(repository.stdout.strip()).resolve() != ROOT:
            raise ValueError('Gitのルートが案件フォルダと一致しません。新しい展開先を使用してください。')
        phase8 = (ROOT / 'phase8-sample/prepare.py').is_file()
        resumed = False
        if phase8:
            record = ROOT / '.aidd/phase8-sample/preparation.json'
            state = json.loads(record.read_text(encoding='utf-8')) if record.exists() else None
            if state is not None:
                if state.get('root') != str(ROOT) or state.get('synthetic') is not True:
                    raise ValueError('準備済みフォルダは移動できません。元ZIPを新しい場所に展開してください。')
                resumed = state.get('ready') is True
            if not resumed:
                print('実装開始用の題材を準備します。Phase 1〜7の検査・承認はテスト専用の合成データです。', flush=True)
                print('数分かかります。実装コードやPhase 8の承認は作成しません。', flush=True)
                run('phase8-sample/prepare.py')
            else:
                print('同じ場所の準備済み環境を使用します。実装中の状態は初期化しません。', flush=True)
        run('aidd-run.py', 'doctor', '--runtime-only')
        print('\n準備できました。Claude Codeで開くフォルダ:\n' + str(ROOT), flush=True)
        if phase8:
            print('初回の入力: 同梱題材の合成入力による試行を行います。', flush=True)
            print('続けて: /aidd-implement reservation-window 1', flush=True)
            print('準備タスク1の導入範囲は specs/reservation-window/tasks.md を確認してください。', flush=True)
        else:
            print('初回の入力: /aidd-requirements-init', flush=True)
        print('途中から再開する場合は、同じ入口と保存された要求の続きを使ってください。', flush=True)
        if args.prepare_only:
            return 0
        claude = shutil.which('claude')
        if claude:
            return subprocess.call([claude], cwd=ROOT)
        print('Claude Code CLIがPATHにありません。Claude Code拡張で上のフォルダを開いて開始できます。', flush=True)
        return 0
    except (OSError, ValueError, subprocess.CalledProcessError) as error:
        print('開始準備に失敗しました: ' + str(error), file=sys.stderr)
        print('同じフォルダで再実行できます。状態ファイルを削除せず、エラーを確認してください。', file=sys.stderr)
        return 1


if __name__ == '__main__':
    raise SystemExit(main())
