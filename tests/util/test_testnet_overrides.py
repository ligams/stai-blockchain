from __future__ import annotations
from typing import Any, Dict


def test_testnet10() -> None:
    overrides: Dict[str, Any] = {}
    assert overrides == {
        "PLOT_FILTER_128_HEIGHT": 3061804,
        "PLOT_FILTER_64_HEIGHT": 8010796,
        "PLOT_FILTER_32_HEIGHT": 13056556,
    }


def test_testnet10_existing() -> None:
    overrides: Dict[str, Any] = {
        "HARD_FORK_FIX_HEIGHT": 3426000,
        "PLOT_FILTER_128_HEIGHT": 42,
        "PLOT_FILTER_64_HEIGHT": 42,
        "PLOT_FILTER_32_HEIGHT": 42,
    }
    assert overrides == {
        "PLOT_FILTER_128_HEIGHT": 42,
        "PLOT_FILTER_64_HEIGHT": 42,
        "PLOT_FILTER_32_HEIGHT": 42,
    }


def test_mainnet() -> None:
    overrides: Dict[str, Any] = {}
    assert overrides == {}
