#!/usr/bin/env python3
"""MCPサーバー動作確認（ワンコマンド）。

使い方:
  python smoke_test.py

本スクリプトが rimay_jp_mcp.py をstdioで子プロセス起動し、
initialize → 44 tools/list → lookup_termを実行する。さらに同梱固定Grammarで
Repository capability、日本語alpha一括検査、redacted observationまで実施して
結果を表示する。
Claude Code登録前の環境検証用（登録後の事前起動は不要＝Claude Codeが自動起動する）。
"""
import json
import subprocess
import sys
from pathlib import Path


def main() -> int:
    server = Path(__file__).resolve().parent / "rimay_jp_mcp.py"
    p = subprocess.Popen([sys.executable, str(server)],
                         stdin=subprocess.PIPE, stdout=subprocess.PIPE,
                         stderr=subprocess.PIPE)

    def send(obj):
        p.stdin.write((json.dumps(obj) + "\n").encode("utf-8"))
        p.stdin.flush()

    def recv():
        line = p.stdout.readline().decode("utf-8")
        if not line:
            err = p.stderr.read().decode("utf-8", errors="replace")
            raise RuntimeError(f"サーバー応答なし。stderr:\n{err[:2000]}")
        return json.loads(line)

    try:
        send({"jsonrpc": "2.0", "id": 1, "method": "initialize",
              "params": {"protocolVersion": "2024-11-05", "capabilities": {},
                         "clientInfo": {"name": "smoke", "version": "0"}}})
        info = recv()["result"]["serverInfo"]
        print(f"[OK] initialize: server={info['name']}")
        send({"jsonrpc": "2.0", "method": "notifications/initialized"})
        send({"jsonrpc": "2.0", "id": 2, "method": "tools/list", "params": {}})
        tools = recv()["result"]["tools"]
        if len(tools) != 44:
            raise RuntimeError(f"公開ツール数が44件でない: {len(tools)}")
        print(f"[OK] tools/list: {len(tools)}ツール")
        send({"jsonrpc": "2.0", "id": 3, "method": "tools/call",
              "params": {"name": "lookup_term",
                         "arguments": {"surface": "顧客メールアドレス",
                                       "project_id": "sample"}}})
        text = recv()["result"]["content"][0]["text"]
        print(f"[OK] tools/call lookup_term: {json.loads(text)}")
        send({"jsonrpc": "2.0", "id": 4, "method": "tools/call",
              "params": {"name": "get_repository_parser_capabilities",
                         "arguments": {}}})
        capability = json.loads(recv()["result"]["content"][0]["text"])
        if capability["grammar"]["action_dispatch_branch_count"] != 50:
            raise RuntimeError("Repository Grammar Action分岐が50件でない")
        print("[OK] Repository capabilities: 178 rules / 50 actions")
        send({"jsonrpc": "2.0", "id": 5, "method": "tools/call",
              "params": {"name": "inspect_japanese_requirement_alpha",
                         "arguments": {
                             "source_text_ja": (
                                 "通知システムは請求書PDFを請求管理システムに"
                                 "送信しなければならない。"
                             )
                         }}})
        alpha = json.loads(recv()["result"]["content"][0]["text"])
        analyzed = alpha["japanese_analysis"]
        evaluated = alpha["fixed_grammar_evaluation"]
        if evaluated["parser"]["status"] != "accepted" or \
                evaluated["linking"]["status"] != "succeeded":
            raise RuntimeError("日本語alpha一括検査のparse/linkに失敗")
        print("[OK] Japanese alpha: smell + parse/link succeeded")
        send({"jsonrpc": "2.0", "id": 6, "method": "tools/call",
              "params": {"name": "build_repository_demo_observation",
                         "arguments": {
                             "session_id": "SMOKE",
                             "turn_id": "TURN-1",
                             "analysis_response": analyzed,
                             "evaluation_response": evaluated,
                         }}})
        observation = json.loads(recv()["result"]["content"][0]["text"])
        if observation["privacy"]["mode"] != "redacted" or \
                "source_text_ja" in observation:
            raise RuntimeError("observationのdefault redactionに失敗")
        print("[OK] Repository observation: redacted / non-intervening")
        print("SMOKE TEST PASS — Claude Codeへ登録可能です（事前起動は不要）")
        return 0
    except Exception as e:  # noqa: BLE001 — 検証用の網羅catch
        print(f"[NG] {e}")
        return 1
    finally:
        p.terminate()


if __name__ == "__main__":
    sys.exit(main())
