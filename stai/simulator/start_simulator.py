from __future__ import annotations

import logging
import sys
from dataclasses import dataclass
from multiprocessing import freeze_support
from pathlib import Path
from typing import Any, Dict, List, Optional, Tuple

from stai.full_node.full_node import FullNode
from stai.server.outbound_message import NodeType
from stai.server.start_service import Service, async_run
from stai.simulator.block_tools import BlockTools, test_constants
from stai.simulator.full_node_simulator import FullNodeSimulator
from stai.simulator.simulator_full_node_rpc_api import SimulatorFullNodeRpcApi
from stai.types.aliases import SimulatorFullNodeService
from stai.types.blockchain_format.sized_bytes import bytes32
from stai.util.bech32m import decode_puzzle_hash
from stai.util.stai_logging import initialize_logging
from stai.util.config import load_config, load_config_cli, override_config
from stai.util.default_root import DEFAULT_ROOT_PATH
from stai.util.ints import uint16
from stai.util.misc import SignalHandlers

# See: https://bugs.python.org/issue29288
"".encode("idna")

SERVICE_NAME = "full_node"
log = logging.getLogger(__name__)
PLOTS = 3  # 3 plots should be enough
PLOT_SIZE = 19  # anything under k19 is a bit buggy


async def create_full_node_simulator_service(
    root_path: Path,
    config: Dict[str, Any],
    bt: BlockTools,
    connect_to_daemon: bool = True,
    override_capabilities: Optional[List[Tuple[uint16, str]]] = None,
) -> SimulatorFullNodeService:
    service_config = config[SERVICE_NAME]
    constants = bt.constants

    node = await FullNode.create(
        config=service_config,
        root_path=root_path,
        consensus_constants=constants,
    )

    peer_api = FullNodeSimulator(node, bt, config)
    network_id = service_config["selected_network"]
    return Service(
        root_path=root_path,
        config=config,
        node=node,
        peer_api=peer_api,
        node_type=NodeType.FULL_NODE,
        advertised_port=service_config["port"],
        service_name=SERVICE_NAME,
        on_connect_callback=node.on_connect,
        network_id=network_id,
        rpc_info=(SimulatorFullNodeRpcApi, service_config["rpc_port"]),
        connect_to_daemon=connect_to_daemon,
        override_capabilities=override_capabilities,
    )


@dataclass
class StartedSimulator:
    service: SimulatorFullNodeService
    exit_code: int


async def async_main(
    test_mode: bool = False,
    automated_testing: bool = False,
    root_path: Path = DEFAULT_ROOT_PATH,
) -> StartedSimulator:
    # Same as full node, but the root_path is defined above
    config = load_config(root_path, "config.yaml")
    service_config = load_config_cli(root_path, "config.yaml", SERVICE_NAME)
    config[SERVICE_NAME] = service_config
    # THIS IS Simulator specific.
    fingerprint: Optional[int] = None
    farming_puzzle_hash: Optional[bytes32] = None
    plot_dir: str = "simulator/plots"
    if "simulator" in config:
        overrides = {}
        plot_dir = config["simulator"].get("plot_directory", "simulator/plots")
        if config["simulator"]["key_fingerprint"] is not None:
            fingerprint = int(config["simulator"]["key_fingerprint"])
        if config["simulator"]["farming_address"] is not None:
            farming_puzzle_hash = decode_puzzle_hash(config["simulator"]["farming_address"])
    else:  # old config format
        overrides = {
            "full_node.selected_network": "testnet0",
            "full_node.database_path": service_config["simulator_database_path"],
            "full_node.peers_file_path": service_config["simulator_peers_file_path"],
            "full_node.introducer_peer": {"host": "127.0.0.1", "port": 58555},
        }
    overrides["simulator.use_current_time"] = True

    # create block tools
    bt = BlockTools(
        test_constants,
        root_path,
        config_overrides=overrides,
        automated_testing=automated_testing,
        plot_dir=plot_dir,
    )
    await bt.setup_keys(fingerprint=fingerprint, reward_ph=farming_puzzle_hash)
    await bt.setup_plots(num_og_plots=PLOTS, num_pool_plots=0, num_non_keychain_plots=0, plot_size=PLOT_SIZE)
    # Everything after this is not simulator specific, excluding the if test_mode.
    initialize_logging(
        service_name=SERVICE_NAME,
        logging_config=service_config["logging"],
        root_path=root_path,
    )
    service = await create_full_node_simulator_service(root_path, override_config(config, overrides), bt)
    if not test_mode:
        async with SignalHandlers.manage() as signal_handlers:
            await service.setup_process_global_state(signal_handlers=signal_handlers)
            await service.run()

    return StartedSimulator(service=service, exit_code=0)


def main() -> int:
    freeze_support()
    return async_run(async_main()).exit_code


if __name__ == "__main__":
    sys.exit(main())
