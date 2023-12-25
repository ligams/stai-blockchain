from __future__ import annotations

from stai.types.blockchain_format.program import Program
from stai.types.blockchain_format.sized_bytes import bytes32
from stai.util.ints import uint64
from stai.wallet.puzzles.load_clvm import load_clvm_maybe_recompile

NOTIFICATION_MOD = load_clvm_maybe_recompile("notification.clsp")


def construct_notification(target: bytes32, amount: uint64) -> Program:
    return NOTIFICATION_MOD.curry(target, amount)
