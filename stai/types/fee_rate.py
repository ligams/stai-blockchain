from __future__ import annotations

import math
from dataclasses import dataclass

import typing_extensions

from stai.types.clvm_cost import CLVMCost
from stai.types.mojos import Mojos
from stai.util.ints import uint64
from stai.util.streamable import Streamable, streamable


@typing_extensions.final
@streamable
@dataclass(frozen=True)
class FeeRate(Streamable):
    """
    Represents Fee Rate in mojos divided by CLVM Cost.
    Performs STAI/mojo conversion.
    Similar to 'Fee per cost'.
    """

    mojos_per_clvm_cost: uint64

    @classmethod
    def create(cls, mojos: Mojos, clvm_cost: CLVMCost) -> FeeRate:
        return cls(uint64(math.ceil(mojos / clvm_cost)))


@dataclass(frozen=True)
class FeeRateV2:
    """
    Represents Fee Rate in mojos divided by CLVM Cost.
    Similar to 'Fee per cost'.
    """

    mojos_per_clvm_cost: float