"""SudachiPy adapter（改善計画 v0.3 P1-2。D6: 解析資産をProvenanceへ記録する）。

- 版数文字列だけでなく、実際にロードした辞書・設定の実体hashを記録する。
- Sudachi固有オブジェクトは本モジュール外へ出さない（LexicalTokenへ写像）。
- 検証済みbaseline: SudachiPy==0.6.11 / SudachiDict-core==20260723
  （評価期間中は変更しない。§8 P1）。
"""
from __future__ import annotations

import hashlib
from functools import lru_cache
from pathlib import Path

from .japanese_lexical_analysis import LexicalToken

_SPLIT_MODES = ("A", "B", "C")
_DICT_PACKAGES = {"small": "sudachidict_small", "core": "sudachidict_core",
                  "full": "sudachidict_full"}


@lru_cache(maxsize=4)
def _file_hash(path: str) -> str:
    h = hashlib.sha256()
    with open(path, "rb") as f:
        for chunk in iter(lambda: f.read(1 << 20), b""):
            h.update(chunk)
    return "sha256:" + h.hexdigest()


@lru_cache(maxsize=4)
def _dictionary(edition: str):
    from sudachipy import Dictionary
    return Dictionary(dict=edition).create()


def _package_version(package: str) -> str:
    from importlib.metadata import version
    return version(package)


class SudachiProvider:
    provider_id = "sudachipy"

    def __init__(self, dictionary: str = "core", split_mode: str = "C"):
        if dictionary not in _DICT_PACKAGES:
            raise ValueError(f"unknown sudachi dictionary edition: {dictionary}")
        if split_mode not in _SPLIT_MODES:
            raise ValueError(f"unknown split mode: {split_mode}")
        self.dictionary_edition = dictionary
        self.split_mode = split_mode
        self._tok = _dictionary(dictionary)

    def _mode(self, name: str):
        from sudachipy import SplitMode
        return {"A": SplitMode.A, "B": SplitMode.B, "C": SplitMode.C}[name]

    def analyze(self, text: str, mode: str | None = None) -> list:
        """text全体をtoken列へ（mode省略時はphrase用split_mode）。

        offsetは常に原文基準（Sudachiのbegin/endをそのまま使わず、
        surface長の累積で復元して原文sliceと照合可能にする）。
        """
        m = self._mode(mode or self.split_mode)
        out, off = [], 0
        for t in self._tok.tokenize(text, m):
            s = t.surface()
            start = text.find(s, off) if text[off:off + len(s)] != s else off
            end = start + len(s)
            out.append(LexicalToken(
                s, start, end, tuple(t.part_of_speech()),
                t.dictionary_form(), t.normalized_form(),
                t.reading_form(), bool(t.is_oov())))
            off = end
        return out

    def metadata(self) -> dict:
        import sudachipy
        pkg = _DICT_PACKAGES[self.dictionary_edition]
        dic_path = self._system_dic_path(pkg)
        return {
            "provider": "sudachipy",
            "provider_version": sudachipy.__version__,
            "dictionary_package": pkg,
            "dictionary_edition": self.dictionary_edition,
            "dictionary_version": _package_version(pkg),
            "dictionary_content_hash": _file_hash(str(dic_path)),
            "config_content_hash": self._config_hash(),
            "split_mode": self.split_mode,
        }

    @staticmethod
    def _system_dic_path(pkg: str) -> Path:
        import importlib
        mod = importlib.import_module(pkg)
        return Path(mod.__file__).parent / "resources" / "system.dic"

    @staticmethod
    @lru_cache(maxsize=1)
    def _config_hash() -> str:
        """実際にロードされる既定設定資産のmanifest hash（D6）。

        sudachi.jsonだけでなく、設定から参照されOOV・分割へ影響する
        char.def / unk.def / rewrite.def も対象に含める（レビュー指摘P2）。
        """
        import json
        import sudachipy
        res = Path(sudachipy.__file__).parent / "resources"
        manifest = [(name, _file_hash(str(res / name)))
                    for name in ("sudachi.json", "char.def", "unk.def",
                                 "rewrite.def")
                    if (res / name).exists()]
        if not manifest:
            return "sha256:" + hashlib.sha256(b"sudachipy-default").hexdigest()
        blob = json.dumps(manifest, sort_keys=True).encode("utf-8")
        return "sha256:" + hashlib.sha256(blob).hexdigest()
