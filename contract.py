"""
Contract class to interact with the PingPong contract
For example the contract deployed in sepolia at address 0xA7F42ff7433cB268dD7D59be62b00c30dEd28d3D
"""
import logging
import os
import json
from typing import List

from dotenv import load_dotenv
from eth_typing import Address, BlockNumber
from web3 import Web3
from web3.contract.contract import Contract
from web3.types import TxData, EventData, ABI


load_dotenv()


class Contract:
    """
    A class to interact with a smart contract on the Ethereum blockchain using Web3.py.

    Attributes:
        rpc (str): The RPC HTTP provider URL.
        web3 (Web3): An instance of Web3 connected to the specified RPC provider.
        address (str): The Ethereum address of the smart contract.
        abi_path (str): The file path to the ABI JSON file of the smart contract.
        contract (Contract): An instance of the smart contract.

    Methods:
        __init__(address, abi_path, logger):
            Initializes the Contract instance with the given address, ABI path, and logger.

        get_abi():
            Reads and returns the ABI from the specified ABI JSON file.

        get_contract_from_abi():
            Loads the ABI and instantiates the smart contract.

        get_transaction(tx_hash: str):
            Retrieves and returns the transaction details for the given transaction hash.

        get_blocknumber_from_tx_hash(tx_hash: str):
            Retrieves and returns the block number for the given transaction hash.

        get_all_pings(start_block):
            Retrieves and returns all 'Ping' events from the contract since the specified start block.

        get_all_pongs(start_block, address):
            Retrieves and returns all 'Pong' events from the contract since the specified start block,
            filtered by the given address.
    """
    # TODO: choose the proper RPC from the chainID
    rpc: str | None = os.getenv("RPC_HTTP_PROVIDER", None)
    if rpc is None:
        raise ValueError("RPC_HTTP_PROVIDER not set")
    web3 = Web3(Web3.HTTPProvider(rpc))

    def __init__(self, address: Address, abi_path: str, logger: logging.Logger) -> None:
        """
        Initialize a new Contract instance.

        Args:
            address (ADdress): The Ethereum address of the smart contract.
            abi_path (str): The file path to the contract's ABI JSON file.
            logger (Logger): Logger instance to record contract interactions.
        """
        self.logger: logging.Logger = logger
        # Just in case to prevent error.
        self.address: ChecksumAddress = Web3.to_checksum_address(
            address.lower())
        self.abi_path = abi_path
        self.get_contract_from_abi()

    def get_abi(self) -> ABI:
        """
        Reads the ABI (Application Binary Interface) from the specified file path and returns it.

        Returns:
            list: The ABI of the contract as a list of dictionaries.f-8") as abi_file:

        Raises:
            FileNotFoundError: If the ABI file does not exist.
            json.JSONDecodeError: If the ABI file is not a valid JSON.
            KeyError: If the ABI key is not found in the JSON data.
        """
        with open(self.abi_path, "r") as abi_file:
            abi_data = json.load(abi_file)
            contract_abi = abi_data["abi"]
        return contract_abi

    def get_contract_from_abi(self) -> Contract:
        """
        Load the contract ABI and instantiate the smart contract.

        Returns:
            Contract: The instantiated Web3 contract object.

        Raises:
            FileNotFoundError: If the ABI file cannot be loaded.
        """
        # Load the ABI from the JSON file
        abi = self.get_abi()
        # Instantiate the smart contract
        self.contract: Contract = self.web3.eth.contract(
            address=self.address, abi=abi, decode_tuples=True
        )
        # TODO: raise error if contract was not possible to instantiate
        self.logger.info(
            f"Contract wit address {self.contract.address} attached")
        return self.contract

    def get_transaction(self, tx_hash: str) -> TxData:
        """
        Retrieve transaction details for a given transaction hash.

        Args:
            tx_hash (str): The hash of the transaction to retrieve.

        Returns:
            dict: Transaction details from the blockchain.
        """
        return self.web3.eth.get_transaction(tx_hash)

    def get_blocknumber_from_tx_hash(self, tx_hash: str) -> BlockNumber | None:
        """
        Get the block number for a given transaction hash.

        Args:
            tx_hash (str): The hash of the transaction.

        Returns:
            int: The block number containing the transaction, or None if not found.
        """
        tx: TxData = self.get_transaction(tx_hash)
        if tx is not None:
            return tx.get("blockNumber")
        return None

    def get_all_pings(self, start_block) -> List[EventData]:
        """
        Retrieve all Ping events from the contract since a specified block.

        Args:
            start_block (int): The block number to start searching from.

        Returns:
            list: All Ping events emitted by the contract since the start block.
        """
        self.logger.info(f"Get all pings since block {start_block}")
        filter_ping = self.contract.events.Ping.create_filter(
            fromBlock=start_block)
        return filter_ping.get_all_entries()

    def get_all_pongs(self, start_block, address) -> List[EventData]:
        """
        Retrieve all Pong events from the contract for a specific address since a specified block.

        Args:
            start_block (int): The block number to start searching from.
            address (str): The Ethereum address to filter events by.

        Returns:
            list: All Pong events emitted by the specified address since the start block.
        """
        self.logger.info(
            f"Get all pongs from {address} since block {start_block}")
        pongs_filter = self.contract.events.Pong.create_filter(
            fromBlock=start_block)
        pongs_events: List[EventData] = pongs_filter.get_all_entries()
        pongs: List[EventData] = []
        for pong_event in pongs_events:
            tx_hash = pong_event.transactionHash.hex()
            tx = self.web3.eth.get_transaction(tx_hash)
            if tx.get("from", "").lower() == address.lower():
                pongs.append(pong_event)
        return pongs
