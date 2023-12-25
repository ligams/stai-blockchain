from __future__ import annotations

from typing import Generator, Iterable, KeysView

SERVICES_FOR_GROUP = {
    "all": [
        "stai_harvester",
        "stai_timelord_launcher",
        "stai_timelord",
        "stai_farmer",
        "stai_full_node",
        "stai_wallet",
        "stai_data_layer",
        "stai_data_layer_http",
    ],
    # TODO: should this be `data_layer`?
    "data": ["stai_wallet", "stai_data_layer"],
    "data_layer_http": ["stai_data_layer_http"],
    "node": ["stai_full_node"],
    "harvester": ["stai_harvester"],
    "farmer": ["stai_harvester", "stai_farmer", "stai_full_node", "stai_wallet"],
    "farmer-no-wallet": ["stai_harvester", "stai_farmer", "stai_full_node"],
    "farmer-only": ["stai_farmer"],
    "timelord": ["stai_timelord_launcher", "stai_timelord", "stai_full_node"],
    "timelord-only": ["stai_timelord"],
    "timelord-launcher-only": ["stai_timelord_launcher"],
    "wallet": ["stai_wallet"],
    "introducer": ["stai_introducer"],
    "simulator": ["stai_full_node_simulator"],
    "crawler": ["stai_crawler"],
    "seeder": ["stai_crawler", "stai_seeder"],
    "seeder-only": ["stai_seeder"],
}


def all_groups() -> KeysView[str]:
    return SERVICES_FOR_GROUP.keys()


def services_for_groups(groups: Iterable[str]) -> Generator[str, None, None]:
    for group in groups:
        yield from SERVICES_FOR_GROUP[group]


def validate_service(service: str) -> bool:
    return any(service in _ for _ in SERVICES_FOR_GROUP.values())
