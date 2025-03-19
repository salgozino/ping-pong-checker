"""
Main module to check the performance of the Pong Bot from different candidates

With this module you can pass the bot address and the starting block to check if
the bot has pong all the pings, if there are missing pongs or duplicated pongs.
"""
import sys
import logging

from contract import Contract

PING_PONG_ADDRESS = "0xA7F42ff7433cB268dD7D59be62b00c30dEd28d3D"


def setupLogger(log_file="logs.log", level=logging.INFO) -> logging.Logger:
    """
    Sets up a logger with both file and stream handlers.

    Args:
        log_file (str): The name of the log file to write to. Defaults to "logs.log".
        level (int): The logging level. Defaults to logging.INFO.

    Returns:
        logging.Logger: Configured logger instance.
    """
    # Configure log file
    name = "pong-checker"
    _logger: logging.Logger = logging.getLogger(name)
    formatter = logging.Formatter(
        "%(asctime)s - %(name)s - %(levelname)s - %(message)s"
    )
    _logger.setLevel(level)
    file_handler = logging.FileHandler(f"logs/{log_file}", mode="a")
    file_handler.setFormatter(formatter)
    _logger.addHandler(file_handler)
    stream_handler = logging.StreamHandler()
    stream_handler.setFormatter(formatter)
    _logger.addHandler(stream_handler)
    return _logger


def getEvents(ping_pong_contract: Contract, start_block: int, address: str):
    """
    Retrieves all ping and pong events from a given ping-pong contract starting from a specific block.

    Args:
        ping_pong_contract (Contract): The contract instance to query for events.
        start_block (int): The block number from which to start retrieving events.
        address (str): The bot identifier to filter pong events.

    Returns:
        tuple: A tuple containing two lists:
            - all_pings: A list of all ping events starting from the start_block.
            - all_pongs: A list of all pong events starting from the start_block
                and filtered by bot address.
    """
    all_pings = ping_pong_contract.get_all_pings(start_block)
    # logger.info(f"Ping example: {all_pings[0]}")
    all_pongs = ping_pong_contract.get_all_pongs(
        start_block, address
    )
    return all_pings, all_pongs


def main(candidate_bot: str, candidate_starting_block: int, logger: logging.Logger) -> None:
    """
    Main function to review pongs for a given candidate bot starting from a specific block.

    Args:
        candidate_bot (str): The candidate bot's identifier.
        candidate_starting_block (int): The block number from which to start reviewing pongs.
        log (logging.Logger): Logger instance for logging information and errors.

    Logs:
        - Information about the start of the review process.
        - Number of pings and pongs found.
        - Errors if there are mismatches in the number of pings and pongs.
        - Errors if there are duplicate pongs.
        - Errors if there are pongs without corresponding pings.
        - Errors if there are missing pings.
        - Information if all pongs have valid corresponding pings and if there are no duplicate pongs.
    """
    logger.info(
        f"Starting to review pongs for candidate: {candidate_bot} since block: {candidate_starting_block}"
    )
    ping_pong_contract = Contract(
        PING_PONG_ADDRESS, "PingPongABI.json", logger)

    all_pings, all_pongs = getEvents(
        ping_pong_contract, candidate_starting_block, candidate_bot
    )
    logger.info(f"Pings: {len(all_pings)} | Pongs: {len(all_pongs)}")

    # Let's check the ping arg in pong events agains the ping txs.
    pings_hash_in_pongs = [pong["args"]["txHash"] for pong in all_pongs]
    ping_txs = [ping["transactionHash"] for ping in all_pings]

    # Same amount of pongs than pings?
    if len(all_pongs) != len(all_pings):
        logger.error(
            "There is no 1 pong event per ping. Don't know yet if there are duplicates or missing."
        )

    # Duplicated pongs check.
    if len(set(pings_hash_in_pongs)) != len(pings_hash_in_pongs):
        logger.error(
            (
                f"There are duplicated pingHash in pongs. There are {len(pings_hash_in_pongs)} pong events,"
                f" but the unique array of ping txs in the pong events are {len(set(pings_hash_in_pongs))}"
            )
        )
    else:
        logger.info("There are not duplicated pingHash in pongs")

    # Check if all the pong tx args match with the ping txs.
    pings_hash_in_pongs = set(
        pings_hash_in_pongs
    )  # If there are duplicate pongs, remove them :)
    count_of_invalid_pongs = 0
    for ping_hash in set(pings_hash_in_pongs):
        if not ping_hash in ping_txs:
            logger.error(
                f"Pong for 0x{ping_hash.hex()} not included in the pings txs")
            count_of_invalid_pongs += 1
    if count_of_invalid_pongs == 0:
        logger.info("All pongs events has a valid ping tx")

    # Missing pings
    if len(pings_hash_in_pongs) < len(ping_txs):
        logger.error(
            f"There are {(1 - len(pings_hash_in_pongs) / len(ping_txs)) * 100:.2f}% missing ping txs"
        )
        missing_pings = [
            ping for ping in ping_txs if ping not in pings_hash_in_pongs]
        logger.error(f"Missing pings: {missing_pings}")


if __name__ == "__main__":
    if len(sys.argv) != 3:
        print("Usage: python3 main.py <candidate_bot> <candidate_starting_block>")
        sys.exit(1)

    candidate_bot_address: str = sys.argv[1]
    starting_block = int(sys.argv[2])
    _logger: logging.Logger = setupLogger(log_file=candidate_bot_address)
    main(candidate_bot=candidate_bot_address,
         candidate_starting_block=starting_block,
         logger=_logger
         )
