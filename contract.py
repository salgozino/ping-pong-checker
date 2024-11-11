import os
import json

from dotenv import load_dotenv
from web3 import Web3


load_dotenv()


class Contract:
    # TODO: choose the proper RPC from the chainID
    rpc = os.getenv("RPC_HTTP_PROVIDER", None)
    if rpc is None:
        raise ValueError("RPC_HTTP_PROVIDER not set")
    web3 = Web3(Web3.HTTPProvider(rpc))

    def __init__(self, address, abi_path, logger):
        self.logger = logger
        # Just in case to prevent error.
        self.address = Web3.to_checksum_address(address.lower())
        self.abi_path = abi_path
        self.get_contract_from_abi()

    def get_abi(self):
        # TODO: Check if ABI is available.
        with open(self.abi_path, "r") as abi_file:
            abi_data = json.load(abi_file)
            contract_abi = abi_data["abi"]
        return contract_abi

    def get_contract_from_abi(self):
        # Load the ABI from the JSON file
        abi = self.get_abi()
        # Instantiate the smart contract
        self.contract = self.web3.eth.contract(
            address=self.address, abi=abi, decode_tuples=True
        )
        # TODO: raise error if contract was not possible to instantiate
        self.logger.info(f"Contract wit address {self.contract.address} attached")
        return self.contract

    def get_transaction(self, tx_hash: str):
        return self.web3.eth.get_transaction(tx_hash)

    def get_blocknumber_from_tx_hash(self, tx_hash: str):
        tx = self.get_transaction(tx_hash)
        if tx is not None:
            return tx["blockNumber"]
        return None

    def get_all_pings(self, start_block):
        """Obtiene todos los eventos Ping de un contrato desde un bloque determinado"""
        self.logger.info(f"Get all pings since block {start_block}")
        filter_ping = self.contract.events.Ping.create_filter(fromBlock=start_block)
        return filter_ping.get_all_entries()

    def get_all_pongs(self, start_block, address):
        """
        Obtiene todos los eventos Pong de un contrato desde un bloque determinado.
        Solo se obtienen los eventos generados por la address indicada
        """
        self.logger.info(f"Get all pongs from {address} since block {start_block}")
        pongs_filter = self.contract.events.Pong.create_filter(fromBlock=start_block)
        pongs_events = pongs_filter.get_all_entries()
        pongs = []
        for pong_event in pongs_events:
            tx_hash = pong_event.transactionHash.hex()
            tx = self.web3.eth.get_transaction(tx_hash)
            if tx["from"].lower() == address.lower():
                pongs.append(pong_event)
        return pongs
