"""ULID（26 桁・時刻順にソートできる識別子）の生成。

先頭 10 桁が 48bit のミリ秒時刻、残り 16 桁が 80bit の乱数で、
Crockford の base32（`I` `L` `O` `U` を除く 32 文字）で表す。
辞書順に並べれば発行順になるため、ログを ID で並べ替えるだけで時系列になる。
"""

import os
import time

ALPHABET = "0123456789ABCDEFGHJKMNPQRSTVWXYZ"
LENGTH = 26


def new(milliseconds=None):
    if milliseconds is None:
        milliseconds = int(time.time() * 1000)
    value = (milliseconds << 80) | int.from_bytes(os.urandom(10), "big")
    out = []
    for _ in range(LENGTH):
        value, remainder = divmod(value, 32)
        out.append(ALPHABET[remainder])
    return "".join(reversed(out))


def short(identifier, width=8):
    """人が読む画面用の短縮表示。**末尾**を取る。

    先頭 10 桁は時刻部のため、同じミリ秒に発行した ID は先頭が一致して衝突する。
    保存と突合には全 26 桁を使う。
    """
    return identifier[-width:] if identifier else ""
