from __future__ import annotations

from stai.data_layer.data_layer import DataLayer
from stai.data_layer.data_layer_api import DataLayerAPI
from stai.farmer.farmer import Farmer
from stai.farmer.farmer_api import FarmerAPI
from stai.full_node.full_node import FullNode
from stai.full_node.full_node_api import FullNodeAPI
from stai.harvester.harvester import Harvester
from stai.harvester.harvester_api import HarvesterAPI
from stai.introducer.introducer import Introducer
from stai.introducer.introducer_api import IntroducerAPI
from stai.rpc.crawler_rpc_api import CrawlerRpcApi
from stai.rpc.data_layer_rpc_api import DataLayerRpcApi
from stai.rpc.farmer_rpc_api import FarmerRpcApi
from stai.rpc.full_node_rpc_api import FullNodeRpcApi
from stai.rpc.harvester_rpc_api import HarvesterRpcApi
from stai.rpc.timelord_rpc_api import TimelordRpcApi
from stai.rpc.wallet_rpc_api import WalletRpcApi
from stai.seeder.crawler import Crawler
from stai.seeder.crawler_api import CrawlerAPI
from stai.server.start_service import Service
from stai.simulator.full_node_simulator import FullNodeSimulator
from stai.simulator.simulator_full_node_rpc_api import SimulatorFullNodeRpcApi
from stai.timelord.timelord import Timelord
from stai.timelord.timelord_api import TimelordAPI
from stai.wallet.wallet_node import WalletNode
from stai.wallet.wallet_node_api import WalletNodeAPI

CrawlerService = Service[Crawler, CrawlerAPI, CrawlerRpcApi]
DataLayerService = Service[DataLayer, DataLayerAPI, DataLayerRpcApi]
FarmerService = Service[Farmer, FarmerAPI, FarmerRpcApi]
FullNodeService = Service[FullNode, FullNodeAPI, FullNodeRpcApi]
HarvesterService = Service[Harvester, HarvesterAPI, HarvesterRpcApi]
IntroducerService = Service[Introducer, IntroducerAPI, FullNodeRpcApi]
SimulatorFullNodeService = Service[FullNode, FullNodeSimulator, SimulatorFullNodeRpcApi]
TimelordService = Service[Timelord, TimelordAPI, TimelordRpcApi]
WalletService = Service[WalletNode, WalletNodeAPI, WalletRpcApi]
